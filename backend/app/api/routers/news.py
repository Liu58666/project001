from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.storage_cleanup import enqueue_storage_cleanup, process_pending_cleanup_jobs
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/news", tags=["news"])


def _news_image_sort_key(image: models.NewsImage) -> tuple[int, int]:
    return (int(getattr(image, "display_order", 0) or 0), int(image.id or 0))


def _build_news_response(news: models.News, db: Session, images: list[models.NewsImage] | None = None) -> schemas.NewsOut:
    """
    构建新闻响应数据，包含封面图片和内容图片
    """
    if images is None:
        images = []
        if news.id:
            image_stmt = (
                select(models.NewsImage)
                .where(models.NewsImage.news_id == news.id)
                .order_by(models.NewsImage.display_order.asc(), models.NewsImage.id.asc())
            )
            images = db.scalars(image_stmt).all()

    cover_image_url = None
    cover_image_obj = next((img for img in sorted(images, key=_news_image_sort_key) if img.position == "cover"), None)
    if cover_image_obj:
        cover_image_url = cover_image_obj.url

    image_items = []
    content_images = [img for img in sorted(images, key=_news_image_sort_key) if img.position == "content"]
    for img_index, image_obj in enumerate(content_images):
        image_items.append(schemas.NewsImageItem(
            url=image_obj.url,
            position=img_index,
            caption=image_obj.caption or ""
        ))

    # 构建响应
    return schemas.NewsOut(
        id=news.id,
        slug=news.slug,
        category=news.category,
        published_at=news.published_at,
        title=news.title,
        subtitle=news.subtitle,
        author=news.author,
        content=news.content,
        cover_image=cover_image_url,
        images=image_items,
    )


@router.get("", response_model=list[schemas.NewsOut])
async def list_news(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[schemas.NewsOut]:
    """
    查询新闻列表：按 publishedAt 升序（时间最早的在最上面）
    """
    stmt = (
        select(models.News)
        .order_by(models.News.published_at.asc(), models.News.id.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()
    news_ids = [int(news.id) for news in rows]
    images_by_news: dict[int, list[models.NewsImage]] = {}
    if news_ids:
        img_stmt = (
            select(models.NewsImage)
            .where(models.NewsImage.news_id.in_(news_ids))
            .order_by(models.NewsImage.news_id.asc(), models.NewsImage.display_order.asc(), models.NewsImage.id.asc())
        )
        for image in db.scalars(img_stmt).all():
            images_by_news.setdefault(int(image.news_id), []).append(image)
    return [_build_news_response(news, db, images_by_news.get(int(news.id), [])) for news in rows]


@router.post("", response_model=schemas.NewsOut, status_code=status.HTTP_201_CREATED)
async def publish_news(
    payload: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.NewsOut:
    """
    发布新闻：仅 role==3 可发布
    """
    # allow role 3 (admin) and higher (e.g., 4)
    if int(current_user.role) < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    image_ids = list(dict.fromkeys(int(image_id) for image_id in payload.image_ids))
    selected_images: list[models.NewsImage] = []
    if image_ids:
        images_stmt = select(models.NewsImage).where(models.NewsImage.id.in_(image_ids))
        selected_images = db.scalars(images_stmt).all()
        selected_by_id = {int(image.id): image for image in selected_images}
        if len(selected_by_id) != len(image_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more images do not exist")
        selected_images = [selected_by_id[image_id] for image_id in image_ids]
        for image in selected_images:
            if int(image.uploaded_by) != int(current_user.id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Images must belong to the current publisher")
            if image.news_id is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Image is already linked to news")

    news = models.News(
        slug=payload.slug,
        category=payload.category,
        published_at=payload.published_at,
        title=payload.title,
        subtitle=payload.subtitle,
        author=payload.author,
        content=payload.content,
    )
    db.add(news)
    try:
        db.flush()
        for display_order, image in enumerate(selected_images):
            image.news_id = int(news.id)
            image.display_order = display_order
            db.add(image)
        if selected_images:
            db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Slug already exists"
        )

    return _build_news_response(news, db, selected_images)


@router.get("/by-slug/{slug}", response_model=schemas.NewsOut)
async def get_news_by_slug(
    slug: str,
    db: Session = Depends(get_db),
) -> schemas.NewsOut:
    news = db.scalar(select(models.News).where(models.News.slug == slug))
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return _build_news_response(news, db)


@router.get("/{news_id}", response_model=schemas.NewsOut)
async def get_news(
    news_id: int,
    db: Session = Depends(get_db),
) -> schemas.NewsOut:
    """
    获取单个新闻详情
    """
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    
    return _build_news_response(news, db)


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Response:
    """
    删除新闻：仅 role==3 可删除
    """
    # allow role 3 (admin) and higher (e.g., 4)
    if int(current_user.role) < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")

    image_rows = db.scalars(select(models.NewsImage).where(models.NewsImage.news_id == int(news_id))).all()
    for image in image_rows:
        enqueue_storage_cleanup(db, cos_key=image.cos_key, source_table="news_images", source_id=int(image.id))

    db.delete(news)
    db.flush()
    background_tasks.add_task(process_pending_cleanup_jobs)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


