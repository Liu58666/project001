from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/applications", tags=["applications"])
admin_router = APIRouter(prefix="/api/admin/applications", tags=["applications"])


def _require_role_at_least_3(current_user: models.User) -> None:
    if int(current_user.role) < 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.post("", response_model=schemas.UserApplicationOut, status_code=status.HTTP_201_CREATED)
async def submit_application_form(
    payload: schemas.UserApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserApplicationOut:
    """
    提交报名表单（每个用户只能提交一次）
    """
    stmt = select(models.UserApplicationForm).where(models.UserApplicationForm.user_id == int(current_user.id))
    existing = db.scalar(stmt)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application already submitted")

    form = models.UserApplicationForm(
        user_id=int(current_user.id),
        name=payload.name,
        grade=payload.grade,
        age=payload.age,
        major=payload.major,
        school=payload.school,
        preference=str(payload.preference.value),
        experience=payload.experience,
        message=payload.message,
        participated_before=bool(payload.participated_before),
        status=int(schemas.ApplicationStatus.pending),
    )
    db.add(form)
    db.flush()
    db.refresh(form)
    return schemas.UserApplicationOut.model_validate(form)


@admin_router.get("", response_model=list[schemas.UserApplicationAdminOut])
async def list_all_application_forms(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: int | None = Query(default=None, alias="status", description="可选：按状态过滤 0/1/2"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.UserApplicationAdminOut]:
    """
    查询所有已提交的报名表单（role >= 3）
    """
    _require_role_at_least_3(current_user)

    stmt = (
        select(models.UserApplicationForm, models.User)
        .join(models.User, models.User.id == models.UserApplicationForm.user_id)
        .order_by(models.UserApplicationForm.created_at.desc(), models.UserApplicationForm.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if status_filter is not None:
        stmt = stmt.where(models.UserApplicationForm.status == int(status_filter))

    rows = db.execute(stmt).all()  # list[tuple[UserApplicationForm, User]]

    out: list[schemas.UserApplicationAdminOut] = []
    for form, user in rows:
        base = schemas.UserApplicationOut.model_validate(form).model_dump()
        out.append(
            schemas.UserApplicationAdminOut(
                **base,
                username=str(user.username),
                phone=str(user.phone),
            )
        )
    return out


@admin_router.post("/{application_id}/accept", response_model=schemas.UserApplicationOut)
async def accept_application_form(
    application_id: int,
    payload: schemas.ApplicationAcceptRequest | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserApplicationOut:
    """
    接受报名：将该用户 role 设置为 1（role >= 3）
    """
    _require_role_at_least_3(current_user)

    form = db.get(models.UserApplicationForm, application_id)
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if int(form.status) != int(schemas.ApplicationStatus.pending):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application already reviewed")

    user = db.get(models.User, int(form.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    now = datetime.utcnow()
    form.status = int(schemas.ApplicationStatus.accepted)
    form.reviewed_by = int(current_user.id)
    form.reviewed_at = now

    # Update user role
    user.role = 1
    db.add(user)

    # keep user_resumes.role in sync if resume exists
    stmt = select(models.UserResume).where(models.UserResume.user_id == int(user.id))
    resume = db.scalar(stmt)
    if resume is not None:
        resume.role = int(user.role)
        db.add(resume)

    db.add(form)
    db.flush()
    db.refresh(form)

    # Send in-app system message to the applicant
    confirm_message = (
        (payload.message.strip() if payload and payload.message else "") or "你的申请已通过审核，请留意后续通知。"
    )
    db.add(
        models.UserMessage(
            user_id=int(user.id),
            created_by=int(current_user.id),
            title="申请通过",
            content=confirm_message,
        )
    )
    db.flush()

    return schemas.UserApplicationOut.model_validate(form)


@admin_router.post("/{application_id}/reject", response_model=schemas.UserApplicationOut)
async def reject_application_form(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserApplicationOut:
    """
    拒绝报名：清空该表单数据，但保留记录以阻止重复提交（role >= 3）
    """
    _require_role_at_least_3(current_user)

    form = db.get(models.UserApplicationForm, application_id)
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if int(form.status) != int(schemas.ApplicationStatus.pending):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application already reviewed")

    now = datetime.utcnow()
    form.status = int(schemas.ApplicationStatus.rejected)
    form.reviewed_by = int(current_user.id)
    form.reviewed_at = now

    # Clear sensitive fields (keep user_id + status to enforce one-time submission)
    form.name = None
    form.grade = None
    form.age = None
    form.major = None
    form.school = None
    form.preference = None
    form.experience = None
    form.message = None
    form.participated_before = None

    db.add(form)
    db.flush()
    db.refresh(form)
    return schemas.UserApplicationOut.model_validate(form)


