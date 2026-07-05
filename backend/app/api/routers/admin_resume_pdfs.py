from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/admin/resume-pdfs", tags=["admin-resume-pdfs"])


def _require_role_at_least_3(current_user: models.User) -> None:
    if int(current_user.role) < 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("", response_model=list[schemas.AdminResumePdfOut])
async def list_all_resume_pdfs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: int | None = Query(default=None, description="按用户ID筛选（可选）"),
    username: str | None = Query(default=None, description="按用户名模糊匹配筛选（可选）"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.AdminResumePdfOut]:
    """
    管理员查询所有用户上传的 PDF 简历（仅 role>=3）。
    """
    _require_role_at_least_3(current_user)

    stmt = (
        select(models.UserResumePDF, models.User)
        .join(models.User, models.User.id == models.UserResumePDF.user_id)
    )

    if user_id is not None:
        stmt = stmt.where(models.UserResumePDF.user_id == int(user_id))
    if username:
        stmt = stmt.where(models.User.username.like(f"%{username}%"))

    stmt = (
        stmt.order_by(models.UserResumePDF.updated_at.desc(), models.UserResumePDF.user_id.asc())
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(stmt).all()  # list[tuple[UserResumePDF, User]]
    return [
        schemas.AdminResumePdfOut(
            id=int(pdf.id),
            user_id=int(pdf.user_id),
            cos_key=pdf.cos_key,
            url=pdf.url,
            original_filename=pdf.original_filename,
            file_size=int(pdf.file_size),
            created_at=pdf.created_at,
            updated_at=pdf.updated_at,
            username=user.username,
            phone=user.phone,
            role=int(user.role),
        )
        for pdf, user in rows
    ]


