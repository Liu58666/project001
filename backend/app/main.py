import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alembic import command
from alembic.config import Config

from app.api.routers import auth
from app.api.routers import admin_users
from app.api.routers import applications
from app.api.routers import admin_messages
from app.api.routers import admin_resume_pdfs
from app.api.routers import messages
from app.api.routers import images
from app.api.routers import news
from app.api.routers import resumes
from app.api.routers import user_images
from app.api.routers import tasks
from app.api.routers import users
from app.core.config import get_settings
from app.db.database import Base, engine

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="AuthService", version="0.1.0")

    # CORS placeholder; configure origins as needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router)
    app.include_router(auth.me_router)
    app.include_router(admin_users.router)
    app.include_router(admin_messages.router)
    app.include_router(admin_resume_pdfs.router)
    app.include_router(applications.router)
    app.include_router(applications.admin_router)
    app.include_router(messages.router)
    app.include_router(news.router)
    app.include_router(images.router)
    app.include_router(resumes.router)
    app.include_router(user_images.router)
    app.include_router(tasks.router)
    app.include_router(tasks.admin_router)
    app.include_router(users.router)

    # For local dev convenience; prefer Alembic in real deployments
    @app.on_event("startup")
    def _create_tables() -> None:
        # Run Alembic migrations automatically (keeps DB schema in sync with models)
        try:
            settings = get_settings()
            # alembic.ini uses %(DATABASE_URL)s interpolation; ensure it's present
            os.environ["DATABASE_URL"] = settings.database_url.unicode_string()

            repo_root = Path(__file__).resolve().parents[1]
            alembic_ini = repo_root / "alembic.ini"

            alembic_cfg = Config(str(alembic_ini))
            # Use absolute script_location to avoid cwd issues
            alembic_cfg.set_main_option("script_location", str(repo_root / "alembic"))
            # Also set url explicitly (env.py will set too; harmless)
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url.unicode_string())

            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            # Don't hard-fail startup; keep legacy behavior for dev
            logger.exception("Failed to run Alembic migrations on startup: %s", e)

        # Fallback: create missing tables (will NOT ALTER existing tables)
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()

