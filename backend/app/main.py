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
from app.core.config import Settings

def _configure_cors(app: FastAPI, settings: Settings) -> None:
    origins = settings.cors_origins
    development_origins = {"http://localhost:5173", "http://127.0.0.1:5173"}
    if settings.environment in {"development", "test"}:
        if not origins:
            origins = sorted(development_origins)
        if set(origins) - development_origins:
            raise RuntimeError("Development CORS origins are limited to the local Vite servers")
    if settings.environment == "production":
        if not origins:
            raise RuntimeError("CORS_ALLOWED_ORIGINS must be configured in production")
        if "*" in origins:
            raise RuntimeError("CORS_ALLOWED_ORIGINS cannot contain * in production")
    if "*" in origins:
        raise RuntimeError("CORS_ALLOWED_ORIGINS cannot use * when credentials are enabled")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _run_migrations(settings: Settings) -> None:
    os.environ["DATABASE_URL"] = settings.database_url.unicode_string()

    repo_root = Path(__file__).resolve().parents[1]
    alembic_ini = repo_root / "alembic.ini"

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("script_location", str(repo_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url.unicode_string())

    command.upgrade(alembic_cfg, "head")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="AuthService", version="0.1.0", debug=settings.debug)

    _configure_cors(app, settings)

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
    app.include_router(images.admin_router)
    app.include_router(resumes.router)
    app.include_router(user_images.router)
    app.include_router(tasks.router)
    app.include_router(tasks.admin_router)
    app.include_router(users.router)

    @app.on_event("startup")
    def _startup_migrations() -> None:
        if settings.auto_migrate:
            _run_migrations(settings)

    return app


app = create_app()

