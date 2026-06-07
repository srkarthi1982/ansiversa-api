from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.users.models import UserSettings
from app.modules.users.schemas import UserSettingsResponse, UserSettingsUpdateRequest


def get_user_settings(db: Session, user: User) -> UserSettingsResponse:
    settings = db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    ).scalar_one_or_none()
    if not settings:
        return UserSettingsResponse()

    return UserSettingsResponse.model_validate(settings, from_attributes=True)


def update_user_settings(
    db: Session,
    user: User,
    payload: UserSettingsUpdateRequest,
) -> UserSettingsResponse:
    settings = db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    ).scalar_one_or_none()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(settings, field, value)

    settings.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(settings)

    return UserSettingsResponse.model_validate(settings, from_attributes=True)
