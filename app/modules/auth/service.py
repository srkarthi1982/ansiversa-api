from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_parent_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    is_legacy_parent_password_hash,
    oauth2_scheme,
    verify_legacy_parent_password,
    verify_password,
)
from app.modules.auth.models import Role, User
from app.modules.auth.schemas import (
    AuthStatusResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


DEFAULT_MEMBER_ROLE_ID = 2
ACTIVE_STATUS = "active"
BLOCKED_LOGIN_STATUSES = {"disabled", "inactive", "suspended"}


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


def create_user_token(user: User) -> TokenResponse:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "type": "access"},
        expires_delta=expires_delta,
    )

    return TokenResponse(access_token=access_token)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        email = payload.get("email")
        if isinstance(user_id, str) and user_id:
            user = get_user_by_id(db, user_id)
        elif isinstance(email, str) and email:
            user = get_user_by_email(db, email)
        else:
            raise credentials_exception
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    if not user or not is_login_allowed_status(user.status):
        raise credentials_exception

    return user
