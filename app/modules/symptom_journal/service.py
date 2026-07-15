from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.symptom_journal import repository
from app.modules.symptom_journal.models import SymptomCategory, SymptomEntry
from app.modules.symptom_journal.schemas import ArchiveFilter, CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest, CountItem, DashboardResponse, EntryCreateRequest, EntryDetailResponse, EntryListResponse, EntrySort, EntrySummaryResponse, EntryUpdateRequest, InsightsResponse, RecurringSymptomItem, SeverityFilter

DEFAULT_CATEGORIES = [
    ("Headache", 10),
    ("Fever", 20),
    ("Cough", 30),
    ("Cold", 40),
    ("Fatigue", 50),
    ("Digestive", 60),
    ("Allergy", 70),
    ("Skin", 80),
    ("Pain", 90),
    ("Sleep", 100),
    ("Mental wellbeing", 110),
    ("Other", 120),
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


def _severity_label(value: int) -> str:
    if value <= 3:
        return "mild"
    if value <= 6:
        return "moderate"
    return "severe"


def _decimal_or_none(value) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"))


def ensure_default_categories(db: Session, user: User) -> None:
    existing = {item.name.lower() for item in repository.list_categories(db, user.id)}
    created = False
    for name, order in DEFAULT_CATEGORIES:
        if name.lower() not in existing:
            repository.add(db, SymptomCategory(owner_id=user.id, name=name, sort_order=order, is_system=True))
            created = True
    if created:
        _commit_or_conflict(db, "Unable to prepare symptom categories.")


def _get_owned_category(db: Session, user: User, category_id: str) -> SymptomCategory:
    item = repository.get_category(db, category_id)
    if not item or item.owner_id != user.id:
        _not_found("Symptom category")
    return item


def _get_owned_entry(db: Session, user: User, entry_id: str) -> SymptomEntry:
    item = repository.get_entry(db, entry_id)
    if not item or item.owner_id != user.id:
        _not_found("Symptom entry")
    return item


def _category_response(item: SymptomCategory, counts: dict[str, int] | None = None) -> CategoryResponse:
    counts = counts or {}
    return CategoryResponse(id=item.id, name=item.name, description=item.description, sort_order=item.sort_order, is_system=item.is_system, entry_count=counts.get(item.id, 0), created_at=item.created_at, updated_at=item.updated_at)


def _entry_summary(item: SymptomEntry) -> EntrySummaryResponse:
    return EntrySummaryResponse(id=item.id, category_id=item.category_id, category_name=item.category.name if item.category else None, entry_date=item.entry_date, entry_time=item.entry_time, symptom_title=item.symptom_title, severity=item.severity, severity_label=_severity_label(item.severity), duration=item.duration, body_location=item.body_location, mood=item.mood, temperature=item.temperature, archived=item.archived, created_at=item.created_at, updated_at=item.updated_at)


def _entry_detail(item: SymptomEntry) -> EntryDetailResponse:
    summary = _entry_summary(item).model_dump()
    return EntryDetailResponse(**summary, triggers=item.triggers, relief_methods=item.relief_methods, follow_up_notes=item.follow_up_notes, notes=item.notes)


def list_categories(db: Session, user: User) -> list[CategoryResponse]:
    ensure_default_categories(db, user)
    counts = repository.entry_counts_by_category(db, user.id)
    return [_category_response(item, counts) for item in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: CategoryCreateRequest) -> CategoryResponse:
    item = SymptomCategory(owner_id=user.id, name=payload.name, description=payload.description, sort_order=payload.sort_order, is_system=False)
    repository.add(db, item)
    _commit_or_conflict(db, "A symptom category with this name already exists.")
    db.refresh(item)
    return _category_response(item)


def update_category(db: Session, user: User, category_id: str, payload: CategoryUpdateRequest) -> CategoryResponse:
    item = _get_owned_category(db, user, category_id)
    item.name = payload.name
    item.description = payload.description
    item.sort_order = payload.sort_order
    _commit_or_conflict(db, "A symptom category with this name already exists.")
    db.refresh(item)
    return _category_response(item, repository.entry_counts_by_category(db, user.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    item = _get_owned_category(db, user, category_id)
    if repository.count_entries_for_category(db, user.id, category_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked entries before deleting this category.")
    repository.delete(db, item)
    db.commit()


def _validate_category_reference(db: Session, user: User, category_id: str | None) -> SymptomCategory | None:
    if not category_id:
        return None
    return _get_owned_category(db, user, category_id)


def _apply_entry_payload(item: SymptomEntry, payload: EntryCreateRequest | EntryUpdateRequest, category: SymptomCategory | None) -> None:
    item.category_id = category.id if category else None
    item.entry_date = payload.entry_date
    item.entry_time = payload.entry_time
    item.symptom_title = payload.symptom_title
    item.severity = payload.severity
    item.duration = payload.duration
    item.body_location = payload.body_location
    item.mood = payload.mood
    item.temperature = _decimal_or_none(payload.temperature)
    item.triggers = payload.triggers
    item.relief_methods = payload.relief_methods
    item.follow_up_notes = payload.follow_up_notes
    item.notes = payload.notes
    item.archived = payload.archived


def create_entry(db: Session, user: User, payload: EntryCreateRequest) -> EntryDetailResponse:
    category = _validate_category_reference(db, user, payload.category_id)
    item = SymptomEntry(owner_id=user.id, entry_date=payload.entry_date, symptom_title=payload.symptom_title, severity=payload.severity)
    _apply_entry_payload(item, payload, category)
    repository.add(db, item)
    _commit_or_conflict(db, "Unable to create symptom entry.")
    return get_entry(db, user, item.id)


def get_entry(db: Session, user: User, entry_id: str) -> EntryDetailResponse:
    return _entry_detail(_get_owned_entry(db, user, entry_id))


def update_entry(db: Session, user: User, entry_id: str, payload: EntryUpdateRequest) -> EntryDetailResponse:
    item = _get_owned_entry(db, user, entry_id)
    category = _validate_category_reference(db, user, payload.category_id)
    _apply_entry_payload(item, payload, category)
    _commit_or_conflict(db, "Unable to update symptom entry.")
    return get_entry(db, user, entry_id)


def set_entry_archived(db: Session, user: User, entry_id: str, archived: bool) -> EntryDetailResponse:
    item = _get_owned_entry(db, user, entry_id)
    item.archived = archived
    db.commit()
    return get_entry(db, user, entry_id)


def delete_entry(db: Session, user: User, entry_id: str) -> None:
    item = _get_owned_entry(db, user, entry_id)
    repository.delete(db, item)
    db.commit()


def _filtered_entries(db: Session, user: User, q: str | None, archive_filter: ArchiveFilter, category_id: str | None, severity_filter: SeverityFilter, body_location: str | None, date_from: date | None, date_to: date | None, sort_by: EntrySort) -> list[SymptomEntry]:
    entries = repository.list_entries(db, user.id)
    if archive_filter == "active":
        entries = [item for item in entries if not item.archived]
    elif archive_filter == "archived":
        entries = [item for item in entries if item.archived]
    if category_id:
        entries = [item for item in entries if item.category_id == category_id]
    if severity_filter == "mild":
        entries = [item for item in entries if item.severity <= 3]
    elif severity_filter == "moderate":
        entries = [item for item in entries if 4 <= item.severity <= 6]
    elif severity_filter == "severe":
        entries = [item for item in entries if item.severity >= 7]
    if body_location:
        needle = body_location.lower()
        entries = [item for item in entries if item.body_location and needle in item.body_location.lower()]
    if date_from:
        entries = [item for item in entries if item.entry_date >= date_from]
    if date_to:
        entries = [item for item in entries if item.entry_date <= date_to]
    if q:
        needle = q.lower()
        entries = [item for item in entries if needle in " ".join([item.symptom_title or "", item.category.name if item.category else "", item.body_location or "", item.mood or "", item.duration or "", item.triggers or "", item.relief_methods or "", item.notes or ""]).lower()]
    if sort_by == "severity":
        entries.sort(key=lambda item: (-item.severity, item.entry_date), reverse=False)
    elif sort_by == "category":
        entries.sort(key=lambda item: ((item.category.name if item.category else ""), item.entry_date), reverse=False)
    elif sort_by == "title":
        entries.sort(key=lambda item: (item.symptom_title.lower(), item.entry_date), reverse=False)
    elif sort_by == "created":
        entries.sort(key=lambda item: item.created_at, reverse=True)
    elif sort_by == "updated":
        entries.sort(key=lambda item: item.updated_at, reverse=True)
    else:
        entries.sort(key=lambda item: (item.entry_date, item.entry_time or item.created_at.time()), reverse=True)
    return entries


def list_entries(db: Session, user: User, q: str | None, archive_filter: ArchiveFilter, category_id: str | None, severity_filter: SeverityFilter, body_location: str | None, date_from: date | None, date_to: date | None, sort_by: EntrySort, page: int, page_size: int) -> EntryListResponse:
    ensure_default_categories(db, user)
    entries = _filtered_entries(db, user, q, archive_filter, category_id, severity_filter, body_location, date_from, date_to, sort_by)
    start = (page - 1) * page_size
    return EntryListResponse(items=[_entry_summary(item) for item in entries[start:start + page_size]], total=len(entries), page=page, page_size=page_size)


def _active_entries(db: Session, user: User) -> list[SymptomEntry]:
    return [item for item in repository.list_entries(db, user.id) if not item.archived]


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    entries = repository.list_entries(db, user.id)
    active = [item for item in entries if not item.archived]
    today = _today()
    week_start = today - timedelta(days=6)
    month_start = today.replace(day=1)
    category_counts = Counter(item.category.name if item.category else "Uncategorized" for item in active)
    average = round(sum(item.severity for item in active) / len(active), 1) if active else 0.0
    return DashboardResponse(total_entries=len(active), today_entries=sum(1 for item in active if item.entry_date == today), weekly_entries=sum(1 for item in active if item.entry_date >= week_start), monthly_entries=sum(1 for item in active if item.entry_date >= month_start), archived_entries=sum(1 for item in entries if item.archived), most_common_category=category_counts.most_common(1)[0][0] if category_counts else None, average_severity=average)


def _count_items(counter: Counter[str], limit: int = 8) -> list[CountItem]:
    return [CountItem(label=label, count=count) for label, count in counter.most_common(limit) if label]


def get_insights(db: Session, user: User) -> InsightsResponse:
    ensure_default_categories(db, user)
    dashboard = get_dashboard(db, user)
    active = _active_entries(db, user)
    category_counts = Counter(item.category.name if item.category else "Uncategorized" for item in active)
    body_counts = Counter(item.body_location or "Not set" for item in active)
    mood_counts = Counter(item.mood or "Not set" for item in active)
    severity_counts = Counter(_severity_label(item.severity) for item in active)
    grouped: dict[str, list[int]] = defaultdict(list)
    for item in active:
        grouped[item.symptom_title.lower()].append(item.severity)
    recurring = [RecurringSymptomItem(title=title.title(), count=len(values), average_severity=round(sum(values) / len(values), 1)) for title, values in grouped.items() if len(values) > 1]
    recurring.sort(key=lambda item: (-item.count, -item.average_severity, item.title))
    return InsightsResponse(**dashboard.model_dump(), categories=list_categories(db, user), entries_by_category=_count_items(category_counts), entries_by_body_location=_count_items(body_counts), entries_by_mood=_count_items(mood_counts), entries_by_severity=_count_items(severity_counts), recurring_symptoms=recurring[:8], recently_added_entries=[_entry_summary(item) for item in sorted(active, key=lambda item: item.created_at, reverse=True)[:8]])
