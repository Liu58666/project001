from app.core.storage_cleanup import cleanup_orphan_news_images, process_pending_cleanup_jobs
from app.db.database import SessionLocal


def main() -> None:
    with SessionLocal() as db:
        orphaned = cleanup_orphan_news_images(db)
        db.commit()
    processed = process_pending_cleanup_jobs()
    print(f"orphaned={orphaned} processed={processed}")


if __name__ == "__main__":
    main()
