from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    AuthStatusResponse,
    CurrentUserResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
)
from app.modules.auth.service import (
    authenticate_user,
    create_parent_user,
    create_user_token,
    get_auth_status,
    get_current_user,
)

router = APIRouter()


@router.get("/status/", response_model=AuthStatusResponse)
def auth_status() -> AuthStatusResponse:
    return get_auth_status()


@router.post(
    "/register",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_parent_db)],
) -> User:
    return create_parent_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_parent_db)],
) -> TokenResponse:
    user = authenticate_user(
        db,
        LoginRequest(email=form_data.username, password=form_data.password),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_user_token(user)


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
