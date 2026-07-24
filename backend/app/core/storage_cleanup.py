from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cos_service import cos_service
from app.db import models
from app.db.database import SessionLocal


def enqueue_storage_cleanup(
    db: Session,
    *,
    cos_key: str | None,
    source_table: str,
    source_id: int | None = None,
) -> None:
    key = str(cos_key or "").strip()
    if not key:
        return
    db.add(
        models.StorageCleanupJob(
            cos_key=key,
            source_table=source_table,
            source_id=source_id,
        )
    )


def process_pending_cleanup_jobs(limit: int = 100) -> int:
    processed = 0
    with SessionLocal() as db:
        stmt = (
            select(models.StorageCleanupJob)
            .where(models.StorageCleanupJob.status == "pending")
            .order_by(models.StorageCleanupJob.created_at.asc(), models.StorageCleanupJob.id.asc())
            .limit(limit)
        )
        jobs = db.scalars(stmt).all()
        for job in jobs:
            try:
                ok = cos_service.delete_image(job.cos_key)
                if not ok:
                    raise RuntimeError("COS delete returned false")
                job.status = "done"
                job.processed_at = datetime.utcnow()
                job.last_error = None
                processed += 1
            except Exception as exc:
                job.attempts = int(job.attempts or 0) + 1
                job.last_error = str(exc)[:4000]
            db.add(job)
        db.commit()
    return processed


def cleanup_orphan_news_images(db: Session, *, older_than_hours: int = 24) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
    stmt = select(models.NewsImage).where(
        models.NewsImage.news_id.is_(None),
        models.NewsImage.created_at < cutoff,
    )
    rows = db.scalars(stmt).all()
    for row in rows:
        enqueue_storage_cleanup(
            db,
            cos_key=row.cos_key,
            source_table="news_images",
            source_id=int(row.id),
        )
        db.delete(row)
    db.flush()
    return len(rows)
