from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Response, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cos_service import cos_service
from app.core.storage_cleanup import enqueue_storage_cleanup, process_pending_cleanup_jobs
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
admin_router = APIRouter(prefix="/api/admin/tasks", tags=["tasks"])


def _require_role_at_least_3(current_user: models.User) -> None:
    if int(current_user.role) < 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _require_role_3_or_4(current_user: models.User) -> None:
    if int(current_user.role) not in (3, 4):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _require_task_recipient(db: Session, *, task_id: int, user_id: int) -> None:
    stmt = select(models.TaskRecipient.id).where(
        models.TaskRecipient.task_id == int(task_id),
        models.TaskRecipient.user_id == int(user_id),
    )
    if db.scalar(stmt) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a task recipient")


@admin_router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
async def admin_create_task(
    payload: schemas.AdminTaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TaskOut:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No recipients found")

    now = datetime.utcnow()
    task = models.Task(
        title=payload.title,
        content=payload.content,
        created_by=int(current_user.id),
        published_at=now,
    )
    db.add(task)
    db.flush()
    db.refresh(task)

    rows = [
        models.TaskRecipient(task_id=int(task.id), user_id=uid)
        for uid in sorted(user_id_set)
    ]
    db.add_all(rows)
    db.flush()

    out = schemas.TaskOut.model_validate(task)
    return out.model_copy(update={"recipient_count": len(user_id_set)})


@admin_router.get("", response_model=list[schemas.TaskOut])
async def admin_list_tasks(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.TaskOut]:
    _require_role_at_least_3(current_user)

    recipient_counts = (
        select(
            models.TaskRecipient.task_id.label("task_id"),
            func.count(models.TaskRecipient.id).label("recipient_count"),
        )
        .group_by(models.TaskRecipient.task_id)
        .subquery()
    )

    stmt = (
        select(models.Task, recipient_counts.c.recipient_count)
        .outerjoin(recipient_counts, recipient_counts.c.task_id == models.Task.id)
        .order_by(models.Task.created_at.desc(), models.Task.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()  # list[tuple[Task, Optional[int]]]

    out: list[schemas.TaskOut] = []
    for task, rc in rows:
        item = schemas.TaskOut.model_validate(task)
        out.append(item.model_copy(update={"recipient_count": int(rc or 0)}))
    return out


@admin_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Response:
    """
    删除任务（发布过的任务可一键删除）

    - 权限：role >= 3
    - 行为：best-effort 删除该任务所有提交图片的 COS 对象，然后删除任务本身（依赖 DB 外键 CASCADE 清理子表）
    """
    _require_role_at_least_3(current_user)

    task = db.get(models.Task, int(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Collect COS keys for all submission images under this task
    key_stmt = (
        select(models.TaskSubmissionImage.cos_key)
        .join(
            models.TaskSubmission,
            models.TaskSubmission.id == models.TaskSubmissionImage.submission_id,
        )
        .where(models.TaskSubmission.task_id == int(task_id))
    )
    cos_keys = [str(k) for k in db.scalars(key_stmt).all()]

    for k in cos_keys:
        enqueue_storage_cleanup(db, cos_key=k, source_table="task_submission_images")

    db.delete(task)
    db.flush()
    background_tasks.add_task(process_pending_cleanup_jobs)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.get("/{task_id}/submissions", response_model=list[schemas.TaskSubmissionAdminOut])
async def admin_list_task_submissions(
    task_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.TaskSubmissionAdminOut]:
    _require_role_at_least_3(current_user)

    task = db.get(models.Task, int(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    stmt = (
        select(models.TaskSubmission, models.User)
        .join(models.User, models.User.id == models.TaskSubmission.user_id)
        .where(models.TaskSubmission.task_id == int(task_id))
        .order_by(models.TaskSubmission.updated_at.desc(), models.TaskSubmission.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()

    submission_ids = [int(sub.id) for sub, _u in rows]
    images_map: dict[int, list[models.TaskSubmissionImage]] = {}
    if len(submission_ids) > 0:
        img_stmt = (
            select(models.TaskSubmissionImage)
            .where(models.TaskSubmissionImage.submission_id.in_(submission_ids))
            .order_by(models.TaskSubmissionImage.created_at.asc(), models.TaskSubmissionImage.id.asc())
        )
        for img in db.scalars(img_stmt).all():
            images_map.setdefault(int(img.submission_id), []).append(img)

    out: list[schemas.TaskSubmissionAdminOut] = []
    for submission, user in rows:
        base = schemas.TaskSubmissionOut.model_validate(submission).model_dump()
        base["images"] = [
            schemas.TaskSubmissionImageOut.model_validate(img) for img in images_map.get(int(submission.id), [])
        ]
        out.append(
            schemas.TaskSubmissionAdminOut(
                **base,
                username=str(user.username),
                phone=str(user.phone),
            )
        )
    return out


@admin_router.post(
    "/{task_id}/submissions/{submission_id}/score",
    response_model=schemas.TaskSubmissionOut,
)
async def admin_score_submission(
    task_id: int,
    submission_id: int,
    payload: schemas.TaskScoreRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TaskSubmissionOut:
    _require_role_at_least_3(current_user)

    submission = db.get(models.TaskSubmission, int(submission_id))
    if not submission or int(submission.task_id) != int(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    submission.score = int(payload.score)
    submission.scored_by = int(current_user.id)
    submission.scored_at = datetime.utcnow()
    db.add(submission)
    db.flush()
    db.refresh(submission)

    img_stmt = (
        select(models.TaskSubmissionImage)
        .where(models.TaskSubmissionImage.submission_id == int(submission.id))
        .order_by(models.TaskSubmissionImage.created_at.asc(), models.TaskSubmissionImage.id.asc())
    )
    images = [schemas.TaskSubmissionImageOut.model_validate(img) for img in db.scalars(img_stmt).all()]
    out = schemas.TaskSubmissionOut.model_validate(submission)
    return out.model_copy(update={"images": images})


@router.get("/me", response_model=list[schemas.TaskAssignedOut])
async def list_my_tasks(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.TaskAssignedOut]:
    stmt = (
        select(models.Task, models.TaskSubmission)
        .join(models.TaskRecipient, models.TaskRecipient.task_id == models.Task.id)
        .outerjoin(
            models.TaskSubmission,
            and_(
                models.TaskSubmission.task_id == models.Task.id,
                models.TaskSubmission.user_id == int(current_user.id),
            ),
        )
        .where(models.TaskRecipient.user_id == int(current_user.id))
        .order_by(models.Task.published_at.desc(), models.Task.created_at.desc(), models.Task.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()  # list[tuple[Task, Optional[TaskSubmission]]]

    submission_ids = [int(sub.id) for _t, sub in rows if sub is not None]
    images_map: dict[int, list[models.TaskSubmissionImage]] = {}
    if len(submission_ids) > 0:
        img_stmt = (
            select(models.TaskSubmissionImage)
            .where(models.TaskSubmissionImage.submission_id.in_(submission_ids))
            .order_by(models.TaskSubmissionImage.created_at.asc(), models.TaskSubmissionImage.id.asc())
        )
        for img in db.scalars(img_stmt).all():
            images_map.setdefault(int(img.submission_id), []).append(img)

    out: list[schemas.TaskAssignedOut] = []
    for task, submission in rows:
        task_out = schemas.TaskOut.model_validate(task)
        my_submission: schemas.TaskSubmissionOut | None = None
        if submission is not None:
            base = schemas.TaskSubmissionOut.model_validate(submission)
            my_submission = base.model_copy(
                update={
                    "images": [
                        schemas.TaskSubmissionImageOut.model_validate(img)
                        for img in images_map.get(int(submission.id), [])
                    ]
                }
            )

        out.append(schemas.TaskAssignedOut(**task_out.model_dump(), my_submission=my_submission))
    return out


@router.get("/{task_id}", response_model=schemas.TaskAssignedOut)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TaskAssignedOut:
    task = db.get(models.Task, int(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if int(current_user.role) < 3:
        _require_task_recipient(db, task_id=int(task_id), user_id=int(current_user.id))

    # my_submission is only meaningful for the current user
    stmt = select(models.TaskSubmission).where(
        models.TaskSubmission.task_id == int(task_id),
        models.TaskSubmission.user_id == int(current_user.id),
    )
    submission = db.scalar(stmt)

    images: list[schemas.TaskSubmissionImageOut] = []
    if submission is not None:
        img_stmt = (
            select(models.TaskSubmissionImage)
            .where(models.TaskSubmissionImage.submission_id == int(submission.id))
            .order_by(models.TaskSubmissionImage.created_at.asc(), models.TaskSubmissionImage.id.asc())
        )
        images = [schemas.TaskSubmissionImageOut.model_validate(img) for img in db.scalars(img_stmt).all()]

    my_submission = None
    if submission is not None:
        my_submission = schemas.TaskSubmissionOut.model_validate(submission).model_copy(update={"images": images})

    task_out = schemas.TaskOut.model_validate(task)
    return schemas.TaskAssignedOut(**task_out.model_dump(), my_submission=my_submission)


@router.put("/{task_id}/submission", response_model=schemas.TaskSubmissionOut)
async def upsert_my_submission(
    task_id: int,
    payload: schemas.TaskSubmissionUpsert,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TaskSubmissionOut:
    task = db.get(models.Task, int(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    _require_task_recipient(db, task_id=int(task_id), user_id=int(current_user.id))

    stmt = select(models.TaskSubmission).where(
        models.TaskSubmission.task_id == int(task_id),
        models.TaskSubmission.user_id == int(current_user.id),
    )
    submission = db.scalar(stmt)
    data = payload.model_dump(exclude_unset=True)

    if submission is None:
        submission = models.TaskSubmission(
            task_id=int(task_id),
            user_id=int(current_user.id),
            text_content=data.get("text_content"),
            suggestion=data.get("suggestion"),
        )
    else:
        if "text_content" in data:
            submission.text_content = data.get("text_content")
        if "suggestion" in data:
            submission.suggestion = data.get("suggestion")

    db.add(submission)
    db.flush()
    db.refresh(submission)

    img_stmt = (
        select(models.TaskSubmissionImage)
        .where(models.TaskSubmissionImage.submission_id == int(submission.id))
        .order_by(models.TaskSubmissionImage.created_at.asc(), models.TaskSubmissionImage.id.asc())
    )
    images = [schemas.TaskSubmissionImageOut.model_validate(img) for img in db.scalars(img_stmt).all()]
    out = schemas.TaskSubmissionOut.model_validate(submission)
    return out.model_copy(update={"images": images})


@router.post(
    "/{task_id}/submission/images",
    response_model=schemas.TaskSubmissionImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_submission_image(
    task_id: int,
    file: bytes = File(..., description="图片文件"),
    filename: str = Form(..., description="文件名"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TaskSubmissionImageUploadResponse:
    task = db.get(models.Task, int(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    _require_task_recipient(db, task_id=int(task_id), user_id=int(current_user.id))

    max_file_size = 10 * 1024 * 1024
    if len(file) > max_file_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过限制（最大 10MB）")

    # ensure submission exists
    stmt = select(models.TaskSubmission).where(
        models.TaskSubmission.task_id == int(task_id),
        models.TaskSubmission.user_id == int(current_user.id),
    )
    submission = db.scalar(stmt)
    if submission is None:
        submission = models.TaskSubmission(task_id=int(task_id), user_id=int(current_user.id))
        db.add(submission)
        db.flush()
        db.refresh(submission)

    try:
        upload_result = cos_service.upload_task_submission_image(
            file_content=file,
            task_id=int(task_id),
            user_id=int(current_user.id),
            original_filename=filename,
            max_size=(1920, 1080),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败：{str(e)}")

    row = models.TaskSubmissionImage(
        submission_id=int(submission.id),
        cos_key=upload_result["key"],
        url=upload_result["url"],
        original_filename=filename,
        file_size=upload_result["size"],
        width=upload_result["width"],
        height=upload_result["height"],
    )
    db.add(row)
    try:
        db.flush()
    except SQLAlchemyError:
        db.rollback()
        if not cos_service.delete_image(upload_result["key"]):
            enqueue_storage_cleanup(db, cos_key=upload_result["key"], source_table="task_submission_images")
            db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="图片保存失败")
    db.refresh(row)

    return schemas.TaskSubmissionImageUploadResponse(
        id=row.id,
        url=row.url,
        original_filename=row.original_filename,
        file_size=row.file_size,
        width=row.width,
        height=row.height,
        created_at=row.created_at,
    )


@router.delete("/{task_id}/submission/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission_image(
    task_id: int,
    image_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Response:
    image = db.get(models.TaskSubmissionImage, int(image_id))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    submission = db.get(models.TaskSubmission, int(image.submission_id))
    if not submission or int(submission.task_id) != int(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if int(submission.user_id) != int(current_user.id) and int(current_user.role) < 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此图片")

    enqueue_storage_cleanup(
        db,
        cos_key=image.cos_key,
        source_table="task_submission_images",
        source_id=int(image.id),
    )
    db.delete(image)
    db.flush()
    background_tasks.add_task(process_pending_cleanup_jobs)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


