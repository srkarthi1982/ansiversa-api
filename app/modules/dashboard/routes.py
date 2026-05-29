from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.schemas import UserResponse
from app.modules.auth.service import get_current_user
from app.modules.dashboard.models import Dashboard
from app.modules.dashboard.schemas import (
    DashboardAppResponse,
    DashboardItemResponse,
    DashboardSummaryResponse,
    RecentAppResponse,
)
from app.modules.dashboard.service import (
    count_unread_notifications,
    count_user_favorites,
    list_user_dashboard_items,
    parse_summary_json,
)

router = APIRouter()


def _serialize_dashboard_item(item: Dashboard) -> DashboardItemResponse:
    return DashboardItemResponse(
        id=item.id,
        app=DashboardAppResponse.model_validate(item.app),
        last_activity_at=item.last_activity_at,
        summary_version=item.summary_version,
        created_at=item.created_at,
        updated_at=item.updated_at,
        summary=parse_summary_json(item.summary_json),
    )


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def read_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> DashboardSummaryResponse:
    dashboard_items = list_user_dashboard_items(db, current_user)
    serialized_items = [
        _serialize_dashboard_item(item)
        for item in dashboard_items
    ]

    return DashboardSummaryResponse(
        user=UserResponse.model_validate(current_user),
        favorites_count=count_user_favorites(db, current_user),
        unread_notifications_count=count_unread_notifications(db, current_user),
        recent_apps=[
            RecentAppResponse(
                app=item.app,
                last_activity_at=item.last_activity_at,
            )
            for item in serialized_items
        ],
        dashboard_items=serialized_items,
    )
