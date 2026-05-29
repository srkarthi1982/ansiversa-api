from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.profile.schemas import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.modules.profile.service import (
    get_or_create_preferences,
    update_user_profile,
    upsert_preferences,
)

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
def read_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.patch("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> User:
    return update_user_profile(db, current_user, payload)


@router.get("/preferences", response_model=PreferencesResponse)
def read_preferences(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> PreferencesResponse:
    return get_or_create_preferences(db, current_user)


@router.put("/preferences", response_model=PreferencesResponse)
def update_preferences(
    payload: PreferencesUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> PreferencesResponse:
    return upsert_preferences(db, current_user, payload)
