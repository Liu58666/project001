"""
新闻图片上传和管理接口
"""
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role_at_least
from app.core.cos_service import cos_service
from app.core.storage_cleanup import enqueue_storage_cleanup, process_pending_cleanup_jobs
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/images", tags=["images"])
admin_router = APIRouter(prefix="/api/admin/images", tags=["admin-images"])

# 支持的图片位置
VALID_POSITIONS = ["cover", "content", "thumbnail", "banner", "gallery"]

# 不同位置的图片最大尺寸限制（像素）
POSITION_MAX_SIZES = {
    "cover": (1920, 1080),  # 封面图：最大 1920x1080
    "content": (1200, 800),  # 内容图：最大 1200x800
    "thumbnail": (400, 300),  # 缩略图：最大 400x300
    "banner": (1920, 600),  # 横幅：最大 1920x600
    "gallery": (1600, 1200),  # 图库：最大 1600x1200
}


@router.post("/upload", response_model=schemas.NewsImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: bytes = File(..., description="图片文件"),
    position: str = Form(..., description="图片位置：cover(封面), content(内容), thumbnail(缩略图), banner(横幅), gallery(图库)"),
    news_id: int | None = Form(default=None, description="关联的新闻ID（可选）"),
    filename: str = Form(..., description="文件名"),
    caption: str = Form(default="", description="图片说明（可选）"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> schemas.NewsImageUploadResponse:
    """
    上传新闻图片到腾讯云 COS
    
    - **position**: 图片位置，支持：cover(封面), content(内容), thumbnail(缩略图), banner(横幅), gallery(图库)
    - **news_id**: 可选，关联的新闻ID。如果提供，会验证新闻是否存在
    - **file**: 图片文件（支持 JPEG, PNG, GIF, WebP 等格式）
    - **filename**: 原始文件名
    - **caption**: 可选，图片说明
    
    图片会自动压缩到对应位置的最大尺寸限制。
    """
    # 验证位置
    if position not in VALID_POSITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的图片位置。支持的位置：{', '.join(VALID_POSITIONS)}",
        )

    # 验证文件大小（最大 10MB）
    max_file_size = 10 * 1024 * 1024  # 10MB
    if len(file) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制（最大 10MB）",
        )

    # 如果提供了 news_id，验证新闻是否存在
    if news_id is not None:
        news = db.get(models.News, news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="新闻不存在",
            )

    try:
        # 获取该位置的最大尺寸限制
        max_size = POSITION_MAX_SIZES.get(position)

        # 上传到腾讯云 COS
        upload_result = cos_service.upload_image(
            file_content=file,
            position=position,
            original_filename=filename,
            max_size=max_size,
        )

        # 保存到数据库
        news_image = models.NewsImage(
            news_id=news_id,
            position=position,
            cos_key=upload_result["key"],
            url=upload_result["url"],
            original_filename=filename,
            file_size=upload_result["size"],
            width=upload_result["width"],
            height=upload_result["height"],
            caption=caption,
            uploaded_by=current_user.id,
        )

        db.add(news_image)
        try:
            db.flush()
        except SQLAlchemyError:
            db.rollback()
            if upload_result.get("key"):
                if not cos_service.delete_image(upload_result["key"]):
                    enqueue_storage_cleanup(
                        db,
                        cos_key=upload_result["key"],
                        source_table="news_images",
                        source_id=None,
                    )
                    db.commit()
            raise
        db.refresh(news_image)

        return schemas.NewsImageUploadResponse(
            id=news_image.id,
            url=news_image.url,
            position=news_image.position,
            news_id=news_image.news_id,
            original_filename=news_image.original_filename,
            file_size=news_image.file_size,
            width=news_image.width,
            height=news_image.height,
            created_at=news_image.created_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}",
        )


@router.get("", response_model=list[schemas.NewsImagePublicOut])
async def list_images(
    position: str | None = Query(default=None, description="按位置筛选"),
    news_id: int | None = Query(default=None, description="按新闻ID筛选"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[schemas.NewsImagePublicOut]:
    """
    查询图片列表
    
    - **position**: 可选，按位置筛选
    - **news_id**: 可选，按新闻ID筛选
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    stmt = select(models.NewsImage).where(models.NewsImage.news_id.is_not(None))

    # 应用筛选条件
    if position:
        if position not in VALID_POSITIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的图片位置。支持的位置：{', '.join(VALID_POSITIONS)}",
            )
        stmt = stmt.where(models.NewsImage.position == position)

    if news_id is not None:
        stmt = stmt.where(models.NewsImage.news_id == news_id)

    # 按创建时间倒序排列
    stmt = stmt.order_by(models.NewsImage.created_at.desc()).limit(limit).offset(offset)

    rows = db.scalars(stmt).all()
    return [schemas.NewsImagePublicOut.model_validate(img) for img in rows]


@router.get("/{image_id}", response_model=schemas.NewsImagePublicOut)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> schemas.NewsImagePublicOut:
    """
    获取单个图片信息
    """
    image = db.get(models.NewsImage, image_id)
    if not image or image.news_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在",
        )
    return schemas.NewsImagePublicOut.model_validate(image)


@admin_router.get("", response_model=list[schemas.NewsImageOut])
async def admin_list_images(
    position: str | None = Query(default=None, description="按位置筛选"),
    news_id: int | None = Query(default=None, description="按新闻ID筛选"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> list[schemas.NewsImageOut]:
    stmt = select(models.NewsImage)
    if position:
        if position not in VALID_POSITIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的图片位置。支持的位置：{', '.join(VALID_POSITIONS)}",
            )
        stmt = stmt.where(models.NewsImage.position == position)
    if news_id is not None:
        stmt = stmt.where(models.NewsImage.news_id == news_id)
    stmt = stmt.order_by(models.NewsImage.created_at.desc()).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [schemas.NewsImageOut.model_validate(img) for img in rows]


@admin_router.get("/{image_id}", response_model=schemas.NewsImageOut)
async def admin_get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> schemas.NewsImageOut:
    image = db.get(models.NewsImage, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    return schemas.NewsImageOut.model_validate(image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> None:
    """
    删除图片
    
    仅允许以下用户删除：
    - 上传者本人
    - role >= 3 的管理员
    """
    image = db.get(models.NewsImage, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在",
        )

    try:
        enqueue_storage_cleanup(db, cos_key=image.cos_key, source_table="news_images", source_id=int(image.id))
        db.delete(image)
        db.flush()
        background_tasks.add_task(process_pending_cleanup_jobs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败：{str(e)}",
        )


@router.put("/{image_id}/link-news", response_model=schemas.NewsImageOut)
async def link_image_to_news(
    image_id: int,
    news_id: int = Form(..., description="要关联的新闻ID"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> schemas.NewsImageOut:
    """
    将图片关联到新闻
    
    仅允许以下用户操作：
    - 上传者本人
    - role >= 3 的管理员
    """
    image = db.get(models.NewsImage, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在",
        )

    # 验证新闻是否存在
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在",
        )

    # 更新关联
    image.news_id = news_id
    db.flush()
    db.refresh(image)

    return schemas.NewsImageOut.model_validate(image)



@router.patch("/{image_id}/caption", response_model=schemas.NewsImageOut)
async def update_image_caption(
    image_id: int,
    caption: str = Form(..., description="图片说明"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_at_least(3)),
) -> schemas.NewsImageOut:
    """
    更新图片说明
    
    仅允许以下用户操作：
    - 上传者本人
    - role >= 3 的管理员
    """
    image = db.get(models.NewsImage, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在",
        )

    image.caption = caption
    db.flush()
    db.refresh(image)

    return schemas.NewsImageOut.model_validate(image)
