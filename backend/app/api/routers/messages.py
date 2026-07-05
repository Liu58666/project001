from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/me", response_model=list[schemas.UserMessageOut])
async def list_my_messages(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False, description="仅返回未读消息"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.UserMessageOut]:
    stmt = (
        select(models.UserMessage)
        .where(models.UserMessage.user_id == int(current_user.id))
        .where(models.UserMessage.revoked_at.is_(None))
        .order_by(models.UserMessage.created_at.desc(), models.UserMessage.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if unread_only:
        stmt = stmt.where(models.UserMessage.read_at.is_(None))
    rows = db.scalars(stmt).all()
    return [schemas.UserMessageOut.model_validate(r) for r in rows]


@router.post("/{message_id}/read", response_model=schemas.UserMessageOut)
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserMessageOut:
    msg = db.get(models.UserMessage, message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if int(msg.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if msg.read_at is None:
        msg.read_at = datetime.utcnow()
        db.add(msg)
        db.flush()
        db.refresh(msg)
    return schemas.UserMessageOut.model_validate(msg)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Response:
    msg = db.get(models.UserMessage, message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if int(msg.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db.delete(msg)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


