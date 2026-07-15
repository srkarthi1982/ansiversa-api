from __future__ import annotations

import calendar
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.home_maintenance_planner import repository
from app.modules.home_maintenance_planner.models import MaintenanceArea, MaintenanceCategory, MaintenanceTask, MaintenanceTaskCompletion
from app.modules.home_maintenance_planner.schemas import (
    ArchiveFilter,
    CompletionRequest,
    CountItem,
    CostSummary,
    DashboardResponse,
    InsightsResponse,
    MaintenanceLookupCreateRequest,
    MaintenanceLookupResponse,
    MaintenanceLookupUpdateRequest,
    MaintenanceTaskCreateRequest,
    MaintenanceTaskDetailResponse,
    MaintenanceTaskSummaryResponse,
    MaintenanceTaskUpdateRequest,
    TaskSort,
    TaskTimeFilter,
)

DEFAULT_AREAS = [
    ("Kitchen", 10), ("Bathroom", 20), ("Bedroom", 30), ("Living room", 40), ("Balcony", 50),
    ("Garden", 60), ("Garage", 70), ("Roof", 80), ("Plumbing", 90), ("Electrical", 100),
    ("HVAC / air conditioning", 110), ("Appliances", 120), ("Doors and windows", 130), ("Exterior", 140), ("General", 150),
]
DEFAULT_CATEGORIES = [
    ("Cleaning", 10), ("Inspection", 20), ("Repair", 30), ("Replacement", 40), ("Servicing", 50),
    ("Safety check", 60), ("Pest control", 70), ("Painting", 80), ("Plumbing", 90), ("Electrical", 100),
    ("Air conditioning", 110), ("Appliance care", 120), ("Outdoor maintenance", 130), ("Other", 140),
]
PRIORITY_RANK = {"urgent": 0, "high": 1, "medium": 2, "low": 3}


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


def _decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_due_date(current_due: date, recurrence_type: str, recurrence_interval: int | None) -> date | None:
    if recurrence_type == "one_time":
        return None
    if recurrence_type == "weekly":
        return current_due.fromordinal(current_due.toordinal() + 7)
    if recurrence_type == "monthly":
        return _add_months(current_due, 1)
    if recurrence_type == "quarterly":
        return _add_months(current_due, 3)
    if recurrence_type == "six_monthly":
        return _add_months(current_due, 6)
    if recurrence_type == "yearly":
        return _add_months(current_due, 12)
    if recurrence_type == "custom" and recurrence_interval:
        return current_due.fromordinal(current_due.toordinal() + recurrence_interval)
    return None


def _status(task: MaintenanceTask, current: date | None = None) -> str:
    today = current or _today()
    if task.archived:
        return "archived"
    if task.completed_at is not None:
        return "completed"
    if task.due_date < today:
        return "overdue"
    if task.due_date == today:
        return "due_today"
    if (task.due_date - today).days <= 7:
        return "due_soon"
    return "upcoming"


def _ensure_defaults(db: Session, user: User) -> None:
    area_names = {item.name.lower() for item in repository.list_areas(db, user.id)}
    category_names = {item.name.lower() for item in repository.list_categories(db, user.id)}
    created = False
    for name, sort_order in DEFAULT_AREAS:
        if name.lower() not in area_names:
            repository.add(db, MaintenanceArea(owner_id=user.id, name=name, sort_order=sort_order, is_system=True))
            created = True
    for name, sort_order in DEFAULT_CATEGORIES:
        if name.lower() not in category_names:
            repository.add(db, MaintenanceCategory(owner_id=user.id, name=name, sort_order=sort_order, is_system=True))
            created = True
    if created:
        _commit_or_conflict(db, "Unable to prepare maintenance defaults.")


def _lookup_response(item: MaintenanceArea | MaintenanceCategory, task_count: int = 0) -> MaintenanceLookupResponse:
    return MaintenanceLookupResponse(id=item.id, name=item.name, description=item.description, sort_order=item.sort_order, is_system=item.is_system, task_count=task_count, created_at=item.created_at, updated_at=item.updated_at)


def _task_summary(task: MaintenanceTask, current: date | None = None) -> MaintenanceTaskSummaryResponse:
    today = current or _today()
    days = (task.due_date - today).days
    return MaintenanceTaskSummaryResponse(
        id=task.id,
        title=task.title,
        area_id=task.area_id,
        area_name=task.area.name,
        category_id=task.category_id,
        category_name=task.category.name,
        due_date=task.due_date,
        recurrence_type=task.recurrence_type,
        recurrence_interval=task.recurrence_interval,
        priority=task.priority,
        status=_status(task, today),
        days_remaining=days,
        due_soon=0 <= days <= task.reminder_lead_days,
        overdue=days < 0 and task.completed_at is None and not task.archived,
        estimated_cost=task.estimated_cost,
        actual_cost=task.actual_cost,
        currency=task.currency,
        provider_name=task.provider_name,
        completed_at=task.completed_at,
        archived=task.archived,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _task_detail(task: MaintenanceTask) -> MaintenanceTaskDetailResponse:
    return MaintenanceTaskDetailResponse(**_task_summary(task).model_dump(), description=task.description, provider_phone=task.provider_phone, provider_email=task.provider_email, reference_number=task.reference_number, notes=task.notes, completion_notes=task.completion_notes, reminder_lead_days=task.reminder_lead_days, completion_count=len(task.completions))


def _get_owned_area(db: Session, user: User, area_id: str) -> MaintenanceArea:
    item = repository.get_area(db, area_id)
    if not item or item.owner_id != user.id:
        _not_found("Maintenance area")
    return item


def _get_owned_category(db: Session, user: User, category_id: str) -> MaintenanceCategory:
    item = repository.get_category(db, category_id)
    if not item or item.owner_id != user.id:
        _not_found("Maintenance category")
    return item


def _get_owned_task(db: Session, user: User, task_id: str) -> MaintenanceTask:
    item = repository.get_task(db, task_id)
    if not item or item.owner_id != user.id:
        _not_found("Maintenance task")
    return item


def list_areas(db: Session, user: User) -> list[MaintenanceLookupResponse]:
    _ensure_defaults(db, user)
    counts = repository.task_counts_by_area(db, user.id)
    return [_lookup_response(item, counts.get(item.id, 0)) for item in repository.list_areas(db, user.id)]


def create_area(db: Session, user: User, payload: MaintenanceLookupCreateRequest) -> MaintenanceLookupResponse:
    item = MaintenanceArea(owner_id=user.id, name=payload.name, description=payload.description, sort_order=payload.sort_order)
    repository.add(db, item)
    _commit_or_conflict(db, "A maintenance area with this name already exists.")
    db.refresh(item)
    return _lookup_response(item)


def update_area(db: Session, user: User, area_id: str, payload: MaintenanceLookupUpdateRequest) -> MaintenanceLookupResponse:
    item = _get_owned_area(db, user, area_id)
    item.name = payload.name
    item.description = payload.description
    item.sort_order = payload.sort_order
    _commit_or_conflict(db, "A maintenance area with this name already exists.")
    db.refresh(item)
    return _lookup_response(item, repository.count_tasks_for_area(db, user.id, item.id))


def delete_area(db: Session, user: User, area_id: str) -> None:
    item = _get_owned_area(db, user, area_id)
    if repository.count_tasks_for_area(db, user.id, item.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Maintenance area has tasks. Reassign or delete tasks first.")
    repository.delete_record(db, item)
    db.commit()


def list_categories(db: Session, user: User) -> list[MaintenanceLookupResponse]:
    _ensure_defaults(db, user)
    counts = repository.task_counts_by_category(db, user.id)
    return [_lookup_response(item, counts.get(item.id, 0)) for item in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: MaintenanceLookupCreateRequest) -> MaintenanceLookupResponse:
    item = MaintenanceCategory(owner_id=user.id, name=payload.name, description=payload.description, sort_order=payload.sort_order)
    repository.add(db, item)
    _commit_or_conflict(db, "A maintenance category with this name already exists.")
    db.refresh(item)
    return _lookup_response(item)


def update_category(db: Session, user: User, category_id: str, payload: MaintenanceLookupUpdateRequest) -> MaintenanceLookupResponse:
    item = _get_owned_category(db, user, category_id)
    item.name = payload.name
    item.description = payload.description
    item.sort_order = payload.sort_order
    _commit_or_conflict(db, "A maintenance category with this name already exists.")
    db.refresh(item)
    return _lookup_response(item, repository.count_tasks_for_category(db, user.id, item.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    item = _get_owned_category(db, user, category_id)
    if repository.count_tasks_for_category(db, user.id, item.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Maintenance category has tasks. Reassign or delete tasks first.")
    repository.delete_record(db, item)
    db.commit()


def _apply_task_payload(task: MaintenanceTask, payload: MaintenanceTaskCreateRequest | MaintenanceTaskUpdateRequest) -> None:
    task.title = payload.title
    task.area_id = payload.area_id
    task.category_id = payload.category_id
    task.description = payload.description
    task.due_date = payload.due_date
    task.recurrence_type = payload.recurrence_type
    task.recurrence_interval = payload.recurrence_interval
    task.priority = payload.priority
    task.estimated_cost = payload.estimated_cost
    task.actual_cost = payload.actual_cost
    task.currency = payload.currency
    task.provider_name = payload.provider_name
    task.provider_phone = payload.provider_phone
    task.provider_email = str(payload.provider_email) if payload.provider_email else None
    task.reference_number = payload.reference_number
    task.notes = payload.notes
    task.completion_notes = payload.completion_notes
    task.reminder_lead_days = payload.reminder_lead_days
    task.archived = payload.archived


def list_tasks(db: Session, user: User, query: str | None = None, archive_filter: ArchiveFilter = "active", area_id: str | None = None, category_id: str | None = None, priority: str | None = None, time_filter: TaskTimeFilter = "all", sort_by: TaskSort = "due") -> list[MaintenanceTaskSummaryResponse]:
    _ensure_defaults(db, user)
    tasks = repository.list_tasks(db, user.id)
    current = _today()
    term = (query or "").strip().lower()
    result: list[MaintenanceTask] = []
    for task in tasks:
        summary = _task_summary(task, current)
        if archive_filter == "active" and task.archived:
            continue
        if archive_filter == "archived" and not task.archived:
            continue
        if area_id and task.area_id != area_id:
            continue
        if category_id and task.category_id != category_id:
            continue
        if priority and task.priority != priority:
            continue
        if term and not any(term in value.lower() for value in [task.title, task.description or "", task.area.name, task.category.name, task.provider_name or "", task.reference_number or "", task.notes or ""]):
            continue
        if time_filter == "today" and summary.days_remaining != 0:
            continue
        if time_filter == "week" and not 0 <= summary.days_remaining <= 7:
            continue
        if time_filter == "month" and task.due_date.month != current.month:
            continue
        if time_filter == "overdue" and not summary.overdue:
            continue
        if time_filter == "completed" and summary.status != "completed":
            continue
        result.append(task)
    if sort_by == "priority":
        result.sort(key=lambda item: (PRIORITY_RANK.get(item.priority, 9), item.due_date, item.title.lower()))
    elif sort_by == "title":
        result.sort(key=lambda item: item.title.lower())
    elif sort_by == "created":
        result.sort(key=lambda item: item.created_at, reverse=True)
    elif sort_by == "updated":
        result.sort(key=lambda item: item.updated_at, reverse=True)
    elif sort_by == "cost":
        result.sort(key=lambda item: _decimal(item.estimated_cost), reverse=True)
    else:
        result.sort(key=lambda item: (item.due_date, PRIORITY_RANK.get(item.priority, 9), item.title.lower()))
    return [_task_summary(item, current) for item in result]


def create_task(db: Session, user: User, payload: MaintenanceTaskCreateRequest) -> MaintenanceTaskDetailResponse:
    _get_owned_area(db, user, payload.area_id)
    _get_owned_category(db, user, payload.category_id)
    task = MaintenanceTask(owner_id=user.id, area_id=payload.area_id, category_id=payload.category_id, title=payload.title, due_date=payload.due_date)
    _apply_task_payload(task, payload)
    repository.add(db, task)
    _commit_or_conflict(db, "Unable to create maintenance task.")
    db.refresh(task)
    return _task_detail(_get_owned_task(db, user, task.id))


def get_task(db: Session, user: User, task_id: str) -> MaintenanceTaskDetailResponse:
    return _task_detail(_get_owned_task(db, user, task_id))


def update_task(db: Session, user: User, task_id: str, payload: MaintenanceTaskUpdateRequest) -> MaintenanceTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    _get_owned_area(db, user, payload.area_id)
    _get_owned_category(db, user, payload.category_id)
    _apply_task_payload(task, payload)
    _commit_or_conflict(db, "Unable to update maintenance task.")
    db.refresh(task)
    return _task_detail(_get_owned_task(db, user, task.id))


def complete_task(db: Session, user: User, task_id: str, payload: CompletionRequest) -> MaintenanceTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    if task.completed_at is not None:
        return _task_detail(task)
    now = datetime.now(timezone.utc)
    repository.add(db, MaintenanceTaskCompletion(owner_id=user.id, task_id=task.id, completed_due_date=task.due_date, completed_at=now, actual_cost=payload.actual_cost, notes=payload.completion_notes))
    if payload.actual_cost is not None:
        task.actual_cost = payload.actual_cost
    if payload.completion_notes is not None:
        task.completion_notes = payload.completion_notes
    next_due = next_due_date(task.due_date, task.recurrence_type, task.recurrence_interval)
    if next_due is None:
        task.completed_at = now
    else:
        task.due_date = next_due
        task.completed_at = None
    _commit_or_conflict(db, "Unable to complete maintenance task.")
    return _task_detail(_get_owned_task(db, user, task.id))


def reopen_task(db: Session, user: User, task_id: str) -> MaintenanceTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    task.completed_at = None
    db.commit()
    db.refresh(task)
    return _task_detail(_get_owned_task(db, user, task.id))


def set_task_archived(db: Session, user: User, task_id: str, archived: bool) -> MaintenanceTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    task.archived = archived
    db.commit()
    db.refresh(task)
    return _task_detail(_get_owned_task(db, user, task.id))


def delete_task(db: Session, user: User, task_id: str) -> None:
    task = _get_owned_task(db, user, task_id)
    repository.delete_record(db, task)
    db.commit()


def _active_tasks(db: Session, user: User) -> list[MaintenanceTask]:
    return [item for item in repository.list_tasks(db, user.id) if not item.archived]


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    _ensure_defaults(db, user)
    current = _today()
    tasks = _active_tasks(db, user)
    summaries = [_task_summary(item, current) for item in tasks]
    completions = repository.list_completions(db, user.id)
    return DashboardResponse(
        total_active_tasks=sum(1 for item in tasks if item.completed_at is None),
        due_today=sum(1 for item in summaries if item.days_remaining == 0 and item.status != "completed"),
        due_this_week=sum(1 for item in summaries if 0 <= item.days_remaining <= 7 and item.status != "completed"),
        overdue_tasks=sum(1 for item in summaries if item.overdue),
        completed_this_month=sum(1 for item in completions if item.completed_at.year == current.year and item.completed_at.month == current.month),
        upcoming_tasks=sum(1 for item in summaries if item.status in {"upcoming", "due_soon", "due_today"}),
        archived_tasks=sum(1 for item in repository.list_tasks(db, user.id) if item.archived),
        estimated_total=sum((_decimal(item.estimated_cost) for item in tasks), Decimal("0.00")),
        actual_total=sum((_decimal(item.actual_cost) for item in tasks), Decimal("0.00")),
    )


def get_insights(db: Session, user: User) -> InsightsResponse:
    current = _today()
    tasks = _active_tasks(db, user)
    summaries = [_task_summary(item, current) for item in tasks]
    dashboard = get_dashboard(db, user)
    by_area = Counter(item.area.name for item in tasks)
    by_category = Counter(item.category.name for item in tasks)
    by_priority = Counter(item.priority for item in tasks)
    completed = [item for item in tasks if item.completed_at is not None]
    return InsightsResponse(
        **dashboard.model_dump(),
        areas=list_areas(db, user),
        categories=list_categories(db, user),
        tasks_by_area=[CountItem(label=label, count=count) for label, count in by_area.most_common()],
        tasks_by_category=[CountItem(label=label, count=count) for label, count in by_category.most_common()],
        tasks_by_priority=[CountItem(label=label.title(), count=count) for label, count in by_priority.most_common()],
        cost_summary=CostSummary(estimated_total=dashboard.estimated_total, actual_total=dashboard.actual_total, currency=(tasks[0].currency if tasks else "USD")),
        recently_completed=[_task_summary(item, current) for item in sorted(completed, key=lambda item: item.completed_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[:8]],
        upcoming=[item for item in sorted(summaries, key=lambda item: item.days_remaining) if item.status in {"upcoming", "due_soon", "due_today"}][:12],
        overdue=[item for item in sorted(summaries, key=lambda item: item.days_remaining) if item.overdue][:12],
    )

