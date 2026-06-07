from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.users.schemas import UserSettingsResponse, UserSettingsUpdateRequest
from app.modules.users.service import get_user_settings, update_user_settings


router = APIRouter()


@router.get("/me/settings", response_model=UserSettingsResponse)
def read_user_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> UserSettingsResponse:
    return get_user_settings(db, current_user)


@router.patch("/me/settings", response_model=UserSettingsResponse)
def patch_user_settings(
    payload: UserSettingsUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> UserSettingsResponse:
    return update_user_settings(db, current_user, payload)
