from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.interview_scheduler.db import get_interview_scheduler_db
from app.modules.interview_scheduler.schemas import (
    InterviewCalendarEventCreateRequest,
    InterviewCalendarEventDetailResponse,
    InterviewCalendarEventSummaryResponse,
    InterviewCalendarEventUpdateRequest,
    InterviewHistoryCreateRequest,
    InterviewHistoryDetailResponse,
    InterviewHistorySummaryResponse,
    InterviewHistoryUpdateRequest,
    InterviewRoundCreateRequest,
    InterviewRoundDetailResponse,
    InterviewRoundSummaryResponse,
    InterviewRoundUpdateRequest,
    InterviewScheduleCreateRequest,
    InterviewScheduleDetailResponse,
    InterviewSchedulerDashboardResponse,
    InterviewScheduleSummaryResponse,
    InterviewScheduleUpdateRequest,
)
from app.modules.interview_scheduler.service import (
    create_calendar_event,
    create_history,
    create_round,
    create_schedule,
    delete_calendar_event,
    delete_history,
    delete_round,
    delete_schedule,
    get_calendar_event,
    get_dashboard,
    get_history,
    get_round,
    get_schedule,
    list_calendar_events,
    list_history,
    list_rounds,
    list_schedules,
    update_calendar_event,
    update_history,
    update_round,
    update_schedule,
)

router = APIRouter()


@router.get("/dashboard", response_model=InterviewSchedulerDashboardResponse)
def get_interview_scheduler_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewSchedulerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/schedules", response_model=InterviewScheduleDetailResponse, status_code=status.HTTP_201_CREATED)
def create_interview_schedule(
    payload: InterviewScheduleCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewScheduleDetailResponse:
    return create_schedule(db, current_user, payload)


@router.get("/schedules", response_model=list[InterviewScheduleSummaryResponse])
def list_interview_schedules(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> list[InterviewScheduleSummaryResponse]:
    return list_schedules(db, current_user)


@router.get("/schedules/{schedule_id}", response_model=InterviewScheduleDetailResponse)
def get_interview_schedule(
    schedule_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewScheduleDetailResponse:
    return get_schedule(db, current_user, schedule_id)


@router.put("/schedules/{schedule_id}", response_model=InterviewScheduleDetailResponse)
def update_interview_schedule(
    schedule_id: Annotated[int, Path(gt=0)],
    payload: InterviewScheduleUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewScheduleDetailResponse:
    return update_schedule(db, current_user, schedule_id, payload)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_schedule(
    schedule_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> None:
    delete_schedule(db, current_user, schedule_id)


@router.post("/rounds", response_model=InterviewRoundDetailResponse, status_code=status.HTTP_201_CREATED)
def create_interview_round(
    payload: InterviewRoundCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewRoundDetailResponse:
    return create_round(db, current_user, payload)


@router.get("/rounds", response_model=list[InterviewRoundSummaryResponse])
def list_interview_rounds(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> list[InterviewRoundSummaryResponse]:
    return list_rounds(db, current_user)


@router.get("/rounds/{round_id}", response_model=InterviewRoundDetailResponse)
def get_interview_round(
    round_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewRoundDetailResponse:
    return get_round(db, current_user, round_id)


@router.put("/rounds/{round_id}", response_model=InterviewRoundDetailResponse)
def update_interview_round(
    round_id: Annotated[int, Path(gt=0)],
    payload: InterviewRoundUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewRoundDetailResponse:
    return update_round(db, current_user, round_id, payload)


@router.delete("/rounds/{round_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_round(
    round_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> None:
    delete_round(db, current_user, round_id)


@router.post("/calendar", response_model=InterviewCalendarEventDetailResponse, status_code=status.HTTP_201_CREATED)
def create_interview_calendar_event(
    payload: InterviewCalendarEventCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewCalendarEventDetailResponse:
    return create_calendar_event(db, current_user, payload)


@router.get("/calendar", response_model=list[InterviewCalendarEventSummaryResponse])
def list_interview_calendar_events(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> list[InterviewCalendarEventSummaryResponse]:
    return list_calendar_events(db, current_user)


@router.get("/calendar/{event_id}", response_model=InterviewCalendarEventDetailResponse)
def get_interview_calendar_event(
    event_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewCalendarEventDetailResponse:
    return get_calendar_event(db, current_user, event_id)


@router.put("/calendar/{event_id}", response_model=InterviewCalendarEventDetailResponse)
def update_interview_calendar_event(
    event_id: Annotated[int, Path(gt=0)],
    payload: InterviewCalendarEventUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewCalendarEventDetailResponse:
    return update_calendar_event(db, current_user, event_id, payload)


@router.delete("/calendar/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_calendar_event(
    event_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> None:
    delete_calendar_event(db, current_user, event_id)


@router.post("/history", response_model=InterviewHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_interview_history(
    payload: InterviewHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[InterviewHistorySummaryResponse])
def list_interview_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> list[InterviewHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=InterviewHistoryDetailResponse)
def get_interview_history(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=InterviewHistoryDetailResponse)
def update_interview_history(
    history_id: Annotated[int, Path(gt=0)],
    payload: InterviewHistoryUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> InterviewHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_history(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_interview_scheduler_db)],
) -> None:
    delete_history(db, current_user, history_id)
