from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.home_inventory_manager import repository
from app.modules.home_inventory_manager.models import InventoryCategory, InventoryItem
from app.modules.home_inventory_manager.schemas import (
    ArchiveFilter,
    InventoryCategoryCreateRequest,
    InventoryCategoryResponse,
    InventoryCategoryUpdateRequest,
    InventoryCountItem,
    InventoryDashboardResponse,
    InventoryInsightsResponse,
    InventoryItemCreateRequest,
    InventoryItemDetailResponse,
    InventoryItemSummaryResponse,
    InventoryItemUpdateRequest,
    ItemSort,
    WarrantyFilter,
    WarrantyStatus,
)


def _today() -> date:
    return date.today()


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _money(value: object) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    if len(normalized) <= 140:
        return normalized
    return f"{normalized[:137]}..."


def _warranty_status(item: InventoryItem, today: date | None = None) -> WarrantyStatus:
    expiry = _parse_date(item.warranty_expiry)
    if not expiry:
        return "noWarranty"
    current = today or _today()
    if expiry < current:
        return "expired"
    if expiry <= current + timedelta(days=30):
        return "expiringSoon"
    return "active"


def _days_until_warranty_expiry(item: InventoryItem) -> int | None:
    expiry = _parse_date(item.warranty_expiry)
    if not expiry:
        return None
    return (expiry - _today()).days


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _get_owned_category(db: Session, user: User, category_id: str) -> InventoryCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category")
    return category


def _get_owned_item(db: Session, user: User, item_id: str) -> InventoryItem:
    item = repository.get_item(db, item_id)
    if not item or item.owner_id != user.id:
        _not_found("Item")
    return item


def _category_summary(category: InventoryCategory, item_count: int = 0) -> InventoryCategoryResponse:
    return InventoryCategoryResponse(
        id=category.id,
        name=category.name,
        item_count=item_count,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _item_summary(item: InventoryItem) -> InventoryItemSummaryResponse:
    return InventoryItemSummaryResponse(
        id=item.id,
        title=item.title,
        category_id=item.category_id,
        category_name=item.category.name,
        room=item.room,
        quantity=item.quantity,
        purchase_date=item.purchase_date,
        purchase_price=_money(item.purchase_price) if item.purchase_price is not None else None,
        estimated_value=_money(item.estimated_value) if item.estimated_value is not None else None,
        warranty_expiry=item.warranty_expiry,
        warranty_status=_warranty_status(item),
        days_until_warranty_expiry=_days_until_warranty_expiry(item),
        brand=item.brand,
        model=item.model,
        serial_number=item.serial_number,
        condition=item.condition,  # type: ignore[arg-type]
        notes_preview=_preview(item.notes),
        archived=item.archived,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _item_detail(item: InventoryItem) -> InventoryItemDetailResponse:
    return InventoryItemDetailResponse(**_item_summary(item).model_dump(), notes=item.notes)


def _apply_item_payload(item: InventoryItem, payload: InventoryItemCreateRequest | InventoryItemUpdateRequest) -> None:
    item.title = payload.title
    item.category_id = payload.category_id
    item.room = payload.room
    item.quantity = payload.quantity
    item.purchase_date = payload.purchase_date
    item.purchase_price = payload.purchase_price
    item.estimated_value = payload.estimated_value
    item.warranty_expiry = payload.warranty_expiry
    item.brand = payload.brand
    item.model = payload.model
    item.serial_number = payload.serial_number
    item.condition = payload.condition
    item.notes = payload.notes


def list_categories(db: Session, user: User) -> list[InventoryCategoryResponse]:
    counts = repository.item_counts_by_category(db, user.id)
    return [_category_summary(category, counts.get(category.id, 0)) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: InventoryCategoryCreateRequest) -> InventoryCategoryResponse:
    category = InventoryCategory(owner_id=user.id, name=payload.name)
    repository.add(db, category)
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_summary(category, 0)


def update_category(db: Session, user: User, category_id: str, payload: InventoryCategoryUpdateRequest) -> InventoryCategoryResponse:
    category = _get_owned_category(db, user, category_id)
    category.name = payload.name
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_summary(category, repository.count_items_for_category(db, user.id, category.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    if repository.count_items_for_category(db, user.id, category.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category has items. Reassign or delete items first.")
    repository.delete_record(db, category)
    db.commit()


def _matches_warranty_filter(item: InventoryItem, warranty_filter: WarrantyFilter) -> bool:
    if warranty_filter == "all":
        return True
    status_value = _warranty_status(item)
    if warranty_filter == "expiring":
        return status_value == "expiringSoon"
    if warranty_filter == "expired":
        return status_value == "expired"
    return status_value == "noWarranty"


def _filter_items(
    items: list[InventoryItem],
    query: str | None,
    category_id: str | None,
    room: str | None,
    condition: str | None,
    warranty_filter: WarrantyFilter,
    archive_filter: ArchiveFilter,
) -> list[InventoryItem]:
    term = (query or "").strip().lower()
    category_filter = (category_id or "").strip()
    room_filter = (room or "").strip().lower()
    condition_filter = (condition or "").strip().lower()
    result: list[InventoryItem] = []
    for item in items:
        haystack = [
            item.title,
            item.category.name,
            item.room,
            item.condition,
            item.brand or "",
            item.model or "",
            item.serial_number or "",
            item.notes or "",
        ]
        if term and not any(term in value.lower() for value in haystack):
            continue
        if category_filter and item.category_id != category_filter:
            continue
        if room_filter and item.room.lower() != room_filter:
            continue
        if condition_filter and item.condition.lower() != condition_filter:
            continue
        if archive_filter == "active" and item.archived:
            continue
        if archive_filter == "archived" and not item.archived:
            continue
        if not _matches_warranty_filter(item, warranty_filter):
            continue
        result.append(item)
    return result


def _sort_items(items: list[InventoryItem], sort_by: ItemSort) -> list[InventoryItem]:
    if sort_by == "title":
        return sorted(items, key=lambda item: item.title.lower())
    if sort_by == "estimatedValue":
        return sorted(items, key=lambda item: (_money(item.estimated_value), item.title.lower()), reverse=True)
    return sorted(items, key=lambda item: (_parse_date(item.purchase_date) is None, _parse_date(item.purchase_date) or date.min, item.title.lower()), reverse=True)


def list_items(
    db: Session,
    user: User,
    query: str | None = None,
    category_id: str | None = None,
    room: str | None = None,
    condition: str | None = None,
    warranty_filter: WarrantyFilter = "all",
    archive_filter: ArchiveFilter = "active",
    sort_by: ItemSort = "purchaseDate",
) -> list[InventoryItemSummaryResponse]:
    items = repository.list_items(db, user.id)
    filtered = _filter_items(items, query, category_id, room, condition, warranty_filter, archive_filter)
    return [_item_summary(item) for item in _sort_items(filtered, sort_by)]


def create_item(db: Session, user: User, payload: InventoryItemCreateRequest) -> InventoryItemDetailResponse:
    category = _get_owned_category(db, user, payload.category_id)
    item = InventoryItem(owner_id=user.id, category_id=category.id, title=payload.title, room=payload.room, quantity=payload.quantity, condition=payload.condition)
    _apply_item_payload(item, payload)
    repository.add(db, item)
    _commit_or_conflict(db, "Unable to create inventory item.")
    db.refresh(item)
    item.category = category
    return _item_detail(item)


def get_item(db: Session, user: User, item_id: str) -> InventoryItemDetailResponse:
    return _item_detail(_get_owned_item(db, user, item_id))


def update_item(db: Session, user: User, item_id: str, payload: InventoryItemUpdateRequest) -> InventoryItemDetailResponse:
    item = _get_owned_item(db, user, item_id)
    category = _get_owned_category(db, user, payload.category_id)
    _apply_item_payload(item, payload)
    _commit_or_conflict(db, "Unable to update inventory item.")
    db.refresh(item)
    item.category = category
    return _item_detail(item)


def set_item_archived(db: Session, user: User, item_id: str, archived: bool) -> InventoryItemDetailResponse:
    item = _get_owned_item(db, user, item_id)
    item.archived = archived
    db.commit()
    db.refresh(item)
    return _item_detail(item)


def delete_item(db: Session, user: User, item_id: str) -> None:
    item = _get_owned_item(db, user, item_id)
    repository.delete_record(db, item)
    db.commit()


def get_dashboard(db: Session, user: User) -> InventoryDashboardResponse:
    items = repository.list_items(db, user.id)
    active_items = [item for item in items if not item.archived]
    return InventoryDashboardResponse(
        total_items=len(items),
        active_items=len(active_items),
        archived_items=len(items) - len(active_items),
        warranty_expiring_count=len([item for item in active_items if _warranty_status(item) == "expiringSoon"]),
        estimated_total_value=sum((_money(item.estimated_value) * item.quantity for item in active_items), Decimal("0.00")),
    )


def get_insights(db: Session, user: User) -> InventoryInsightsResponse:
    items = repository.list_items(db, user.id)
    active_items = [item for item in items if not item.archived]
    dashboard = get_dashboard(db, user)
    category_counts = Counter(item.category.name for item in active_items)
    room_counts = Counter(item.room for item in active_items)
    condition_counts = Counter(item.condition for item in active_items)
    warranty_counts = Counter(_warranty_status(item) for item in active_items)
    recent_items = sorted(active_items, key=lambda item: item.created_at, reverse=True)[:8]
    highest_value_items = sorted(active_items, key=lambda item: (_money(item.estimated_value), item.title.lower()), reverse=True)[:8]

    return InventoryInsightsResponse(
        **dashboard.model_dump(),
        categories=list_categories(db, user),
        category_distribution=[InventoryCountItem(label=label, count=count) for label, count in category_counts.most_common(8)],
        room_distribution=[InventoryCountItem(label=label, count=count) for label, count in room_counts.most_common(8)],
        condition_distribution=[InventoryCountItem(label=label, count=count) for label, count in condition_counts.most_common(8)],
        warranty_summary=[InventoryCountItem(label=label, count=count) for label, count in warranty_counts.most_common()],
        recent_items=[_item_summary(item) for item in recent_items],
        highest_value_items=[_item_summary(item) for item in highest_value_items],
    )
