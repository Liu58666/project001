"""
验证码生成和验证服务
"""
import hmac
import secrets
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.sms_service import send_sms_code
from app.db import models

settings = get_settings()


def generate_code(length: int = None) -> str:
    """生成数字验证码"""
    if length is None:
        length = settings.verification_code_length
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_verification_code(phone: str, code: str) -> str:
    message = f"{str(phone).strip()}:{str(code).strip()}".encode("utf-8")
    return hmac.new(settings.jwt_secret_key.encode("utf-8"), message, sha256).hexdigest()


def create_verification_code(db: Session, phone: str) -> models.VerificationCode:
    """
    创建并发送验证码

    Args:
        db: 数据库会话
        phone: 手机号

    Returns:
        VerificationCode: 创建的验证码记录
    """
    # 检查是否在重发间隔内
    stmt = select(models.VerificationCode).where(
        models.VerificationCode.phone == phone,
        models.VerificationCode.is_used == False,
        models.VerificationCode.expires_at > datetime.utcnow(),
    ).order_by(models.VerificationCode.created_at.desc())
    recent_code = db.scalar(stmt)
    if recent_code:
        time_since_last = (datetime.utcnow() - recent_code.created_at).total_seconds()
        if time_since_last < settings.verification_code_resend_interval_seconds:
            raise ValueError(
                f"Please wait {int(settings.verification_code_resend_interval_seconds - time_since_last)} seconds before requesting a new code"
            )

    db.execute(
        update(models.VerificationCode)
        .where(
            models.VerificationCode.phone == phone,
            models.VerificationCode.is_used == False,
        )
        .values(is_used=True)
    )

    # 生成新验证码
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.verification_code_expire_minutes
    )

    verification_code = models.VerificationCode(
        phone=phone,
        code="",
        code_hash=hash_verification_code(phone, code),
        expires_at=expires_at,
        is_used=False,
    )
    db.add(verification_code)
    db.flush()

    # 发送短信
    if not send_sms_code(phone, code):
        db.rollback()
        raise RuntimeError("Failed to send verification code")

    return verification_code


def verify_code(db: Session, phone: str, code: str) -> bool:
    """
    验证验证码

    Args:
        db: 数据库会话
        phone: 手机号
        code: 验证码

    Returns:
        bool: 验证是否成功
    """
    stmt = select(models.VerificationCode).where(
        models.VerificationCode.phone == phone,
        models.VerificationCode.code_hash == hash_verification_code(phone, code),
        models.VerificationCode.is_used == False,
        models.VerificationCode.expires_at > datetime.utcnow(),
    ).order_by(models.VerificationCode.created_at.desc())

    verification_code = db.scalar(stmt)
    if not verification_code:
        return False

    # 标记为已使用
    verification_code.is_used = True
    db.flush()
    return True

