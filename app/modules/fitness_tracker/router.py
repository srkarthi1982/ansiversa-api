from typing import Literal

from fastapi import APIRouter, Query, Response, status

from app.modules.fitness_tracker import service
from app.modules.fitness_tracker.dependencies import CurrentFitnessTrackerUser, FitnessTrackerDB
from app.modules.fitness_tracker.schemas import (
    ActivityCreateRequest,
    ActivityDetailResponse,
    ActivityUpdateRequest,
    FitnessTrackerDashboardResponse,
    LogCreateRequest,
    LogDetailResponse,
    LogUpdateRequest,
    PaginatedActivityResponse,
    PaginatedLogResponse,
)

router = APIRouter()


@router.get("/dashboard", response_model=FitnessTrackerDashboardResponse)
def get_dashboard(db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    return service.get_dashboard(db, current_user)


@router.get("/activities", response_model=PaginatedActivityResponse)
def list_activities(
    db: FitnessTrackerDB,
    current_user: CurrentFitnessTrackerUser,
    q: str | None = Query(default=None, max_length=120),
    activity_type: str | None = Query(default=None, alias="activityType", max_length=40),
    activity_status: str | None = Query(default=None, alias="status", max_length=40),
    sort: Literal["title", "updatedAt"] = "updatedAt",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_activities(
        db,
        current_user,
        query=q,
        activity_type=activity_type,
        activity_status=activity_status,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/activities", response_model=ActivityDetailResponse, status_code=status.HTTP_201_CREATED)
def create_activity(payload: ActivityCreateRequest, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    return service.create_activity(db, current_user, payload)


@router.get("/activities/{activity_id}", response_model=ActivityDetailResponse)
def get_activity(activity_id: str, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    return service.get_activity(db, current_user, activity_id)


@router.put("/activities/{activity_id}", response_model=ActivityDetailResponse)
def update_activity(
    activity_id: str,
    payload: ActivityUpdateRequest,
    db: FitnessTrackerDB,
    current_user: CurrentFitnessTrackerUser,
):
    return service.update_activity(db, current_user, activity_id, payload)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: str, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    service.delete_activity(db, current_user, activity_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/logs", response_model=PaginatedLogResponse)
def list_logs(
    db: FitnessTrackerDB,
    current_user: CurrentFitnessTrackerUser,
    q: str | None = Query(default=None, max_length=120),
    activity_id: str | None = Query(default=None, alias="activityId", max_length=36),
    activity_type: str | None = Query(default=None, alias="activityType", max_length=40),
    date_from: str | None = Query(default=None, alias="dateFrom", max_length=40),
    date_before: str | None = Query(default=None, alias="dateBefore", max_length=40),
    sort: Literal["logDate", "updatedAt"] = "logDate",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_logs(
        db,
        current_user,
        query=q,
        activity_id=activity_id,
        activity_type=activity_type,
        date_from=date_from,
        date_before=date_before,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/logs", response_model=LogDetailResponse, status_code=status.HTTP_201_CREATED)
def create_log(payload: LogCreateRequest, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    return service.create_log(db, current_user, payload)


@router.get("/logs/{log_id}", response_model=LogDetailResponse)
def get_log(log_id: str, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    return service.get_log(db, current_user, log_id)


@router.put("/logs/{log_id}", response_model=LogDetailResponse)
def update_log(
    log_id: str,
    payload: LogUpdateRequest,
    db: FitnessTrackerDB,
    current_user: CurrentFitnessTrackerUser,
):
    return service.update_log(db, current_user, log_id, payload)


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: str, db: FitnessTrackerDB, current_user: CurrentFitnessTrackerUser):
    service.delete_log(db, current_user, log_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
