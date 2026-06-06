from datetime import datetime, timedelta, timezone
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


def is_legacy_parent_password_hash(hashed_password: str) -> bool:
    salt, separator, digest = hashed_password.partition(":")

    return bool(separator and salt and digest)


def verify_legacy_parent_password(plain_password: str, hashed_password: str) -> bool:
    salt, separator, digest = hashed_password.partition(":")
    if not separator or not salt or not digest:
        return False

    hmac = hmac_new(
        settings.ANSIVERSA_AUTH_SECRET.encode("utf-8"),
        digestmod=sha256,
    )
    hmac.update(f"{salt}:{plain_password}".encode("utf-8"))
    check = hmac.hexdigest()

    return compare_digest(check, digest)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    if not settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured.")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    if not settings.JWT_SECRET_KEY:
        raise InvalidTokenError("JWT_SECRET_KEY is not configured.")

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
