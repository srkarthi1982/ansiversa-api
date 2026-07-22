from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timing import set_timing_user_id, timing_span
from app.core.database import get_parent_db
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_access_token,
    get_password_hash,
    hash_password_reset_token,
    is_legacy_parent_password_hash,
    oauth2_scheme,
    verify_legacy_parent_password,
    verify_password,
)
from app.modules.auth.constants import DEFAULT_MEMBER_ROLE_ID
from app.modules.auth.models import PasswordResetToken, Role, User
from app.modules.auth.schemas import (
    AuthStatusResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    PasswordActionResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)


ACTIVE_STATUS = "active"
BLOCKED_LOGIN_STATUSES = {"disabled", "inactive", "suspended"}
FORGOT_PASSWORD_MESSAGE = (
    "If the account exists, password reset instructions will be available."
)
RESET_PASSWORD_MESSAGE = "Password has been reset successfully."
CHANGE_PASSWORD_MESSAGE = "Password changed successfully."
PASSWORD_REUSE_ERROR = "New password must be different from the current password."


def get_auth_status() -> AuthStatusResponse:
    return AuthStatusResponse(
        status="ok",
        service="ansiversa-auth",
        auth_ready=True,
        message="Parent authentication foundation is enabled.",
    )


def is_login_allowed_status(value: str | None) -> bool:
    normalized = (value or ACTIVE_STATUS).strip().lower()

    return normalized not in BLOCKED_LOGIN_STATUSES


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def ensure_default_member_role(db: Session) -> Role:
    role = db.get(Role, DEFAULT_MEMBER_ROLE_ID)
    if role:
        return role

    role = Role(
        id=DEFAULT_MEMBER_ROLE_ID,
        name="Member",
        key="member",
        description="Default Ansiversa member role.",
    )
    db.add(role)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.get(Role, DEFAULT_MEMBER_ROLE_ID)
        if existing:
            return existing
        raise

    return role


def create_parent_user(db: Session, payload: RegisterRequest) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    ensure_default_member_role(db)

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=get_password_hash(payload.password),
        role_id=DEFAULT_MEMBER_ROLE_ID,
        status=ACTIVE_STATUS,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc

    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User | None:
    user = get_user_by_email(db, payload.email)
    if not user:
        return None

    is_legacy_hash = is_legacy_parent_password_hash(user.password_hash)
    password_valid = (
        verify_legacy_parent_password(payload.password, user.password_hash)
        if is_legacy_hash
        else verify_password(payload.password, user.password_hash)
    )
    if not password_valid:
        return None

    if not is_login_allowed_status(user.status):
        return None

    if is_legacy_hash:
        user.password_hash = get_password_hash(payload.password)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def request_password_reset(
    db: Session,
    payload: ForgotPasswordRequest,
) -> tuple[PasswordActionResponse, str | None]:
    user = get_user_by_email(db, payload.email)
    if not user:
        return PasswordActionResponse(message=FORGOT_PASSWORD_MESSAGE), None

    now = datetime.now(timezone.utc)
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    token = create_password_reset_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_password_reset_token(token),
            expires_at=now
            + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
    )
    db.commit()

    return PasswordActionResponse(message=FORGOT_PASSWORD_MESSAGE), token


def reset_password(
    db: Session,
    payload: ResetPasswordRequest,
) -> PasswordActionResponse:
    reset_token = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_password_reset_token(payload.token),
            PasswordResetToken.used_at.is_(None),
        )
    ).scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if not reset_token or _as_utc(reset_token.expires_at) <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or expired.",
        )

    user = get_user_by_id(db, reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or expired.",
        )

    if _password_matches_hash(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PASSWORD_REUSE_ERROR,
        )

    user.password_hash = get_password_hash(payload.new_password)
    user.updated_at = now
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    db.add(user)
    db.commit()

    return PasswordActionResponse(message=RESET_PASSWORD_MESSAGE)


def change_password(
    db: Session,
    user: User,
    payload: ChangePasswordRequest,
) -> PasswordActionResponse:
    current_password_valid = (
        verify_legacy_parent_password(payload.current_password, user.password_hash)
        if is_legacy_parent_password_hash(user.password_hash)
        else verify_password(payload.current_password, user.password_hash)
    )
    if not current_password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    if _password_matches_hash(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PASSWORD_REUSE_ERROR,
        )

    user.password_hash = get_password_hash(payload.new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    return PasswordActionResponse(message=CHANGE_PASSWORD_MESSAGE)


def _password_matches_hash(password: str, password_hash: str) -> bool:
    if is_legacy_parent_password_hash(password_hash):
        return verify_legacy_parent_password(password, password_hash)

    return verify_password(password, password_hash)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def create_user_token(user: User) -> TokenResponse:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "type": "access"},
        expires_delta=expires_delta,
    )

    return TokenResponse(access_token=access_token)


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        max_age=settings.AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=bool(settings.AUTH_COOKIE_SECURE),
        samesite=settings.AUTH_COOKIE_SAMESITE or "lax",
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        key=settings.AUTH_SESSION_HINT_COOKIE_NAME,
        value="1",
        max_age=settings.AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=False,
        secure=bool(settings.AUTH_COOKIE_SECURE),
        samesite=settings.AUTH_COOKIE_SAMESITE or "lax",
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        httponly=True,
        secure=bool(settings.AUTH_COOKIE_SECURE),
        samesite=settings.AUTH_COOKIE_SAMESITE or "lax",
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
    )
    response.delete_cookie(
        key=settings.AUTH_SESSION_HINT_COOKIE_NAME,
        httponly=False,
        secure=bool(settings.AUTH_COOKIE_SECURE),
        samesite=settings.AUTH_COOKIE_SAMESITE or "lax",
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
    )


def get_current_user(
    request: Request,
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = bearer_token or request.cookies.get(settings.AUTH_COOKIE_NAME)
    if not token:
        raise credentials_exception

    try:
        with timing_span("auth.decode_access_token"):
            payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        email = payload.get("email")
        if isinstance(user_id, str) and user_id:
            with timing_span("auth.current_user_lookup_by_id"):
                user = get_user_by_id(db, user_id)
        elif isinstance(email, str) and email:
            with timing_span("auth.current_user_lookup_by_email"):
                user = get_user_by_email(db, email)
        else:
            raise credentials_exception
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    with timing_span("auth.status_check"):
        is_allowed = bool(user and is_login_allowed_status(user.status))

    if not user or not is_allowed:
        raise credentials_exception

    set_timing_user_id(user.id)

    return user


def get_optional_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> User | None:
    authorization = request.headers.get("authorization") or ""
    scheme, _, bearer_token = authorization.partition(" ")
    token = (
        bearer_token.strip()
        if scheme.lower() == "bearer" and bearer_token.strip()
        else request.cookies.get(settings.AUTH_COOKIE_NAME)
    )
    if not token:
        return None

    try:
        with timing_span("auth.decode_optional_access_token"):
            payload = decode_access_token(token)
        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        email = payload.get("email")
        if isinstance(user_id, str) and user_id:
            with timing_span("auth.optional_current_user_lookup_by_id"):
                user = get_user_by_id(db, user_id)
        elif isinstance(email, str) and email:
            with timing_span("auth.optional_current_user_lookup_by_email"):
                user = get_user_by_email(db, email)
        else:
            return None
    except InvalidTokenError:
        return None

    if not user or not is_login_allowed_status(user.status):
        return None

    set_timing_user_id(user.id)

    return user
