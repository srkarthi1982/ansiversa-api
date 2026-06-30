from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.interview_scheduler.models import (
    InterviewCalendarEvent,
    InterviewHistory,
    InterviewRound,
    InterviewSchedule,
)
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _schedule_title(schedule: InterviewSchedule) -> str:
    if schedule.company_name:
        return f"{schedule.candidate_name} - {schedule.role_title} at {schedule.company_name}"
    return f"{schedule.candidate_name} - {schedule.role_title}"


def _get_owned_schedule(db: Session, user: User, schedule_id: int) -> InterviewSchedule:
    schedule = db.get(InterviewSchedule, schedule_id)
    if not schedule or schedule.owner_id != user.id:
        _not_found("Interview schedule was not found.")
    return schedule


def _get_owned_round(db: Session, user: User, round_id: int) -> InterviewRound:
    round_ = db.get(InterviewRound, round_id)
    if not round_ or round_.owner_id != user.id:
        _not_found("Interview round was not found.")
    return round_


def _get_owned_event(db: Session, user: User, event_id: int) -> InterviewCalendarEvent:
    event = db.get(InterviewCalendarEvent, event_id)
    if not event or event.owner_id != user.id:
        _not_found("Interview calendar event was not found.")
    return event


def _get_owned_history(db: Session, user: User, history_id: int) -> InterviewHistory:
    history = db.get(InterviewHistory, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Interview history record was not found.")
    return history


def _optional_owned_round(db: Session, user: User, round_id: int | None) -> InterviewRound | None:
    if round_id is None:
        return None
    return _get_owned_round(db, user, round_id)


def _count_rounds(db: Session, schedule_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(InterviewRound).where(InterviewRound.schedule_id == schedule_id)).scalar_one())


def _count_events(db: Session, schedule_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(InterviewCalendarEvent).where(InterviewCalendarEvent.schedule_id == schedule_id)).scalar_one())


def _count_history(db: Session, schedule_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(InterviewHistory).where(InterviewHistory.schedule_id == schedule_id)).scalar_one())


def _schedule_summary_response(db: Session, schedule: InterviewSchedule) -> InterviewScheduleSummaryResponse:
    return InterviewScheduleSummaryResponse(
        id=schedule.id,
        platform_id=schedule.platform_id,
        candidate_name=schedule.candidate_name,
        role_title=schedule.role_title,
        company_name=schedule.company_name,
        interview_stage=schedule.interview_stage,
        status=schedule.status,
        priority=schedule.priority,
        target_date=schedule.target_date,
        round_count=_count_rounds(db, schedule.id),
        event_count=_count_events(db, schedule.id),
        history_count=_count_history(db, schedule.id),
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def _schedule_detail_response(db: Session, schedule: InterviewSchedule) -> InterviewScheduleDetailResponse:
    summary = _schedule_summary_response(db, schedule)
    return InterviewScheduleDetailResponse(**summary.model_dump(), notes=schedule.notes)


def _round_summary_response(round_: InterviewRound, schedule_title: str) -> InterviewRoundSummaryResponse:
    return InterviewRoundSummaryResponse(
        id=round_.id,
        platform_id=round_.platform_id,
        schedule_id=round_.schedule_id,
        schedule_title=schedule_title,
        round_name=round_.round_name,
        interviewer_name=round_.interviewer_name,
        interview_type=round_.interview_type,
        sequence=round_.sequence,
        status=round_.status,
        scheduled_at=round_.scheduled_at,
        location=round_.location,
        preparation_preview=_preview(round_.preparation_notes),
        created_at=round_.created_at,
        updated_at=round_.updated_at,
    )


def _round_detail_response(round_: InterviewRound, schedule_title: str) -> InterviewRoundDetailResponse:
    summary = _round_summary_response(round_, schedule_title)
    return InterviewRoundDetailResponse(**summary.model_dump(), preparation_notes=round_.preparation_notes)


def _event_summary_response(
    event: InterviewCalendarEvent,
    schedule_title: str,
    round_name: str | None,
) -> InterviewCalendarEventSummaryResponse:
    return InterviewCalendarEventSummaryResponse(
        id=event.id,
        platform_id=event.platform_id,
        schedule_id=event.schedule_id,
        schedule_title=schedule_title,
        round_id=event.round_id,
        round_name=round_name,
        title=event.title,
        event_type=event.event_type,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        reminder_minutes=event.reminder_minutes,
        location=event.location,
        notes_preview=_preview(event.notes),
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def _event_detail_response(
    event: InterviewCalendarEvent,
    schedule_title: str,
    round_name: str | None,
) -> InterviewCalendarEventDetailResponse:
    summary = _event_summary_response(event, schedule_title, round_name)
    return InterviewCalendarEventDetailResponse(**summary.model_dump(), notes=event.notes)


def _history_summary_response(history: InterviewHistory, schedule_title: str) -> InterviewHistorySummaryResponse:
    return InterviewHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        schedule_id=history.schedule_id,
        schedule_title=schedule_title,
        title=history.title,
        outcome=history.outcome,
        completed_at=history.completed_at,
        summary_preview=_preview(history.summary),
        next_steps_preview=_preview(history.next_steps),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: InterviewHistory, schedule_title: str) -> InterviewHistoryDetailResponse:
    summary = _history_summary_response(history, schedule_title)
    return InterviewHistoryDetailResponse(
        **summary.model_dump(),
        summary=history.summary,
        next_steps=history.next_steps,
    )


def list_schedules(db: Session, user: User) -> list[InterviewScheduleSummaryResponse]:
    schedules = list(db.execute(select(InterviewSchedule).where(InterviewSchedule.owner_id == user.id).order_by(InterviewSchedule.updated_at.desc(), InterviewSchedule.candidate_name.asc())).scalars().all())
    return [_schedule_summary_response(db, schedule) for schedule in schedules]


def create_schedule(db: Session, user: User, payload: InterviewScheduleCreateRequest) -> InterviewScheduleDetailResponse:
    schedule = InterviewSchedule(owner_id=user.id, **payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return _schedule_detail_response(db, schedule)


def get_schedule(db: Session, user: User, schedule_id: int) -> InterviewScheduleDetailResponse:
    return _schedule_detail_response(db, _get_owned_schedule(db, user, schedule_id))


def update_schedule(db: Session, user: User, schedule_id: int, payload: InterviewScheduleUpdateRequest) -> InterviewScheduleDetailResponse:
    schedule = _get_owned_schedule(db, user, schedule_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return _schedule_detail_response(db, schedule)


def delete_schedule(db: Session, user: User, schedule_id: int) -> None:
    schedule = _get_owned_schedule(db, user, schedule_id)
    db.execute(delete(InterviewCalendarEvent).where(InterviewCalendarEvent.schedule_id == schedule.id))
    db.execute(delete(InterviewHistory).where(InterviewHistory.schedule_id == schedule.id))
    db.execute(delete(InterviewRound).where(InterviewRound.schedule_id == schedule.id))
    db.delete(schedule)
    db.commit()


def list_rounds(db: Session, user: User) -> list[InterviewRoundSummaryResponse]:
    rows = db.execute(
        select(InterviewRound, InterviewSchedule)
        .join(InterviewSchedule, InterviewSchedule.id == InterviewRound.schedule_id)
        .where(InterviewRound.owner_id == user.id)
        .order_by(InterviewRound.updated_at.desc(), InterviewRound.sequence.asc())
    ).all()
    return [_round_summary_response(round_, _schedule_title(schedule)) for round_, schedule in rows]


def create_round(db: Session, user: User, payload: InterviewRoundCreateRequest) -> InterviewRoundDetailResponse:
    schedule = _get_owned_schedule(db, user, payload.schedule_id)
    round_ = InterviewRound(owner_id=user.id, **payload.model_dump())
    db.add(round_)
    db.commit()
    db.refresh(round_)
    return _round_detail_response(round_, _schedule_title(schedule))


def get_round(db: Session, user: User, round_id: int) -> InterviewRoundDetailResponse:
    round_ = _get_owned_round(db, user, round_id)
    schedule = _get_owned_schedule(db, user, round_.schedule_id)
    return _round_detail_response(round_, _schedule_title(schedule))


def update_round(db: Session, user: User, round_id: int, payload: InterviewRoundUpdateRequest) -> InterviewRoundDetailResponse:
    round_ = _get_owned_round(db, user, round_id)
    data = payload.model_dump(exclude_unset=True)
    schedule = _get_owned_schedule(db, user, round_.schedule_id)
    for field, value in data.items():
        setattr(round_, field, value)
    db.commit()
    db.refresh(round_)
    return _round_detail_response(round_, _schedule_title(schedule))


def delete_round(db: Session, user: User, round_id: int) -> None:
    round_ = _get_owned_round(db, user, round_id)
    db.execute(delete(InterviewCalendarEvent).where(InterviewCalendarEvent.round_id == round_.id))
    db.delete(round_)
    db.commit()


def list_calendar_events(db: Session, user: User) -> list[InterviewCalendarEventSummaryResponse]:
    rows = db.execute(
        select(InterviewCalendarEvent, InterviewSchedule, InterviewRound.round_name)
        .join(InterviewSchedule, InterviewSchedule.id == InterviewCalendarEvent.schedule_id)
        .outerjoin(InterviewRound, InterviewRound.id == InterviewCalendarEvent.round_id)
        .where(InterviewCalendarEvent.owner_id == user.id)
        .order_by(InterviewCalendarEvent.starts_at.asc(), InterviewCalendarEvent.updated_at.desc())
    ).all()
    return [_event_summary_response(event, _schedule_title(schedule), round_name) for event, schedule, round_name in rows]


def create_calendar_event(db: Session, user: User, payload: InterviewCalendarEventCreateRequest) -> InterviewCalendarEventDetailResponse:
    schedule = _get_owned_schedule(db, user, payload.schedule_id)
    round_ = _optional_owned_round(db, user, payload.round_id)
    if round_ and round_.schedule_id != schedule.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Round must belong to the selected schedule.")
    event = InterviewCalendarEvent(owner_id=user.id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return _event_detail_response(event, _schedule_title(schedule), round_.round_name if round_ else None)


def get_calendar_event(db: Session, user: User, event_id: int) -> InterviewCalendarEventDetailResponse:
    event = _get_owned_event(db, user, event_id)
    schedule = _get_owned_schedule(db, user, event.schedule_id)
    round_ = _optional_owned_round(db, user, event.round_id)
    return _event_detail_response(event, _schedule_title(schedule), round_.round_name if round_ else None)


def update_calendar_event(db: Session, user: User, event_id: int, payload: InterviewCalendarEventUpdateRequest) -> InterviewCalendarEventDetailResponse:
    event = _get_owned_event(db, user, event_id)
    data = payload.model_dump(exclude_unset=True)
    schedule = _get_owned_schedule(db, user, event.schedule_id)
    round_ = _optional_owned_round(db, user, data.get("round_id") if "round_id" in data else event.round_id)
    if round_ and round_.schedule_id != schedule.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Round must belong to the selected schedule.")
    for field, value in data.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return _event_detail_response(event, _schedule_title(schedule), round_.round_name if round_ else None)


def delete_calendar_event(db: Session, user: User, event_id: int) -> None:
    event = _get_owned_event(db, user, event_id)
    db.delete(event)
    db.commit()


def list_history(db: Session, user: User) -> list[InterviewHistorySummaryResponse]:
    rows = db.execute(
        select(InterviewHistory, InterviewSchedule)
        .join(InterviewSchedule, InterviewSchedule.id == InterviewHistory.schedule_id)
        .where(InterviewHistory.owner_id == user.id)
        .order_by(InterviewHistory.updated_at.desc(), InterviewHistory.completed_at.desc())
    ).all()
    return [_history_summary_response(history, _schedule_title(schedule)) for history, schedule in rows]


def create_history(db: Session, user: User, payload: InterviewHistoryCreateRequest) -> InterviewHistoryDetailResponse:
    schedule = _get_owned_schedule(db, user, payload.schedule_id)
    history = InterviewHistory(owner_id=user.id, **payload.model_dump())
    db.add(history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, _schedule_title(schedule))


def get_history(db: Session, user: User, history_id: int) -> InterviewHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    schedule = _get_owned_schedule(db, user, history.schedule_id)
    return _history_detail_response(history, _schedule_title(schedule))


def update_history(db: Session, user: User, history_id: int, payload: InterviewHistoryUpdateRequest) -> InterviewHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    data = payload.model_dump(exclude_unset=True)
    schedule = _get_owned_schedule(db, user, history.schedule_id)
    for field, value in data.items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, _schedule_title(schedule))


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    db.delete(history)
    db.commit()


def get_dashboard(db: Session, user: User) -> InterviewSchedulerDashboardResponse:
    schedules = list_schedules(db, user)
    rounds = list_rounds(db, user)
    calendar_events = list_calendar_events(db, user)
    history = list_history(db, user)
    return InterviewSchedulerDashboardResponse(
        schedules=schedules,
        rounds=rounds,
        calendar_events=calendar_events,
        history=history,
        schedule_count=len(schedules),
        round_count=len(rounds),
        calendar_event_count=len(calendar_events),
        history_count=len(history),
        scheduled_count=sum(1 for item in schedules if item.status == "scheduled"),
        completed_count=sum(1 for item in schedules if item.status == "completed"),
    )
