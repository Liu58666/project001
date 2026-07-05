import re
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/news", tags=["news"])


def _build_news_response(news: models.News, db: Session) -> schemas.NewsOut:
    """
    构建新闻响应数据，包含封面图片和内容图片
    """
    # 查询封面图片 - 确保 news_id 不为 None
    cover_image_url = None
    if news.id:
        cover_stmt = select(models.NewsImage).where(
            models.NewsImage.news_id == news.id,
            models.NewsImage.position == "cover"
        ).limit(1)
        cover_image_obj = db.scalar(cover_stmt)
        if cover_image_obj:
            cover_image_url = cover_image_obj.url

    # 查询内容图片 - 确保 news_id 不为 None
    image_items = []
    if news.id:
        content_images_stmt = select(models.NewsImage).where(
            models.NewsImage.news_id == news.id,
            models.NewsImage.position == "content"
        ).order_by(models.NewsImage.created_at.asc())
        content_images = db.scalars(content_images_stmt).all()

        # 将图片按上传顺序匹配到占位符索引
        # 第1个图片对应 [IMAGE:0]，第2个对应 [IMAGE:1]，以此类推
        for img_index, image_obj in enumerate(content_images):
            image_items.append(schemas.NewsImageItem(
                url=image_obj.url,
                position=img_index,  # 占位符索引，对应 [IMAGE:0], [IMAGE:1] 等
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
    return [_build_news_response(news, db) for news in rows]


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
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Slug already exists"
        )

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

    db.delete(news)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


