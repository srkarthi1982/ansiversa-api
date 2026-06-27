from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.core.timing import timing_span
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


def _serialize_dashboard_entry(item: Dashboard) -> tuple[DashboardItemResponse, RecentAppResponse] | None:
    if item.app is None:
        return None

    app = DashboardAppResponse.model_validate(item.app)

    return (
        DashboardItemResponse(
            id=item.id,
            app=app,
            last_activity_at=item.last_activity_at,
            summary_version=item.summary_version,
            created_at=item.created_at,
            updated_at=item.updated_at,
            summary=parse_summary_json(item.summary_json),
        ),
        RecentAppResponse(
            app=app,
            last_activity_at=item.last_activity_at,
        ),
    )


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def read_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> DashboardSummaryResponse:
    with timing_span("dashboard.list_items"):
        dashboard_items = list_user_dashboard_items(db, current_user)
    with timing_span("dashboard.serialize_entries"):
        serialized_entries = [
            entry
            for entry in (_serialize_dashboard_entry(item) for item in dashboard_items)
            if entry is not None
        ]
    with timing_span("dashboard.count_favorites"):
        favorites_count = count_user_favorites(db, current_user)
    with timing_span("dashboard.count_unread_notifications"):
        unread_notifications_count = count_unread_notifications(db, current_user)

    with timing_span("dashboard.build_response_model"):
        return DashboardSummaryResponse(
            user=UserResponse.model_validate(current_user),
            favorites_count=favorites_count,
            unread_notifications_count=unread_notifications_count,
            recent_apps=[entry[1] for entry in serialized_entries],
            dashboard_items=[entry[0] for entry in serialized_entries],
        )
