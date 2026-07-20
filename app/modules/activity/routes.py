from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.activity.schemas import ActivityType, AppNavigationActivityRequest, PlatformActivityRequest, UniversalActivityListResponse, UniversalActivitySummaryResponse
from app.modules.activity.service import list_activity, record_activity, record_app_navigation, serialize_activity
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user

router = APIRouter()


@router.get("", response_model=UniversalActivityListResponse)
def read_activity(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_parent_db)],
        page: Annotated[int, Query(ge=1)] = 1, page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
        type: ActivityType | None = None, app: str | None = None) -> UniversalActivityListResponse:
    items, total = list_activity(db, current_user, page=page, page_size=page_size, activity_type=type, app_slug=app)
    return UniversalActivityListResponse(items=[serialize_activity(item) for item in items], page=page, page_size=page_size, total=total)


@router.get("/summary", response_model=UniversalActivitySummaryResponse)
def read_activity_summary(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_parent_db)]) -> UniversalActivitySummaryResponse:
    items, _ = list_activity(db, current_user, page=1, page_size=5)
    return UniversalActivitySummaryResponse(items=[serialize_activity(item) for item in items])


@router.post("/navigation", response_model=None, status_code=204)
def publish_navigation(payload: AppNavigationActivityRequest, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_parent_db)]) -> None:
    record_app_navigation(db, current_user, payload.app_slug)


@router.post("/platform-event", response_model=None, status_code=204)
def publish_platform_event(payload: PlatformActivityRequest, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_parent_db)]) -> None:
    if payload.event == "assistant_used":
        record_activity(db, user_id=current_user.id, activity_type="assistant", title="Used Ansiversa AI", description="Asked the platform assistant for help.", source="assistant", action_route="/dashboard", action_label="Open Dashboard", deduplication_window=timedelta(minutes=10))
    else:
        record_activity(db, user_id=current_user.id, activity_type="notification", title="Opened a notification", description="Continued from the Notifications Center.", source="notification", deduplication_window=timedelta(minutes=10))
