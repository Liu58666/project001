from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/admin/messages", tags=["admin-messages"])


def _require_role_3_or_4(current_user: models.User) -> None:
    if int(current_user.role) not in (3, 4):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.post("/broadcast", response_model=schemas.AdminBroadcastMessageResponse)
async def broadcast_system_message(
    payload: schemas.AdminBroadcastMessageRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.AdminBroadcastMessageResponse:
    """
    群发系统消息（仅 role in {3,4}）
    - 可按 roles 多选筛选
    - 可指定 user_ids
    - 两者同时提供时取并集
    """
    _require_role_3_or_4(current_user)

    target_roles = list({int(r) for r in (payload.roles or [])})
    target_user_ids = list({int(uid) for uid in (payload.user_ids or [])})

    user_id_set: set[int] = set()

    if len(target_roles) > 0:
        stmt = select(models.User.id).where(
            models.User.is_active == True,  # noqa: E712
            models.User.role.in_(target_roles),
        )
        user_id_set.update([int(x) for x in db.scalars(stmt).all()])

    if len(target_user_ids) > 0:
        stmt = select(models.User.id).where(
            models.User.is_active == True,  # noqa: E712
            models.User.id.in_(target_user_ids),
        )
        user_id_set.update([int(x) for x in db.scalars(stmt).all()])

    if len(user_id_set) == 0:
        return schemas.AdminBroadcastMessageResponse(sent_count=0, recipient_count=0, batch_id=str(uuid4()))

    batch_id = str(uuid4())
    rows = [
        models.UserMessage(
            user_id=uid,
            created_by=int(current_user.id),
            batch_id=batch_id,
            title=payload.title,
            content=payload.content,
        )
        for uid in sorted(user_id_set)
    ]
    db.add_all(rows)
    db.flush()
    return schemas.AdminBroadcastMessageResponse(
        sent_count=len(rows), recipient_count=len(user_id_set), batch_id=batch_id
    )


@router.post("/broadcast/{batch_id}/revoke", response_model=schemas.AdminRevokeBroadcastResponse)
async def revoke_broadcast(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.AdminRevokeBroadcastResponse:
    """
    撤回一批群发消息（仅 role in {3,4}）
    撤回后，用户侧默认不会再查询到这些消息。
    """
    _require_role_3_or_4(current_user)

    now = datetime.utcnow()
    stmt = select(models.UserMessage).where(
        models.UserMessage.batch_id == batch_id,
        models.UserMessage.revoked_at.is_(None),
    )
    rows = db.scalars(stmt).all()

    for msg in rows:
        msg.revoked_at = now
        msg.revoked_by = int(current_user.id)
        db.add(msg)

    db.flush()
    return schemas.AdminRevokeBroadcastResponse(revoked_count=len(rows), batch_id=batch_id)


