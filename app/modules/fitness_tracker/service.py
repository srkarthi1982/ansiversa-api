from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.fitness_tracker import repository
from app.modules.fitness_tracker.models import FitnessActivity, FitnessLog
from app.modules.fitness_tracker.schemas import (
    ActivityCreateRequest,
    ActivityDetailResponse,
    ActivitySummaryResponse,
    ActivityUpdateRequest,
    FitnessTrackerDashboardResponse,
    LogCreateRequest,
    LogDetailResponse,
    LogSummaryResponse,
    LogUpdateRequest,
    PaginatedActivityResponse,
    PaginatedLogResponse,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_activity(db: Session, user: User, activity_id: str) -> FitnessActivity:
    activity = repository.get_activity(db, activity_id)
    if not activity or activity.owner_id != user.id:
        _not_found("Activity was not found.")
    return activity


def _get_owned_log(db: Session, user: User, log_id: str) -> FitnessLog:
    log = repository.get_log(db, log_id)
    if not log or log.owner_id != user.id:
        _not_found("Fitness log was not found.")
    return log


def _activity_summary_response(activity: FitnessActivity) -> ActivitySummaryResponse:
    return ActivitySummaryResponse(
        id=activity.id,
        title=activity.title,
        activity_type=activity.activity_type,
        default_duration_minutes=activity.default_duration_minutes,
        intensity=activity.intensity,
        status=activity.status,
        notes_preview=_preview(activity.notes),
        log_count=len(activity.logs),
        total_minutes=sum(log.duration_minutes for log in activity.logs),
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )


def _activity_detail_response(activity: FitnessActivity) -> ActivityDetailResponse:
    logs = sorted(activity.logs, key=lambda item: (item.log_date, item.created_at), reverse=True)
    return ActivityDetailResponse(
        **_activity_summary_response(activity).model_dump(),
        notes=activity.notes,
        logs=[_log_summary_response(log) for log in logs],
    )


def _log_summary_response(log: FitnessLog) -> LogSummaryResponse:
    return LogSummaryResponse(
        id=log.id,
        activity_id=log.activity_id,
        activity_title=log.activity.title,
        activity_type=log.activity.activity_type,
        log_date=log.log_date,
        duration_minutes=log.duration_minutes,
        intensity=log.intensity,
        effort=log.effort,
        distance_value=log.distance_value,
        distance_unit=log.distance_unit,
        notes_preview=_preview(log.notes),
        created_at=log.created_at,
        updated_at=log.updated_at,
    )


def _log_detail_response(log: FitnessLog) -> LogDetailResponse:
    return LogDetailResponse(**_log_summary_response(log).model_dump(), notes=log.notes)


def _current_week_range() -> tuple[str, str]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat(), (monday + timedelta(days=7)).isoformat()


def list_activities(
    db: Session,
    user: User,
    *,
    query: str | None,
    activity_type: str | None,
    activity_status: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedActivityResponse:
    activities, total = repository.list_activities(
        db,
        user.id,
        query=query,
        activity_type=activity_type,
        status=activity_status,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedActivityResponse(
        items=[_activity_summary_response(activity) for activity in activities],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_activity(db: Session, user: User, payload: ActivityCreateRequest) -> ActivityDetailResponse:
    activity = FitnessActivity(owner_id=user.id, **payload.model_dump())
    repository.add(db, activity)
    db.commit()
    db.refresh(activity)
    return _activity_detail_response(activity)


def get_activity(db: Session, user: User, activity_id: str) -> ActivityDetailResponse:
    return _activity_detail_response(_get_owned_activity(db, user, activity_id))


def update_activity(db: Session, user: User, activity_id: str, payload: ActivityUpdateRequest) -> ActivityDetailResponse:
    activity = _get_owned_activity(db, user, activity_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    db.commit()
    db.refresh(activity)
    return _activity_detail_response(activity)


def delete_activity(db: Session, user: User, activity_id: str) -> None:
    activity = _get_owned_activity(db, user, activity_id)
    repository.delete_record(db, activity)
    db.commit()


def list_logs(
    db: Session,
    user: User,
    *,
    query: str | None,
    activity_id: str | None,
    activity_type: str | None,
    date_from: str | None,
    date_before: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedLogResponse:
    if activity_id:
        _get_owned_activity(db, user, activity_id)
    logs, total = repository.list_logs(
        db,
        user.id,
        query=query,
        activity_id=activity_id,
        activity_type=activity_type,
        date_from=date_from,
        date_before=date_before,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedLogResponse(
        items=[_log_summary_response(log) for log in logs],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_log(db: Session, user: User, payload: LogCreateRequest) -> LogDetailResponse:
    data = payload.model_dump()
    _get_owned_activity(db, user, data["activity_id"])
    log = FitnessLog(owner_id=user.id, **data)
    repository.add(db, log)
    db.commit()
    db.refresh(log)
    return _log_detail_response(log)


def get_log(db: Session, user: User, log_id: str) -> LogDetailResponse:
    return _log_detail_response(_get_owned_log(db, user, log_id))


def update_log(db: Session, user: User, log_id: str, payload: LogUpdateRequest) -> LogDetailResponse:
    log = _get_owned_log(db, user, log_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return _log_detail_response(log)


def delete_log(db: Session, user: User, log_id: str) -> None:
    log = _get_owned_log(db, user, log_id)
    repository.delete_record(db, log)
    db.commit()


def get_dashboard(db: Session, user: User) -> FitnessTrackerDashboardResponse:
    activities, _ = repository.list_activities(db, user.id, page_size=200)
    logs, _ = repository.list_logs(db, user.id, page_size=200)
    recent_logs, _ = repository.list_logs(db, user.id, sort="updatedAt", direction="desc", page_size=5)
    week_start, week_end = _current_week_range()
    return FitnessTrackerDashboardResponse(
        activities=[_activity_summary_response(activity) for activity in activities],
        logs=[_log_summary_response(log) for log in logs],
        activity_count=repository.count_activities(db, user.id),
        active_activity_count=repository.count_activities(db, user.id, status="active"),
        log_count=repository.count_logs(db, user.id),
        total_minutes=repository.total_minutes(db, user.id),
        weekly_minutes=repository.total_minutes(db, user.id, date_from=week_start, date_before=week_end),
        recent_logs=[_log_summary_response(log) for log in recent_logs],
    )
