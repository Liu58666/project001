from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_role_3_or_4
from app.core.security import hash_password
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _assert_can_manage_target(actor: models.User, target: models.User) -> None:
    if int(actor.role) == 3 and int(target.role) > 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only manage role 0-2 users")


def _assert_can_assign_role(actor: models.User, role: int | None) -> None:
    if role is None:
        return
    if int(actor.role) == 3 and int(role) > 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only assign role 0-2")


def _assert_not_last_active_admin_change(db: Session, target: models.User, payload: schemas.AdminUserUpdate) -> None:
    if int(target.role) != 4 or not bool(target.is_active):
        return
    will_deactivate = payload.is_active is False
    will_downgrade = payload.role is not None and int(payload.role) != 4
    if not (will_deactivate or will_downgrade):
        return

    active_admin_count = db.scalar(
        select(func.count(models.User.id)).where(
            models.User.role == 4,
            models.User.is_active == True,  # noqa: E712
        )
    )
    if int(active_admin_count or 0) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the last active role 4 administrator",
        )


@router.get("/users", response_model=list[schemas.UserOut])
async def list_all_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_3_or_4),
) -> list[schemas.UserOut]:
    stmt = select(models.User).order_by(models.User.id.asc())
    if int(current_user.role) == 3:
        stmt = stmt.where(models.User.role <= 2)
    stmt = stmt.limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
    return [schemas.UserOut.model_validate(u) for u in rows]


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
async def admin_update_user(
    user_id: int,
    payload: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role_3_or_4),
) -> schemas.UserOut:
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _assert_can_manage_target(current_user, user)
    _assert_can_assign_role(current_user, payload.role)
    _assert_not_last_active_admin_change(db, user, payload)

    if payload.username is not None:
        user.username = payload.username
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.email is not None:
        user.email = payload.email
    if payload.birthday is not None:
        user.birthday = payload.birthday
    if payload.photo is not None:
        user.photo = payload.photo
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = int(payload.role)
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or phone already exists")

    # keep user_resumes.role in sync when admin changes role
    if payload.role is not None:
        stmt = select(models.UserResume).where(models.UserResume.user_id == int(user.id))
        resume = db.scalar(stmt)
        if resume is not None:
            resume.role = int(user.role)
            db.add(resume)
            db.flush()

    # keep user_resumes contact in sync when admin changes phone/email
    if payload.phone is not None or payload.email is not None:
        stmt = select(models.UserResume).where(models.UserResume.user_id == int(user.id))
        resume = db.scalar(stmt)
        if resume is not None:
            resume.phone = user.phone
            resume.email = user.email
            db.add(resume)
            db.flush()

    return schemas.UserOut.model_validate(user)


