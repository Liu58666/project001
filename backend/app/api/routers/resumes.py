from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, status
from fastapi import Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cos_service import cos_service
from app.core.storage_cleanup import enqueue_storage_cleanup, process_pending_cleanup_jobs
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

MAX_PDF_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def _validate_pdf(file_content: bytes, filename: str) -> None:
    name = (filename or "").lower()
    if not name.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 PDF 文件（.pdf）")
    if len(file_content) > MAX_PDF_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过限制（最大 20MB）")
    # Basic magic header check
    if len(file_content) < 4 or file_content[:4] != b"%PDF":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件内容不是有效的 PDF（缺少 %PDF 头）")


def _build_resume_response(resume: models.UserResume, db: Session) -> schemas.ResumeOut:
    user_id = int(resume.user_id)

    # Avatar (latest)
    avatar_stmt = (
        select(models.UserImage)
        .where(models.UserImage.user_id == user_id, models.UserImage.image_type == "avatar")
        .order_by(models.UserImage.created_at.desc(), models.UserImage.id.desc())
        .limit(1)
    )
    avatar_obj = db.scalar(avatar_stmt)
    avatar_url = avatar_obj.url if avatar_obj else None

    # Bio images -> map by upload order to [IMAGE:0], [IMAGE:1], ...
    bio_stmt = (
        select(models.UserImage)
        .where(models.UserImage.user_id == user_id, models.UserImage.image_type == "bio")
        .order_by(models.UserImage.created_at.asc(), models.UserImage.id.asc())
    )
    bio_rows = db.scalars(bio_stmt).all()
    bio_images: list[schemas.ResumeBioImageItem] = [
        schemas.ResumeBioImageItem(url=img.url, position=i, caption=img.caption or "")
        for i, img in enumerate(bio_rows)
    ]

    def _list_by_type(t: str) -> list[schemas.UserImageOut]:
        stmt = (
            select(models.UserImage)
            .where(models.UserImage.user_id == user_id, models.UserImage.image_type == t)
            .order_by(models.UserImage.display_order.asc(), models.UserImage.created_at.asc(), models.UserImage.id.asc())
        )
        rows = db.scalars(stmt).all()
        return [schemas.UserImageOut.model_validate(r) for r in rows]

    return schemas.ResumeOut(
        id=resume.id,
        user_id=user_id,
        role=int(getattr(resume, "role", 0) or 0),
        real_name=resume.real_name,
        gender=resume.gender,
        age=resume.age,
        address=resume.address,
        phone=getattr(resume, "phone", None),
        email=getattr(resume, "email", None),
        job_title=getattr(resume, "job_title", None),
        department=getattr(resume, "department", None),
        education=getattr(resume, "education", None),
        bio=resume.bio or [],
        is_public=bool(resume.is_public),
        avatar_url=avatar_url,
        bio_images=bio_images,
        certificates=_list_by_type("certificate"),
        projects=_list_by_type("project"),
        portfolios=_list_by_type("portfolio"),
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.post("", response_model=schemas.ResumeOut, status_code=status.HTTP_201_CREATED)
async def create_or_update_resume(
    payload: schemas.ResumeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ResumeOut:
    stmt = select(models.UserResume).where(models.UserResume.user_id == current_user.id)
    existing = db.scalar(stmt)

    if existing:
        # keep resume.role in sync with users.role
        existing.role = int(current_user.role)
        # keep contact in sync with users profile
        existing.phone = current_user.phone
        existing.email = current_user.email
        existing.real_name = payload.real_name
        existing.gender = payload.gender
        existing.age = payload.age
        existing.address = payload.address
        existing.job_title = payload.job_title
        existing.department = payload.department
        existing.education = payload.education
        existing.bio = payload.bio or []
        existing.is_public = payload.is_public
        db.add(existing)
        db.flush()
        return _build_resume_response(existing, db)

    resume = models.UserResume(
        user_id=current_user.id,
        role=int(current_user.role),
        phone=current_user.phone,
        email=current_user.email,
        real_name=payload.real_name,
        gender=payload.gender,
        age=payload.age,
        address=payload.address,
        job_title=payload.job_title,
        department=payload.department,
        education=payload.education,
        bio=payload.bio or [],
        is_public=payload.is_public,
    )
    db.add(resume)
    db.flush()
    db.refresh(resume)
    return _build_resume_response(resume, db)


@router.get("", response_model=list[schemas.ResumeDirectoryItemOut])
async def list_all_resumes_directory(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[schemas.ResumeDirectoryItemOut]:
    """
    查询所有用户简历目录（不区分是否公开）：
    - 始终返回：职务(job_title)、真实姓名(real_name)、部门(department)、头像(avatar)
    - 若该简历公开(is_public=True)，额外返回完整 resume 详情
    - 若不公开，则返回 private_hidden=True 且 resume=None
    """
    stmt = (
        select(models.UserResume, models.User)
        .join(models.User, models.User.id == models.UserResume.user_id)
        .order_by(models.UserResume.user_id.asc(), models.UserResume.id.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()  # list[tuple[UserResume, User]]

    items: list[schemas.ResumeDirectoryItemOut] = []
    for resume, user in rows:
        # avatar: prefer users.photo; can be empty string
        avatar = getattr(user, "photo", None) or None
        role = int(getattr(resume, "role", None) or getattr(user, "role", 0) or 0)
        email = (getattr(resume, "email", None) or getattr(user, "email", None)) if bool(resume.is_public) else None
        # phone is only shown when resume is public
        phone = (getattr(resume, "phone", None) or getattr(user, "phone", None)) if bool(resume.is_public) else None

        if bool(resume.is_public):
            resume_out = _build_resume_response(resume, db)
            items.append(
                schemas.ResumeDirectoryItemOut(
                    user_id=int(resume.user_id),
                    role=role,
                    real_name=resume.real_name,
                    job_title=getattr(resume, "job_title", None),
                    department=getattr(resume, "department", None),
                    avatar=avatar,
                    email=email,
                    phone=phone,
                    is_public=True,
                    private_hidden=False,
                    resume=resume_out,
                )
            )
        else:
            items.append(
                schemas.ResumeDirectoryItemOut(
                    user_id=int(resume.user_id),
                    role=role,
                    real_name=resume.real_name,
                    job_title=getattr(resume, "job_title", None),
                    department=getattr(resume, "department", None),
                    avatar=avatar,
                    email=None,
                    phone=None,
                    is_public=False,
                    private_hidden=True,
                    resume=None,
                )
            )

    return items


@router.get("/me", response_model=schemas.ResumeOut)
async def get_my_resume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ResumeOut:
    stmt = select(models.UserResume).where(models.UserResume.user_id == current_user.id)
    resume = db.scalar(stmt)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return _build_resume_response(resume, db)


@router.patch("/me", response_model=schemas.ResumeOut)
async def update_my_resume(
    payload: schemas.ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ResumeOut:
    stmt = select(models.UserResume).where(models.UserResume.user_id == current_user.id)
    resume = db.scalar(stmt)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if payload.real_name is not None:
        resume.real_name = payload.real_name
    if payload.gender is not None:
        resume.gender = payload.gender
    if payload.age is not None:
        resume.age = payload.age
    if payload.address is not None:
        resume.address = payload.address
    if payload.job_title is not None:
        resume.job_title = payload.job_title
    if payload.department is not None:
        resume.department = payload.department
    if payload.education is not None:
        resume.education = payload.education
    if payload.bio is not None:
        resume.bio = payload.bio
    if payload.is_public is not None:
        resume.is_public = payload.is_public

    # keep resume.role in sync with users.role
    resume.role = int(current_user.role)
    # keep contact in sync with users profile
    resume.phone = current_user.phone
    resume.email = current_user.email

    db.add(resume)
    db.flush()
    return _build_resume_response(resume, db)


@router.post("/me/pdf", response_model=schemas.ResumePdfOut, status_code=status.HTTP_201_CREATED)
async def upload_my_resume_pdf(
    file: bytes = File(..., description="PDF简历文件"),
    filename: str = Form(..., description="文件名"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ResumePdfOut:
    """
    上传/覆盖当前用户的 PDF 简历：\n
    - 上传到腾讯云 COS（users/{user_id}/resume_pdf/...）\n
    - 落库/覆盖更新 `user_resume_pdfs`（每用户仅保留最新一份）\n
    """
    _validate_pdf(file, filename)

    stmt = select(models.UserResumePDF).where(models.UserResumePDF.user_id == int(current_user.id))
    existing = db.scalar(stmt)
    old_key = existing.cos_key if existing else None

    try:
        upload_result = cos_service.upload_user_pdf(
            file_content=file,
            user_id=int(current_user.id),
            original_filename=filename,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败：{str(e)}")

    if existing:
        existing.cos_key = upload_result["key"]
        existing.url = upload_result["url"]
        existing.original_filename = filename
        existing.file_size = int(upload_result["size"])
        db.add(existing)
        try:
            db.flush()
        except SQLAlchemyError:
            db.rollback()
            if upload_result.get("key") and not cos_service.delete_image(upload_result["key"]):
                enqueue_storage_cleanup(db, cos_key=upload_result["key"], source_table="user_resume_pdfs", source_id=None)
                db.commit()
            raise
        db.refresh(existing)
        if old_key and old_key != existing.cos_key:
            enqueue_storage_cleanup(db, cos_key=old_key, source_table="user_resume_pdfs", source_id=int(existing.id))
            if background_tasks is not None:
                background_tasks.add_task(process_pending_cleanup_jobs)
        return schemas.ResumePdfOut.model_validate(existing)

    row = models.UserResumePDF(
        user_id=int(current_user.id),
        cos_key=upload_result["key"],
        url=upload_result["url"],
        original_filename=filename,
        file_size=int(upload_result["size"]),
    )
    db.add(row)
    try:
        db.flush()
    except SQLAlchemyError:
        db.rollback()
        if upload_result.get("key") and not cos_service.delete_image(upload_result["key"]):
            enqueue_storage_cleanup(db, cos_key=upload_result["key"], source_table="user_resume_pdfs", source_id=None)
            db.commit()
        raise
    db.refresh(row)
    return schemas.ResumePdfOut.model_validate(row)


@router.get("/me/pdf", response_model=schemas.ResumePdfOut)
async def get_my_resume_pdf(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ResumePdfOut:
    stmt = select(models.UserResumePDF).where(models.UserResumePDF.user_id == int(current_user.id))
    row = db.scalar(stmt)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume PDF not found")
    return schemas.ResumePdfOut.model_validate(row)


@router.get("/{user_id}", response_model=schemas.ResumeOut)
async def get_public_resume(
    user_id: int,
    db: Session = Depends(get_db),
) -> schemas.ResumeOut:
    stmt = select(models.UserResume).where(
        models.UserResume.user_id == user_id,
        models.UserResume.is_public == True,  # noqa: E712
    )
    resume = db.scalar(stmt)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return _build_resume_response(resume, db)


