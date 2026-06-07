from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    AuthStatusResponse,
    ChangePasswordRequest,
    CurrentUserResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutResponse,
    PasswordActionResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.modules.auth.service import (
    authenticate_user,
    change_password,
    create_parent_user,
    create_user_token,
    clear_auth_cookie,
    get_auth_status,
    get_current_user,
    request_password_reset,
    reset_password,
    set_auth_cookie,
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
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_parent_db)],
) -> User:
    return create_parent_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_parent_db)],
    response: Response,
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

    token_response = create_user_token(user)
    set_auth_cookie(response, token_response.access_token)

    return token_response


@router.post("/logout", response_model=LogoutResponse)
def logout_user(response: Response) -> LogoutResponse:
    clear_auth_cookie(response)

    return LogoutResponse(ok=True)


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.post("/forgot-password", response_model=PasswordActionResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Annotated[Session, Depends(get_parent_db)],
) -> PasswordActionResponse:
    response, _ = request_password_reset(db, payload)
    return response


@router.post("/reset-password", response_model=PasswordActionResponse)
def reset_user_password(
    payload: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_parent_db)],
) -> PasswordActionResponse:
    return reset_password(db, payload)


@router.post("/change-password", response_model=PasswordActionResponse)
def change_current_user_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> PasswordActionResponse:
    return change_password(db, current_user, payload)
