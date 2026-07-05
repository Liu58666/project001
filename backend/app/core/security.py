from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(
    # bcrypt has a 72-byte password limit; bcrypt_sha256 avoids this safely.
    # Keep "bcrypt" for backward compatibility with existing stored hashes.
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
    bcrypt_sha256__rounds=settings.bcrypt_rounds,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_token(token: str) -> str:
    """
    One-way hash for storing refresh tokens server-side.
    Never persist raw refresh tokens in DB.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_token(
    subject: str,
    expires_delta: timedelta,
    token_type: str = "access",
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        # ensure token uniqueness even within the same second
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if additional_claims:
        payload.update(additional_claims)
    token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return token


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid token") from exc

