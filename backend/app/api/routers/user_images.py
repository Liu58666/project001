"""
用户图片上传和管理接口
"""

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.core.cos_service import cos_service
from app.core.storage_cleanup import enqueue_storage_cleanup, process_pending_cleanup_jobs
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/user-images", tags=["user-images"])

VALID_IMAGE_TYPES = ["avatar", "certificate", "project", "portfolio", "bio"]

IMAGE_TYPE_MAX_SIZES: dict[str, tuple[int, int]] = {
    "avatar": (800, 800),
    "certificate": (1200, 1600),
    "project": (1600, 1200),
    "portfolio": (1920, 1080),
    "bio": (1200, 800),
}


@router.post("/upload", response_model=schemas.UserImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_user_image(
    file: bytes = File(..., description="图片文件"),
    image_type: str = Form(..., description="图片类型：avatar/certificate/project/portfolio/bio"),
    filename: str = Form(..., description="文件名"),
    caption: str = Form(default="", description="图片说明（可选）"),
    display_order: int = Form(default=0, description="展示顺序（可选）"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserImageUploadResponse:
    if image_type not in VALID_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的图片类型。支持：{', '.join(VALID_IMAGE_TYPES)}",
        )

    max_file_size = 10 * 1024 * 1024
    if len(file) > max_file_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过限制（最大 10MB）")

    max_size = IMAGE_TYPE_MAX_SIZES.get(image_type)

    try:
        upload_result = cos_service.upload_user_image(
            file_content=file,
            user_id=int(current_user.id),
            image_type=image_type,
            original_filename=filename,
            max_size=max_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败：{str(e)}")

    row = models.UserImage(
        user_id=int(current_user.id),
        image_type=image_type,
        cos_key=upload_result["key"],
        url=upload_result["url"],
        original_filename=filename,
        file_size=upload_result["size"],
        width=upload_result["width"],
        height=upload_result["height"],
        caption=caption,
        display_order=display_order,
    )
    db.add(row)
    try:
        db.flush()
    except SQLAlchemyError:
        db.rollback()
        if not cos_service.delete_image(upload_result["key"]):
            enqueue_storage_cleanup(db, cos_key=upload_result["key"], source_table="user_images")
            db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="图片保存失败")
    db.refresh(row)

    return schemas.UserImageUploadResponse(
        id=row.id,
        url=row.url,
        image_type=row.image_type,
        original_filename=row.original_filename,
        file_size=row.file_size,
        width=row.width,
        height=row.height,
        caption=row.caption or "",
        display_order=int(row.display_order),
        created_at=row.created_at,
    )


@router.get("", response_model=list[schemas.UserImageOut])
async def list_user_images(
    user_id: int | None = Query(default=None, description="用户ID（不传则默认当前用户）"),
    image_type: str | None = Query(default=None, description="按类型筛选"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user_optional),
) -> list[schemas.UserImageOut]:
    if image_type is not None and image_type not in VALID_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的图片类型。支持：{', '.join(VALID_IMAGE_TYPES)}",
        )

    # default to current user when user_id is omitted
    if user_id is None:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        user_id = int(current_user.id)

    # public access: only allow listing others when resume is public
    if current_user is None or int(current_user.id) != int(user_id):
        stmt = select(models.UserResume).where(
            models.UserResume.user_id == int(user_id),
            models.UserResume.is_public == True,  # noqa: E712
        )
        resume = db.scalar(stmt)
        if resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    stmt = select(models.UserImage).where(models.UserImage.user_id == int(user_id))
    if image_type is not None:
        stmt = stmt.where(models.UserImage.image_type == image_type)

    stmt = (
        stmt.order_by(models.UserImage.display_order.asc(), models.UserImage.created_at.desc(), models.UserImage.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()
    return [schemas.UserImageOut.model_validate(r) for r in rows]


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_image(
    image_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    image = db.get(models.UserImage, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if int(image.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此图片")

    enqueue_storage_cleanup(db, cos_key=image.cos_key, source_table="user_images", source_id=int(image.id))
    db.delete(image)
    db.flush()
    background_tasks.add_task(process_pending_cleanup_jobs)


@router.patch("/{image_id}/caption", response_model=schemas.UserImageOut)
async def update_user_image_caption(
    image_id: int,
    caption: str = Form(..., description="图片说明"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserImageOut:
    image = db.get(models.UserImage, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if int(image.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此图片")

    image.caption = caption
    db.flush()
    db.refresh(image)
    return schemas.UserImageOut.model_validate(image)


@router.patch("/{image_id}/order", response_model=schemas.UserImageOut)
async def update_user_image_order(
    image_id: int,
    display_order: int = Form(..., description="展示顺序"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserImageOut:
    image = db.get(models.UserImage, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if int(image.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此图片")

    image.display_order = display_order
    db.flush()
    db.refresh(image)
    return schemas.UserImageOut.model_validate(image)


