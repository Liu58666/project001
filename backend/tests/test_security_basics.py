import pytest
from fastapi import FastAPI
from pydantic import ValidationError

from app.core.config import Settings
from app.core.verification_code import generate_code, hash_verification_code
from app.db.schemas import AdminUserUpdate
from app.main import _configure_cors


def test_verification_code_is_secret_and_hash_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/test")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    first = generate_code()
    second = generate_code()

    assert first.isdigit() and len(first) == 6
    assert second.isdigit() and len(second) == 6
    assert hash_verification_code("138****0000", first) == hash_verification_code("138****0000", first)
    assert hash_verification_code("138****0000", first) != hash_verification_code("138****0001", first)


def test_admin_role_schema_rejects_role_five() -> None:
    with pytest.raises(ValidationError):
        AdminUserUpdate(role=5)


def test_development_cors_defaults_are_local_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/test")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    settings = Settings()
    assert settings.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_cors_rejects_non_local_development_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/test")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://example.test")
    with pytest.raises(RuntimeError, match="Development CORS origins"):
        _configure_cors(FastAPI(), Settings())
