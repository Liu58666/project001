from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cos_service import cos_service
from app.core.config import get_settings
from app.core.security import create_token, decode_token, hash_password, hash_token, verify_password
from app.core.verification_code import create_verification_code, verify_code
from app.db import models, schemas
from app.db.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])
me_router = APIRouter(prefix="/api", tags=["users"])
settings = get_settings()


@router.post("/send-code", response_model=schemas.SendCodeResponse)
async def send_verification_code(
    payload: schemas.SendCodeRequest, db: Session = Depends(get_db)
) -> schemas.SendCodeResponse:
    """
    发送验证码到指定手机号
    """
    try:
        create_verification_code(db, payload.phone)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return schemas.SendCodeResponse(
        resend_interval_seconds=settings.verification_code_resend_interval_seconds
    )


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: schemas.UserCreate, db: Session = Depends(get_db)
) -> schemas.UserOut:
    # 验证验证码
    if not verify_code(db, payload.phone, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    new_user = models.User(
        username=payload.username,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=0,
    )
    db.add(new_user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        stmt = select(models.User).where(
            (models.User.phone == payload.phone) | (models.User.username == payload.username)
        )
        existing = db.scalar(stmt)
        if existing and existing.phone == payload.phone:
            detail = "Phone already registered"
        elif existing and existing.username == payload.username:
            detail = "Username already taken"
        else:
            detail = "User already exists"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    return schemas.UserOut.model_validate(new_user)


@router.post("/login", response_model=schemas.TokenPair)
async def login(
    payload: schemas.UserLogin, db: Session = Depends(get_db)
) -> schemas.TokenPair:
    stmt = select(models.User).where(models.User.phone == payload.phone)
    user = db.scalar(stmt)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_expires = timedelta(days=settings.refresh_token_expire_days)

    # Bind role/roles into token claims for downstream authorization
    role_claims = {"role": int(user.role), "roles": [int(user.role)]}
    access_token = create_token(
        subject=str(user.id),
        expires_delta=access_expires,
        token_type="access",
        additional_claims=role_claims,
    )
    refresh_token = create_token(
        subject=str(user.id),
        expires_delta=refresh_expires,
        token_type="refresh",
        additional_claims=role_claims,
    )
    # Persist refresh token for rotation/revocation (store hash only)
    # Use naive UTC to match DB stored datetimes (avoid aware/naive comparison errors)
    now = datetime.utcnow()
    db.add(
        models.RefreshToken(
            user_id=int(user.id),
            token_hash=hash_token(refresh_token),
            issued_at=now,
            expires_at=now + refresh_expires,
        )
    )
    return schemas.TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_in=int(access_expires.total_seconds()),
        refresh_expires_in=int(refresh_expires.total_seconds()),
        username=user.username,
        created_at=user.created_at,
        email=user.email,
        birthday=user.birthday,
        photo=user.photo,
    )


@router.post("/refresh", response_model=schemas.TokenPair)
async def refresh_access_token(
    payload: schemas.RefreshTokenRequest, db: Session = Depends(get_db)
) -> schemas.TokenPair:
    """
    Refresh access token using a refresh token.

    Implements refresh token rotation:
    - each refresh issues a new refresh_token
    - the old refresh_token is revoked immediately
    """

    def _invalid_refresh() -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    raw_refresh = payload.refresh_token
    try:
        token_payload = decode_token(raw_refresh)
    except Exception:
        _invalid_refresh()

    if token_payload.get("type") != "refresh" or token_payload.get("sub") is None:
        _invalid_refresh()

    try:
        user_id = int(token_payload["sub"])
    except Exception:
        _invalid_refresh()

    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        _invalid_refresh()

    # Use naive UTC to match DB stored datetimes (avoid aware/naive comparison errors)
    now = datetime.utcnow()
    incoming_hash = hash_token(raw_refresh)

    # Lock this refresh-token row until the replacement is flushed.  A second
    # concurrent request then sees revoked_at and cannot rotate it again.
    stmt = (
        select(models.RefreshToken)
        .where(models.RefreshToken.token_hash == incoming_hash)
        .with_for_update()
    )
    stored = db.scalar(stmt)

    if stored is None:
        # Legacy bootstrap: token is a valid JWT refresh token (signature+exp),
        # but was issued before we persisted refresh tokens. Store it as revoked
        # so it becomes single-use from now on.
        try:
            issued_at = datetime.utcfromtimestamp(int(token_payload.get("iat", now.timestamp())))
            expires_at = datetime.utcfromtimestamp(int(token_payload.get("exp", now.timestamp())))
        except Exception:
            issued_at = now
            expires_at = now

        stored = models.RefreshToken(
            user_id=user_id,
            token_hash=incoming_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked_at=now,
        )
        db.add(stored)
        db.flush()
    else:
        if stored.user_id != user_id or stored.revoked_at is not None or stored.expires_at <= now:
            _invalid_refresh()
        stored.revoked_at = now

    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_expires = timedelta(days=settings.refresh_token_expire_days)

    role_claims = {"role": int(user.role), "roles": [int(user.role)]}
    access_token = create_token(
        subject=str(user.id),
        expires_delta=access_expires,
        token_type="access",
        additional_claims=role_claims,
    )
    new_refresh_token = create_token(
        subject=str(user.id),
        expires_delta=refresh_expires,
        token_type="refresh",
        additional_claims=role_claims,
    )

    new_row = models.RefreshToken(
        user_id=int(user.id),
        token_hash=hash_token(new_refresh_token),
        issued_at=now,
        expires_at=now + refresh_expires,
    )
    db.add(new_row)
    db.flush()

    stored.replaced_by_id = new_row.id

    return schemas.TokenPair(
        access_token=access_token,
        refresh_token=new_refresh_token,
        access_expires_in=int(access_expires.total_seconds()),
        refresh_expires_in=int(refresh_expires.total_seconds()),
        username=user.username,
        created_at=user.created_at,
        email=user.email,
        birthday=user.birthday,
        photo=user.photo,
    )


@me_router.get("/me", response_model=schemas.UserOut)
async def read_me(current_user: models.User = Depends(get_current_user)) -> schemas.UserOut:
    return schemas.UserOut.model_validate(current_user)


@me_router.get("/me/profile", response_model=schemas.UserProfileOut)
async def read_my_profile(current_user: models.User = Depends(get_current_user)) -> schemas.UserProfileOut:
    """
    返回当前用户资料（username, phone, email, birthday, created_at, updated_at）
    """
    return schemas.UserProfileOut.model_validate(current_user)


@me_router.patch("/me/profile", response_model=schemas.UserOut)
async def update_my_profile(
    payload: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserOut:
    """
    更新当前用户资料：email / birthday
    photo 目前默认空，后续如需上传/更新再单独扩展接口
    """
    if payload.username is not None:
        current_user.username = payload.username
    if payload.email is not None:
        current_user.email = payload.email
    if payload.birthday is not None:
        current_user.birthday = payload.birthday

    db.add(current_user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # keep user_resumes email in sync with profile changes
    if payload.email is not None:
        stmt = select(models.UserResume).where(models.UserResume.user_id == int(current_user.id))
        resume = db.scalar(stmt)
        if resume is not None:
            resume.email = current_user.email
            resume.phone = current_user.phone
            db.add(resume)
            db.flush()
    return schemas.UserOut.model_validate(current_user)


@me_router.post("/me/photo", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def upload_my_photo(
    file: bytes = File(..., description="头像图片文件"),
    filename: str = Form(..., description="文件名"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserOut:
    """
    上传/更新当前用户头像：
    - 上传到腾讯云 COS（users/{user_id}/avatar/...）
    - 更新 users.photo 为头像 URL
    - 同时在 user_images 记录一条 image_type=avatar（便于履历/历史使用）
    """
    max_file_size = 10 * 1024 * 1024  # 10MB
    if len(file) > max_file_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过限制（最大 10MB）")

    try:
        upload_result = cos_service.upload_user_image(
            file_content=file,
            user_id=int(current_user.id),
            # user profile photo should not affect resume avatar (which uses user_images image_type='avatar')
            image_type="photo",
            original_filename=filename,
            max_size=(800, 800),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败：{str(e)}")

    # Update user.photo
    current_user.photo = upload_result["url"]
    db.add(current_user)

    try:
        db.flush()
    except SQLAlchemyError:
        db.rollback()
        # The object is not referenced if the user update fails.
        cos_service.delete_image(upload_result["key"])
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="头像保存失败")
    return schemas.UserOut.model_validate(current_user)

