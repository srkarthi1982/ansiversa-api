from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.water_intake_tracker import repository
from app.modules.water_intake_tracker.models import WaterEntry, WaterGoal
from app.modules.water_intake_tracker.schemas import AmountItem, DashboardResponse, DaySummary, EntryCreateRequest, EntryDetailResponse, EntryListResponse, EntrySort, EntrySummaryResponse, EntryUpdateRequest, GoalRequest, GoalResponse, InsightsResponse, SummaryRange

DEFAULT_DRINK_TYPES = ['Water', 'Sparkling Water', 'Electrolyte Drink', 'Coconut Water', 'Other']
DEFAULT_GOAL = Decimal('2000.00')


def _today() -> date:
    return date.today()


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{resource} was not found.')


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _decimal(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _to_ml(amount, unit: str) -> Decimal:
    value = _decimal(amount)
    return (value * Decimal('1000.00')).quantize(Decimal('0.01')) if unit == 'L' else value


def _from_ml(amount_ml: Decimal, unit: str) -> Decimal:
    amount = _decimal(amount_ml)
    return (amount / Decimal('1000.00')).quantize(Decimal('0.01')) if unit == 'L' else amount


def _percent(total_ml: Decimal, goal_ml: Decimal) -> float:
    if goal_ml <= 0:
        return 0.0
    return float(min((total_ml / goal_ml * Decimal('100')).quantize(Decimal('0.1')), Decimal('999.9')))


def ensure_goal(db: Session, user: User) -> WaterGoal:
    goal = repository.get_goal(db, user.id)
    if goal:
        return goal
    goal = WaterGoal(owner_id=user.id, daily_goal=DEFAULT_GOAL, preferred_unit='ml')
    repository.add(db, goal)
    _commit_or_conflict(db, 'Unable to prepare water intake goal.')
    db.refresh(goal)
    return goal


def _goal_response(goal: WaterGoal) -> GoalResponse:
    return GoalResponse(id=goal.id, daily_goal=goal.daily_goal, preferred_unit=goal.preferred_unit, daily_goal_ml=_to_ml(goal.daily_goal, goal.preferred_unit), created_at=goal.created_at, updated_at=goal.updated_at)


def get_goal(db: Session, user: User) -> GoalResponse:
    return _goal_response(ensure_goal(db, user))


def update_goal(db: Session, user: User, payload: GoalRequest) -> GoalResponse:
    goal = ensure_goal(db, user)
    goal.daily_goal = payload.daily_goal
    goal.preferred_unit = payload.preferred_unit
    _commit_or_conflict(db, 'Unable to save water intake goal.')
    db.refresh(goal)
    return _goal_response(goal)


def _entry_summary(item: WaterEntry) -> EntrySummaryResponse:
    notes_preview = item.notes[:140] if item.notes else None
    return EntrySummaryResponse(id=item.id, entry_date=item.entry_date, entry_time=item.entry_time, amount=item.amount, unit=item.unit, amount_ml=_to_ml(item.amount, item.unit), drink_type=item.drink_type, notes_preview=notes_preview, created_at=item.created_at, updated_at=item.updated_at)


def _entry_detail(item: WaterEntry) -> EntryDetailResponse:
    return EntryDetailResponse(**_entry_summary(item).model_dump(), notes=item.notes)


def _get_owned_entry(db: Session, user: User, entry_id: str) -> WaterEntry:
    item = repository.get_entry(db, entry_id)
    if not item or item.owner_id != user.id:
        _not_found('Water entry')
    return item


def _apply_entry_payload(item: WaterEntry, payload: EntryCreateRequest | EntryUpdateRequest) -> None:
    item.entry_date = payload.entry_date
    item.entry_time = payload.entry_time
    item.amount = payload.amount
    item.unit = payload.unit
    item.drink_type = payload.drink_type or 'Water'
    item.notes = payload.notes


def list_entries(db: Session, user: User, query: str | None = None, date_from: date | None = None, date_to: date | None = None, drink_type: str | None = None, sort_by: EntrySort = 'date', page: int = 1, page_size: int = 25) -> EntryListResponse:
    ensure_goal(db, user)
    term = (query or '').strip().lower()
    drink = (drink_type or '').strip().lower()
    result: list[WaterEntry] = []
    for item in repository.list_entries(db, user.id):
        if date_from and item.entry_date < date_from:
            continue
        if date_to and item.entry_date > date_to:
            continue
        if drink and item.drink_type.lower() != drink:
            continue
        if term and term not in item.drink_type.lower() and term not in (item.notes or '').lower():
            continue
        result.append(item)
    if sort_by == 'amount':
        result.sort(key=lambda item: _to_ml(item.amount, item.unit), reverse=True)
    elif sort_by == 'drink_type':
        result.sort(key=lambda item: (item.drink_type.lower(), item.entry_date, item.entry_time))
    elif sort_by == 'created':
        result.sort(key=lambda item: item.created_at, reverse=True)
    else:
        result.sort(key=lambda item: (item.entry_date, item.entry_time, item.created_at), reverse=True)
    total = len(result)
    start = (page - 1) * page_size
    return EntryListResponse(items=[_entry_summary(item) for item in result[start:start + page_size]], total=total, page=page, page_size=page_size)


def create_entry(db: Session, user: User, payload: EntryCreateRequest) -> EntryDetailResponse:
    ensure_goal(db, user)
    item = WaterEntry(owner_id=user.id, entry_date=payload.entry_date, entry_time=payload.entry_time, amount=payload.amount, unit=payload.unit, drink_type=payload.drink_type or 'Water', notes=payload.notes)
    repository.add(db, item)
    _commit_or_conflict(db, 'Unable to create water entry.')
    db.refresh(item)
    return _entry_detail(item)


def get_entry(db: Session, user: User, entry_id: str) -> EntryDetailResponse:
    return _entry_detail(_get_owned_entry(db, user, entry_id))


def update_entry(db: Session, user: User, entry_id: str, payload: EntryUpdateRequest) -> EntryDetailResponse:
    item = _get_owned_entry(db, user, entry_id)
    _apply_entry_payload(item, payload)
    _commit_or_conflict(db, 'Unable to update water entry.')
    db.refresh(item)
    return _entry_detail(item)


def delete_entry(db: Session, user: User, entry_id: str) -> None:
    item = _get_owned_entry(db, user, entry_id)
    repository.delete_record(db, item)
    db.commit()


def _daily_totals(entries: list[WaterEntry]) -> dict[date, Decimal]:
    totals: dict[date, Decimal] = defaultdict(lambda: Decimal('0.00'))
    for item in entries:
        totals[item.entry_date] += _to_ml(item.amount, item.unit)
    return dict(totals)


def _day_summaries(entries: list[WaterEntry], goal_ml: Decimal) -> list[DaySummary]:
    totals = _daily_totals(entries)
    counts = Counter(item.entry_date for item in entries)
    return [DaySummary(date=day, total_amount=_decimal(total), entry_count=counts[day], goal_achieved=total >= goal_ml) for day, total in sorted(totals.items(), reverse=True)]


def _average_for_days(entries: list[WaterEntry], days: int) -> Decimal:
    if days <= 0:
        return Decimal('0.00')
    total = sum((_to_ml(item.amount, item.unit) for item in entries), Decimal('0.00'))
    return _decimal(total / Decimal(days))


def _current_streak(entries: list[WaterEntry], goal_ml: Decimal, current: date) -> int:
    totals = _daily_totals(entries)
    streak = 0
    cursor = current
    while totals.get(cursor, Decimal('0.00')) >= goal_ml:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    goal = ensure_goal(db, user)
    goal_response = _goal_response(goal)
    goal_ml = goal_response.daily_goal_ml
    today = _today()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)
    entries = repository.list_entries_between(db, user.id, month_start, today)
    today_entries = [item for item in entries if item.entry_date == today]
    week_entries = [item for item in entries if item.entry_date >= week_start]
    todays_ml = sum((_to_ml(item.amount, item.unit) for item in today_entries), Decimal('0.00'))
    remaining_ml = max(goal_ml - todays_ml, Decimal('0.00'))
    return DashboardResponse(goal=goal_response, todays_intake=_from_ml(todays_ml, goal.preferred_unit), remaining_amount=_from_ml(remaining_ml, goal.preferred_unit), completion_percent=_percent(todays_ml, goal_ml), goal_achieved=todays_ml >= goal_ml, entries_today=len(today_entries), weekly_average=_from_ml(_average_for_days(week_entries, 7), goal.preferred_unit), monthly_average=_from_ml(_average_for_days(entries, 30), goal.preferred_unit), current_streak=_current_streak(entries, goal_ml, today))


def get_insights(db: Session, user: User) -> InsightsResponse:
    dashboard = get_dashboard(db, user)
    goal = ensure_goal(db, user)
    today = _today()
    month_start = today - timedelta(days=29)
    entries = repository.list_entries_between(db, user.id, month_start, today)
    goal_ml = dashboard.goal.daily_goal_ml
    summaries = _day_summaries(entries, goal_ml)
    best = max(summaries, key=lambda item: item.total_amount, default=None)
    by_type: dict[str, Decimal] = defaultdict(lambda: Decimal('0.00'))
    counts = Counter()
    by_week: dict[str, Decimal] = defaultdict(lambda: Decimal('0.00'))
    for item in entries:
        amount_ml = _to_ml(item.amount, item.unit)
        by_type[item.drink_type] += amount_ml
        counts[item.drink_type] += 1
        iso = item.entry_date.isocalendar()
        by_week[f'{iso.year}-W{iso.week:02d}'] += amount_ml
    recent = sorted(entries, key=lambda item: (item.entry_date, item.entry_time, item.created_at), reverse=True)[:8]
    drink_types = sorted(set(DEFAULT_DRINK_TYPES) | set(by_type.keys()))
    return InsightsResponse(**dashboard.model_dump(), best_hydration_day=best, intake_trend_by_week=[AmountItem(label=label, amount=_from_ml(amount, goal.preferred_unit)) for label, amount in sorted(by_week.items())], intake_by_drink_type=[AmountItem(label=label, amount=_from_ml(amount, goal.preferred_unit), count=counts[label]) for label, amount in sorted(by_type.items(), key=lambda row: row[1], reverse=True)], recent_entries=[_entry_summary(item) for item in recent], weekly_summaries=summaries[:7], monthly_summaries=summaries, drink_types=drink_types)


def get_summary(db: Session, user: User, range_name: SummaryRange) -> list[DaySummary]:
    goal = ensure_goal(db, user)
    today = _today()
    days = 7 if range_name == 'week' else 30
    start = today - timedelta(days=days - 1)
    return _day_summaries(repository.list_entries_between(db, user.id, start, today), _to_ml(goal.daily_goal, goal.preferred_unit))


def list_drink_types(db: Session, user: User) -> list[str]:
    ensure_goal(db, user)
    entries = repository.list_entries(db, user.id)
    return sorted(set(DEFAULT_DRINK_TYPES) | {item.drink_type for item in entries})
