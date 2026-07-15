from __future__ import annotations

from collections import Counter
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.packing_checklist import repository
from app.modules.packing_checklist.models import PackingCategory, PackingItem, PackingTripChecklist
from app.modules.packing_checklist.schemas import (
    ArchiveFilter,
    ChecklistSort,
    PackedFilter,
    PackingCategoryCreateRequest,
    PackingCategoryResponse,
    PackingCategoryUpdateRequest,
    PackingChecklistCreateRequest,
    PackingChecklistDashboardResponse,
    PackingChecklistDetailResponse,
    PackingChecklistInsightsResponse,
    PackingChecklistSummaryResponse,
    PackingChecklistUpdateRequest,
    PackingCountItem,
    PackingItemCreateRequest,
    PackingItemResponse,
    PackingItemUpdateRequest,
)

DEFAULT_CATEGORIES = [
    ("Documents", 10),
    ("Clothing", 20),
    ("Toiletries", 30),
    ("Electronics", 40),
    ("Medicines", 50),
    ("Accessories", 60),
    ("Baby Items", 70),
    ("Food", 80),
    ("Sports", 90),
    ("Camping", 100),
    ("Work", 110),
    ("Miscellaneous", 120),
]


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


def ensure_default_categories(db: Session, user: User) -> None:
    existing_names = {category.name.lower() for category in repository.list_categories(db, user.id)}
    created = False
    for name, sort_order in DEFAULT_CATEGORIES:
        if name.lower() in existing_names:
            continue
        repository.add(db, PackingCategory(owner_id=user.id, name=name, sort_order=sort_order, is_system=True))
        created = True
    if created:
        _commit_or_conflict(db, "Unable to prepare default packing categories.")


def _get_owned_category(db: Session, user: User, category_id: str) -> PackingCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category")
    return category


def _get_owned_checklist(db: Session, user: User, checklist_id: str) -> PackingTripChecklist:
    checklist = repository.get_checklist(db, checklist_id)
    if not checklist or checklist.owner_id != user.id:
        _not_found("Checklist")
    return checklist


def _get_owned_item(db: Session, user: User, item_id: str) -> PackingItem:
    item = repository.get_item(db, item_id)
    if not item or item.owner_id != user.id or item.checklist.owner_id != user.id:
        _not_found("Item")
    return item


def _progress(items: list[PackingItem]) -> tuple[int, int, int, int, int]:
    total = len(items)
    packed = len([item for item in items if item.packed])
    remaining = total - packed
    high_priority_remaining = len([item for item in items if item.priority == "high" and not item.packed])
    completion = int(round((packed / total) * 100)) if total else 0
    return total, packed, remaining, high_priority_remaining, completion


def _category_response(category: PackingCategory, item_count: int = 0) -> PackingCategoryResponse:
    return PackingCategoryResponse(
        id=category.id,
        name=category.name,
        sort_order=category.sort_order,
        is_system=category.is_system,
        item_count=item_count,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _item_response(item: PackingItem) -> PackingItemResponse:
    return PackingItemResponse(
        id=item.id,
        checklist_id=item.checklist_id,
        category_id=item.category_id,
        category_name=item.category.name,
        item_name=item.item_name,
        quantity=item.quantity,
        packed=item.packed,
        priority=item.priority,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _checklist_summary(checklist: PackingTripChecklist) -> PackingChecklistSummaryResponse:
    total, packed, remaining, high_priority_remaining, completion = _progress(checklist.items)
    return PackingChecklistSummaryResponse(
        id=checklist.id,
        title=checklist.title,
        destination=checklist.destination,
        trip_type=checklist.trip_type,
        start_date=checklist.start_date,
        end_date=checklist.end_date,
        status=checklist.status,
        archived=checklist.archived,
        notes_preview=_preview(checklist.notes),
        total_items=total,
        packed_items=packed,
        remaining_items=remaining,
        high_priority_remaining=high_priority_remaining,
        completion_percentage=completion,
        created_at=checklist.created_at,
        updated_at=checklist.updated_at,
    )


def _checklist_detail(checklist: PackingTripChecklist) -> PackingChecklistDetailResponse:
    items = sorted(checklist.items, key=lambda item: (item.packed, item.category.sort_order, item.priority != "high", item.item_name.lower()))
    return PackingChecklistDetailResponse(**_checklist_summary(checklist).model_dump(), notes=checklist.notes, items=[_item_response(item) for item in items])


def _apply_checklist_payload(checklist: PackingTripChecklist, payload: PackingChecklistCreateRequest | PackingChecklistUpdateRequest) -> None:
    checklist.title = payload.title
    checklist.destination = payload.destination
    checklist.trip_type = payload.trip_type
    checklist.start_date = payload.start_date
    checklist.end_date = payload.end_date
    checklist.status = payload.status
    checklist.notes = payload.notes


def _apply_item_payload(item: PackingItem, payload: PackingItemCreateRequest | PackingItemUpdateRequest) -> None:
    item.category_id = payload.category_id
    item.item_name = payload.item_name
    item.quantity = payload.quantity
    item.packed = payload.packed
    item.priority = payload.priority
    item.notes = payload.notes


def list_categories(db: Session, user: User) -> list[PackingCategoryResponse]:
    ensure_default_categories(db, user)
    counts = repository.item_counts_by_category(db, user.id)
    return [_category_response(category, counts.get(category.id, 0)) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: PackingCategoryCreateRequest) -> PackingCategoryResponse:
    category = PackingCategory(owner_id=user.id, name=payload.name, sort_order=payload.sort_order)
    repository.add(db, category)
    _commit_or_conflict(db, "A packing category with this name already exists.")
    db.refresh(category)
    return _category_response(category, 0)


def update_category(db: Session, user: User, category_id: str, payload: PackingCategoryUpdateRequest) -> PackingCategoryResponse:
    category = _get_owned_category(db, user, category_id)
    category.name = payload.name
    category.sort_order = payload.sort_order
    _commit_or_conflict(db, "A packing category with this name already exists.")
    db.refresh(category)
    return _category_response(category, repository.count_items_for_category(db, user.id, category.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    if repository.count_items_for_category(db, user.id, category.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category has packing items. Reassign or delete items first.")
    repository.delete_record(db, category)
    db.commit()


def _filter_checklists(checklists: list[PackingTripChecklist], query: str | None, archive_filter: ArchiveFilter, trip_type: str | None) -> list[PackingTripChecklist]:
    term = (query or "").strip().lower()
    trip_type_filter = (trip_type or "").strip().lower()
    filtered: list[PackingTripChecklist] = []
    for checklist in checklists:
        if archive_filter == "active" and checklist.archived:
            continue
        if archive_filter == "archived" and not checklist.archived:
            continue
        haystack = [checklist.title, checklist.destination or "", checklist.trip_type, checklist.status, checklist.notes or ""]
        if term and not any(term in value.lower() for value in haystack):
            continue
        if trip_type_filter and checklist.trip_type.lower() != trip_type_filter:
            continue
        filtered.append(checklist)
    return filtered


def _sort_checklists(checklists: list[PackingTripChecklist], sort_by: ChecklistSort) -> list[PackingTripChecklist]:
    if sort_by == "title":
        return sorted(checklists, key=lambda checklist: checklist.title.lower())
    if sort_by == "startDate":
        return sorted(checklists, key=lambda checklist: (checklist.start_date is None, checklist.start_date or date.max, checklist.title.lower()))
    if sort_by == "progress":
        return sorted(checklists, key=lambda checklist: (_progress(checklist.items)[4], checklist.title.lower()), reverse=True)
    return sorted(checklists, key=lambda checklist: checklist.updated_at, reverse=True)


def list_checklists(
    db: Session,
    user: User,
    query: str | None = None,
    archive_filter: ArchiveFilter = "active",
    trip_type: str | None = None,
    sort_by: ChecklistSort = "updated",
) -> list[PackingChecklistSummaryResponse]:
    ensure_default_categories(db, user)
    checklists = repository.list_checklists(db, user.id)
    return [_checklist_summary(checklist) for checklist in _sort_checklists(_filter_checklists(checklists, query, archive_filter, trip_type), sort_by)]


def create_checklist(db: Session, user: User, payload: PackingChecklistCreateRequest) -> PackingChecklistDetailResponse:
    ensure_default_categories(db, user)
    checklist = PackingTripChecklist(owner_id=user.id, title=payload.title, trip_type=payload.trip_type)
    _apply_checklist_payload(checklist, payload)
    repository.add(db, checklist)
    _commit_or_conflict(db, "Unable to create packing checklist.")
    db.refresh(checklist)
    return _checklist_detail(checklist)


def get_checklist(db: Session, user: User, checklist_id: str) -> PackingChecklistDetailResponse:
    return _checklist_detail(_get_owned_checklist(db, user, checklist_id))


def update_checklist(db: Session, user: User, checklist_id: str, payload: PackingChecklistUpdateRequest) -> PackingChecklistDetailResponse:
    checklist = _get_owned_checklist(db, user, checklist_id)
    _apply_checklist_payload(checklist, payload)
    _commit_or_conflict(db, "Unable to update packing checklist.")
    db.refresh(checklist)
    return _checklist_detail(checklist)


def duplicate_checklist(db: Session, user: User, checklist_id: str) -> PackingChecklistDetailResponse:
    checklist = _get_owned_checklist(db, user, checklist_id)
    duplicate = PackingTripChecklist(
        owner_id=user.id,
        title=f"{checklist.title} Copy",
        destination=checklist.destination,
        trip_type=checklist.trip_type,
        start_date=checklist.start_date,
        end_date=checklist.end_date,
        status="planning",
        notes=checklist.notes,
        archived=False,
    )
    repository.add(db, duplicate)
    db.flush()
    for item in checklist.items:
        repository.add(
            db,
            PackingItem(
                owner_id=user.id,
                checklist_id=duplicate.id,
                category_id=item.category_id,
                item_name=item.item_name,
                quantity=item.quantity,
                packed=False,
                priority=item.priority,
                notes=item.notes,
            ),
        )
    _commit_or_conflict(db, "Unable to duplicate packing checklist.")
    db.refresh(duplicate)
    return _checklist_detail(_get_owned_checklist(db, user, duplicate.id))


def set_checklist_archived(db: Session, user: User, checklist_id: str, archived: bool) -> PackingChecklistDetailResponse:
    checklist = _get_owned_checklist(db, user, checklist_id)
    checklist.archived = archived
    db.commit()
    db.refresh(checklist)
    return _checklist_detail(checklist)


def delete_checklist(db: Session, user: User, checklist_id: str) -> None:
    checklist = _get_owned_checklist(db, user, checklist_id)
    repository.delete_record(db, checklist)
    db.commit()


def create_item(db: Session, user: User, checklist_id: str, payload: PackingItemCreateRequest) -> PackingItemResponse:
    checklist = _get_owned_checklist(db, user, checklist_id)
    category = _get_owned_category(db, user, payload.category_id)
    item = PackingItem(owner_id=user.id, checklist_id=checklist.id, category_id=category.id, item_name=payload.item_name)
    _apply_item_payload(item, payload)
    repository.add(db, item)
    _commit_or_conflict(db, "Unable to add packing item.")
    db.refresh(item)
    item.category = category
    return _item_response(item)


def list_items(db: Session, user: User, checklist_id: str, category_id: str | None = None, packed_filter: PackedFilter = "all") -> list[PackingItemResponse]:
    checklist = _get_owned_checklist(db, user, checklist_id)
    category_filter = (category_id or "").strip()
    items: list[PackingItem] = []
    for item in checklist.items:
        if category_filter and item.category_id != category_filter:
            continue
        if packed_filter == "packed" and not item.packed:
            continue
        if packed_filter == "remaining" and item.packed:
            continue
        items.append(item)
    return [_item_response(item) for item in sorted(items, key=lambda record: (record.packed, record.category.sort_order, record.item_name.lower()))]


def update_item(db: Session, user: User, item_id: str, payload: PackingItemUpdateRequest) -> PackingItemResponse:
    item = _get_owned_item(db, user, item_id)
    category = _get_owned_category(db, user, payload.category_id)
    _apply_item_payload(item, payload)
    _commit_or_conflict(db, "Unable to update packing item.")
    db.refresh(item)
    item.category = category
    return _item_response(item)


def set_item_packed(db: Session, user: User, item_id: str, packed: bool) -> PackingItemResponse:
    item = _get_owned_item(db, user, item_id)
    item.packed = packed
    db.commit()
    db.refresh(item)
    return _item_response(item)


def delete_item(db: Session, user: User, item_id: str) -> None:
    item = _get_owned_item(db, user, item_id)
    repository.delete_record(db, item)
    db.commit()


def get_dashboard(db: Session, user: User) -> PackingChecklistDashboardResponse:
    ensure_default_categories(db, user)
    checklists = repository.list_checklists(db, user.id)
    active = [checklist for checklist in checklists if not checklist.archived]
    totals = [_progress(checklist.items) for checklist in checklists]
    total_items = sum(total for total, _, _, _, _ in totals)
    packed_items = sum(packed for _, packed, _, _, _ in totals)
    remaining_items = sum(remaining for _, _, remaining, _, _ in totals)
    high_priority_remaining = sum(high for _, _, _, high, _ in totals)
    average_completion = int(round(sum(completion for _, _, _, _, completion in totals) / len(totals))) if totals else 0
    return PackingChecklistDashboardResponse(
        total_checklists=len(checklists),
        active_checklists=len(active),
        archived_checklists=len(checklists) - len(active),
        total_items=total_items,
        packed_items=packed_items,
        remaining_items=remaining_items,
        high_priority_remaining=high_priority_remaining,
        average_completion=average_completion,
    )


def get_insights(db: Session, user: User) -> PackingChecklistInsightsResponse:
    checklists = repository.list_checklists(db, user.id)
    dashboard = get_dashboard(db, user)
    all_items = [item for checklist in checklists for item in checklist.items]
    status_counts = Counter(checklist.status for checklist in checklists)
    trip_type_counts = Counter(checklist.trip_type for checklist in checklists)
    category_counts = Counter(item.category.name for item in all_items)
    upcoming = sorted([checklist for checklist in checklists if checklist.start_date and not checklist.archived], key=lambda checklist: checklist.start_date)[:8]
    recent = sorted(checklists, key=lambda checklist: checklist.updated_at, reverse=True)[:8]
    return PackingChecklistInsightsResponse(
        **dashboard.model_dump(),
        categories=list_categories(db, user),
        status_distribution=[PackingCountItem(label=label, count=count) for label, count in status_counts.most_common(10)],
        trip_type_distribution=[PackingCountItem(label=label, count=count) for label, count in trip_type_counts.most_common(10)],
        category_distribution=[PackingCountItem(label=label, count=count) for label, count in category_counts.most_common(12)],
        upcoming_checklists=[_checklist_summary(checklist) for checklist in upcoming],
        recently_updated=[_checklist_summary(checklist) for checklist in recent],
    )
