from __future__ import annotations

import calendar
from collections import Counter
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.birthday_and_anniversary_reminder import repository
from app.modules.birthday_and_anniversary_reminder.models import ReminderAcknowledgement, ReminderContact, ReminderType
from app.modules.birthday_and_anniversary_reminder.schemas import (
    ArchiveFilter,
    CountItem,
    DashboardResponse,
    FavouriteFilter,
    InsightsResponse,
    ReminderCreateRequest,
    ReminderDetailResponse,
    ReminderSort,
    ReminderSummaryResponse,
    ReminderTypeCreateRequest,
    ReminderTypeResponse,
    ReminderTypeUpdateRequest,
    ReminderUpdateRequest,
    TimeFilter,
)

DEFAULT_TYPES = [
    ("Birthday", 10),
    ("Wedding Anniversary", 20),
    ("Engagement Anniversary", 30),
    ("Work Anniversary", 40),
    ("Graduation", 50),
    ("Child Birthday", 60),
    ("Other", 70),
]


def _today() -> date:
    return date.today()


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    return normalized if len(normalized) <= 140 else f"{normalized[:137]}..."


def _annual_date(event_date: date, year: int) -> date:
    day = min(event_date.day, calendar.monthrange(year, event_date.month)[1])
    return date(year, event_date.month, day)


def next_occurrence(event_date: date, today: date | None = None) -> date:
    current = today or _today()
    occurrence = _annual_date(event_date, current.year)
    if occurrence < current:
        occurrence = _annual_date(event_date, current.year + 1)
    return occurrence


def days_remaining(event_date: date, today: date | None = None) -> int:
    current = today or _today()
    return (next_occurrence(event_date, current) - current).days


def ensure_default_types(db: Session, user: User) -> None:
    existing_names = {item.name.lower() for item in repository.list_types(db, user.id)}
    created = False
    for name, sort_order in DEFAULT_TYPES:
        if name.lower() in existing_names:
            continue
        repository.add(db, ReminderType(owner_id=user.id, name=name, sort_order=sort_order, is_system=True))
        created = True
    if created:
        _commit_or_conflict(db, "Unable to prepare reminder types.")


def _get_owned_type(db: Session, user: User, type_id: str) -> ReminderType:
    item = repository.get_type(db, type_id)
    if not item or item.owner_id != user.id:
        _not_found("Reminder type")
    return item


def _get_owned_reminder(db: Session, user: User, reminder_id: str) -> ReminderContact:
    reminder = repository.get_reminder(db, reminder_id)
    if not reminder or reminder.owner_id != user.id:
        _not_found("Reminder")
    return reminder


def _is_acknowledged(reminder: ReminderContact, year: int) -> bool:
    return any(item.acknowledgement_year == year for item in reminder.acknowledgements)


def _missed_this_year(reminder: ReminderContact, today: date) -> bool:
    occurrence = _annual_date(reminder.event_date, today.year)
    return occurrence < today and not _is_acknowledged(reminder, today.year)


def _type_response(item: ReminderType, reminder_count: int = 0) -> ReminderTypeResponse:
    return ReminderTypeResponse(id=item.id, name=item.name, sort_order=item.sort_order, is_system=item.is_system, reminder_count=reminder_count, created_at=item.created_at, updated_at=item.updated_at)


def _reminder_summary(reminder: ReminderContact, today: date | None = None) -> ReminderSummaryResponse:
    current = today or _today()
    upcoming = next_occurrence(reminder.event_date, current)
    return ReminderSummaryResponse(
        id=reminder.id,
        person_name=reminder.person_name,
        reminder_type_id=reminder.reminder_type_id,
        reminder_type_name=reminder.reminder_type.name,
        relationship=reminder.relationship,
        event_date=reminder.event_date,
        next_occurrence=upcoming,
        days_remaining=(upcoming - current).days,
        phone=reminder.phone,
        email=reminder.email,
        favourite=reminder.favourite,
        archived=reminder.archived,
        acknowledged_this_year=_is_acknowledged(reminder, current.year),
        missed_this_year=_missed_this_year(reminder, current),
        gift_preview=_preview(reminder.gift_ideas),
        notes_preview=_preview(reminder.notes),
        created_at=reminder.created_at,
        updated_at=reminder.updated_at,
    )


def _reminder_detail(reminder: ReminderContact) -> ReminderDetailResponse:
    return ReminderDetailResponse(**_reminder_summary(reminder).model_dump(), gift_ideas=reminder.gift_ideas, notes=reminder.notes)


def _apply_reminder_payload(reminder: ReminderContact, payload: ReminderCreateRequest | ReminderUpdateRequest) -> None:
    reminder.person_name = payload.person_name
    reminder.reminder_type_id = payload.reminder_type_id
    reminder.relationship = payload.relationship
    reminder.event_date = payload.event_date
    reminder.phone = payload.phone
    reminder.email = str(payload.email) if payload.email else None
    reminder.gift_ideas = payload.gift_ideas
    reminder.notes = payload.notes
    reminder.favourite = payload.favourite
    reminder.archived = payload.archived


def list_types(db: Session, user: User) -> list[ReminderTypeResponse]:
    ensure_default_types(db, user)
    counts = repository.reminder_counts_by_type(db, user.id)
    return [_type_response(item, counts.get(item.id, 0)) for item in repository.list_types(db, user.id)]


def create_type(db: Session, user: User, payload: ReminderTypeCreateRequest) -> ReminderTypeResponse:
    item = ReminderType(owner_id=user.id, name=payload.name, sort_order=payload.sort_order)
    repository.add(db, item)
    _commit_or_conflict(db, "A reminder type with this name already exists.")
    db.refresh(item)
    return _type_response(item)


def update_type(db: Session, user: User, type_id: str, payload: ReminderTypeUpdateRequest) -> ReminderTypeResponse:
    item = _get_owned_type(db, user, type_id)
    item.name = payload.name
    item.sort_order = payload.sort_order
    _commit_or_conflict(db, "A reminder type with this name already exists.")
    db.refresh(item)
    return _type_response(item, repository.count_reminders_for_type(db, user.id, item.id))


def delete_type(db: Session, user: User, type_id: str) -> None:
    item = _get_owned_type(db, user, type_id)
    if repository.count_reminders_for_type(db, user.id, item.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reminder type has reminders. Reassign or delete reminders first.")
    repository.delete_record(db, item)
    db.commit()


def _filter_reminders(reminders: list[ReminderContact], query: str | None, archive_filter: ArchiveFilter, favourite_filter: FavouriteFilter, type_id: str | None, time_filter: TimeFilter) -> list[ReminderContact]:
    current = _today()
    term = (query or "").strip().lower()
    type_filter = (type_id or "").strip()
    result: list[ReminderContact] = []
    for reminder in reminders:
        summary = _reminder_summary(reminder, current)
        if archive_filter == "active" and reminder.archived:
            continue
        if archive_filter == "archived" and not reminder.archived:
            continue
        if favourite_filter == "favourites" and not reminder.favourite:
            continue
        if type_filter and reminder.reminder_type_id != type_filter:
            continue
        if term and not any(term in value.lower() for value in [reminder.person_name, reminder.relationship or "", reminder.reminder_type.name, reminder.phone or "", reminder.email or "", reminder.gift_ideas or "", reminder.notes or ""]):
            continue
        if time_filter == "today" and summary.days_remaining != 0:
            continue
        if time_filter == "week" and summary.days_remaining > 7:
            continue
        if time_filter == "month" and summary.next_occurrence.month != current.month:
            continue
        if time_filter == "next30" and summary.days_remaining > 30:
            continue
        if time_filter == "missed" and not summary.missed_this_year:
            continue
        if time_filter == "acknowledged" and not summary.acknowledged_this_year:
            continue
        result.append(reminder)
    return result


def _sort_reminders(reminders: list[ReminderContact], sort_by: ReminderSort) -> list[ReminderContact]:
    current = _today()
    if sort_by == "name":
        return sorted(reminders, key=lambda item: item.person_name.lower())
    if sort_by == "type":
        return sorted(reminders, key=lambda item: (item.reminder_type.sort_order, item.person_name.lower()))
    if sort_by == "created":
        return sorted(reminders, key=lambda item: item.created_at, reverse=True)
    return sorted(reminders, key=lambda item: (days_remaining(item.event_date, current), item.person_name.lower()))


def list_reminders(db: Session, user: User, query: str | None = None, archive_filter: ArchiveFilter = "active", favourite_filter: FavouriteFilter = "all", type_id: str | None = None, time_filter: TimeFilter = "all", sort_by: ReminderSort = "upcoming") -> list[ReminderSummaryResponse]:
    ensure_default_types(db, user)
    reminders = repository.list_reminders(db, user.id)
    filtered = _filter_reminders(reminders, query, archive_filter, favourite_filter, type_id, time_filter)
    return [_reminder_summary(item) for item in _sort_reminders(filtered, sort_by)]


def create_reminder(db: Session, user: User, payload: ReminderCreateRequest) -> ReminderDetailResponse:
    reminder_type = _get_owned_type(db, user, payload.reminder_type_id)
    reminder = ReminderContact(owner_id=user.id, reminder_type_id=reminder_type.id, person_name=payload.person_name, event_date=payload.event_date)
    _apply_reminder_payload(reminder, payload)
    repository.add(db, reminder)
    _commit_or_conflict(db, "Unable to create reminder.")
    db.refresh(reminder)
    reminder.reminder_type = reminder_type
    return _reminder_detail(reminder)


def get_reminder(db: Session, user: User, reminder_id: str) -> ReminderDetailResponse:
    return _reminder_detail(_get_owned_reminder(db, user, reminder_id))


def update_reminder(db: Session, user: User, reminder_id: str, payload: ReminderUpdateRequest) -> ReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    reminder_type = _get_owned_type(db, user, payload.reminder_type_id)
    _apply_reminder_payload(reminder, payload)
    _commit_or_conflict(db, "Unable to update reminder.")
    db.refresh(reminder)
    reminder.reminder_type = reminder_type
    return _reminder_detail(reminder)


def set_reminder_archived(db: Session, user: User, reminder_id: str, archived: bool) -> ReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    reminder.archived = archived
    db.commit()
    db.refresh(reminder)
    return _reminder_detail(reminder)


def set_reminder_favourite(db: Session, user: User, reminder_id: str, favourite: bool) -> ReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    reminder.favourite = favourite
    db.commit()
    db.refresh(reminder)
    return _reminder_detail(reminder)


def acknowledge_reminder(db: Session, user: User, reminder_id: str) -> ReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    year = _today().year
    if repository.get_acknowledgement(db, user.id, reminder.id, year) is None:
        repository.add(db, ReminderAcknowledgement(owner_id=user.id, reminder_contact_id=reminder.id, acknowledgement_year=year, acknowledged_at=datetime.now(timezone.utc)))
        _commit_or_conflict(db, "Unable to acknowledge reminder.")
    db.refresh(reminder)
    return _reminder_detail(_get_owned_reminder(db, user, reminder.id))


def delete_reminder(db: Session, user: User, reminder_id: str) -> None:
    reminder = _get_owned_reminder(db, user, reminder_id)
    repository.delete_record(db, reminder)
    db.commit()


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    ensure_default_types(db, user)
    current = _today()
    reminders = [item for item in repository.list_reminders(db, user.id) if not item.archived]
    summaries = [_reminder_summary(item, current) for item in reminders]
    return DashboardResponse(
        total_reminders=len(reminders),
        birthdays=sum(1 for item in reminders if "birthday" in item.reminder_type.name.lower()),
        anniversaries=sum(1 for item in reminders if "anniversary" in item.reminder_type.name.lower()),
        today=sum(1 for item in summaries if item.days_remaining == 0),
        this_week=sum(1 for item in summaries if item.days_remaining <= 7),
        this_month=sum(1 for item in summaries if item.next_occurrence.month == current.month),
        next_30_days=sum(1 for item in summaries if item.days_remaining <= 30),
        missed_this_year=sum(1 for item in summaries if item.missed_this_year),
        acknowledged_this_year=sum(1 for item in summaries if item.acknowledged_this_year),
        favourites=sum(1 for item in reminders if item.favourite),
    )


def get_insights(db: Session, user: User) -> InsightsResponse:
    current = _today()
    reminders = [item for item in repository.list_reminders(db, user.id) if not item.archived]
    summaries = [_reminder_summary(item, current) for item in reminders]
    monthly = Counter(calendar.month_name[item.event_date.month] for item in reminders)
    type_counts = Counter(item.reminder_type.name for item in reminders)
    dashboard = get_dashboard(db, user)
    return InsightsResponse(
        **dashboard.model_dump(),
        types=list_types(db, user),
        monthly_distribution=[CountItem(label=label, count=count) for label, count in monthly.items()],
        type_distribution=[CountItem(label=label, count=count) for label, count in type_counts.most_common(10)],
        favourite_reminders=[_reminder_summary(item, current) for item in reminders if item.favourite][:8],
        recently_added=[_reminder_summary(item, current) for item in sorted(reminders, key=lambda item: item.created_at, reverse=True)[:8]],
        upcoming_next_30=[item for item in sorted(summaries, key=lambda item: item.days_remaining) if item.days_remaining <= 30][:12],
    )
