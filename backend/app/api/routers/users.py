from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/avatars", response_model=list[schemas.UserAvatarOut])
async def list_user_avatars(
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[schemas.UserAvatarOut]:
    """
    获取所有用户头像（公开接口，无权限限制）
    仅返回：用户 id + photo(头像URL/路径)
    """
    stmt = (
        select(models.User)
        .where(models.User.is_active == True)  # noqa: E712
        .order_by(models.User.id.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()
    return [schemas.UserAvatarOut.model_validate(u) for u in rows]


