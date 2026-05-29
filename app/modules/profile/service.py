from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.auth.models import User, UserPreference
from app.modules.profile.schemas import (
    PreferencesUpdateRequest,
    ProfileUpdateRequest,
)


def update_user_profile(
    db: Session,
    user: User,
    payload: ProfileUpdateRequest,
) -> User:
    updates = payload.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is not None:
        user.name = updates["name"]

    if "country_code" in updates:
        user.country_code = updates["country_code"]

    if "region_code" in updates:
        user.region_code = updates["region_code"]

    if "city" in updates:
        user.city = updates["city"]

    if "timezone" in updates:
        user.timezone = updates["timezone"]

    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_preferences(db: Session, user: User) -> UserPreference:
    preferences = db.get(UserPreference, user.id)
    if preferences:
        return preferences

    preferences = UserPreference(user_id=user.id)
    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def upsert_preferences(
    db: Session,
    user: User,
    payload: PreferencesUpdateRequest,
) -> UserPreference:
    preferences = db.get(UserPreference, user.id)

    if not preferences:
        preferences = UserPreference(user_id=user.id)
        db.add(preferences)

    preferences.product_updates = payload.product_updates
    preferences.security_alerts = payload.security_alerts
    preferences.theme = payload.theme
    preferences.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(preferences)

    return preferences
