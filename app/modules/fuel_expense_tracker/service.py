from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.fuel_expense_tracker import repository
from app.modules.fuel_expense_tracker.models import FuelEntry, FuelVehicle
from app.modules.fuel_expense_tracker.schemas import ArchiveFilter, DashboardResponse, EntryCreateRequest, EntryListResponse, EntryResponse, EntrySort, EntryUpdateRequest, InsightsResponse, MoneyItem, CountItem, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _vehicle(db: Session, user: User, vehicle_id: str) -> FuelVehicle:
    item = repository.get_vehicle(db, vehicle_id)
    if not item or item.owner_id != user.id:
        _not_found("Fuel vehicle")
    return item


def _entry(db: Session, user: User, entry_id: str) -> FuelEntry:
    item = repository.get_entry(db, entry_id)
    if not item or item.owner_id != user.id:
        _not_found("Fuel entry")
    return item


def _money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _quantity(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.001"))


def _entry_economy(entries: list[FuelEntry], item: FuelEntry) -> Decimal | None:
    if item.odometer is None:
        return None
    same_vehicle = sorted([entry for entry in entries if entry.vehicle_id == item.vehicle_id and entry.odometer is not None], key=lambda entry: (entry.odometer, entry.purchase_date))
    previous = None
    for candidate in same_vehicle:
        if candidate.id == item.id:
            break
        previous = candidate
    if not previous or previous.odometer is None or item.odometer <= previous.odometer or item.fuel_quantity <= 0:
        return None
    distance = Decimal(str(item.odometer - previous.odometer))
    economy = distance / Decimal(str(item.fuel_quantity))
    return economy.quantize(Decimal("0.01"))


def _vehicle_response(item: FuelVehicle, entries: list[FuelEntry]) -> VehicleResponse:
    vehicle_entries = [entry for entry in entries if entry.vehicle_id == item.id]
    return VehicleResponse(id=item.id, vehicle_name=item.vehicle_name, manufacturer=item.manufacturer, model=item.model, year=item.year, fuel_type=item.fuel_type, registration_nickname=item.registration_nickname, odometer_unit=item.odometer_unit, notes=item.notes, archived=item.archived, entry_count=len(vehicle_entries), total_cost=sum((_money(e.total_cost) for e in vehicle_entries), Decimal("0.00")), total_fuel=sum((_quantity(e.fuel_quantity) for e in vehicle_entries), Decimal("0.000")), created_at=item.created_at, updated_at=item.updated_at)


def _entry_response(item: FuelEntry, entries: list[FuelEntry]) -> EntryResponse:
    return EntryResponse(id=item.id, vehicle_id=item.vehicle_id, vehicle_name=item.vehicle.vehicle_name, purchase_date=item.purchase_date, odometer=item.odometer, fuel_quantity=item.fuel_quantity, fuel_unit=item.fuel_unit, total_cost=item.total_cost, currency=item.currency, unit_price=item.unit_price, station_name=item.station_name, payment_method=item.payment_method, full_tank=item.full_tank, fuel_economy=_entry_economy(entries, item), notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)


def list_vehicles(db: Session, user: User, archive_filter: ArchiveFilter = "active") -> list[VehicleResponse]:
    vehicles = repository.list_vehicles(db, user.id)
    if archive_filter == "active":
        vehicles = [item for item in vehicles if not item.archived]
    elif archive_filter == "archived":
        vehicles = [item for item in vehicles if item.archived]
    entries = repository.list_entries(db, user.id)
    return [_vehicle_response(item, entries) for item in vehicles]


def create_vehicle(db: Session, user: User, payload: VehicleCreateRequest) -> VehicleResponse:
    item = FuelVehicle(owner_id=user.id, vehicle_name=payload.vehicle_name, manufacturer=payload.manufacturer, model=payload.model, year=payload.year, fuel_type=payload.fuel_type, registration_nickname=payload.registration_nickname, odometer_unit=payload.odometer_unit, notes=payload.notes, archived=payload.archived)
    repository.add(db, item)
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_entries(db, user.id))


def update_vehicle(db: Session, user: User, vehicle_id: str, payload: VehicleUpdateRequest) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.vehicle_name = payload.vehicle_name
    item.manufacturer = payload.manufacturer
    item.model = payload.model
    item.year = payload.year
    item.fuel_type = payload.fuel_type
    item.registration_nickname = payload.registration_nickname
    item.odometer_unit = payload.odometer_unit
    item.notes = payload.notes
    item.archived = payload.archived
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_entries(db, user.id))


def set_vehicle_archived(db: Session, user: User, vehicle_id: str, archived: bool) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.archived = archived
    db.commit()
    return _vehicle_response(item, repository.list_entries(db, user.id))


def delete_vehicle(db: Session, user: User, vehicle_id: str) -> None:
    item = _vehicle(db, user, vehicle_id)
    if repository.count_entries_for_vehicle(db, user.id, vehicle_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked fuel entries before deleting this vehicle.")
    repository.delete(db, item)
    db.commit()


def _validate_odometer(db: Session, user: User, payload: EntryCreateRequest | EntryUpdateRequest, ignore_entry_id: str | None = None) -> None:
    if payload.odometer is None:
        return
    entries = [entry for entry in repository.list_entries(db, user.id) if entry.vehicle_id == payload.vehicle_id and entry.odometer is not None and entry.id != ignore_entry_id]
    for entry in entries:
        if entry.purchase_date <= payload.purchase_date and entry.odometer > payload.odometer:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Odometer reading cannot be lower than an earlier stored reading for this vehicle.")
        if entry.purchase_date >= payload.purchase_date and entry.odometer < payload.odometer:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Odometer reading cannot be higher than a later stored reading for this vehicle.")


def _apply_entry(item: FuelEntry, payload: EntryCreateRequest | EntryUpdateRequest) -> None:
    item.vehicle_id = payload.vehicle_id
    item.purchase_date = payload.purchase_date
    item.odometer = payload.odometer
    item.fuel_quantity = payload.fuel_quantity
    item.fuel_unit = payload.fuel_unit
    item.total_cost = payload.total_cost
    item.currency = payload.currency
    item.unit_price = payload.unit_price or (payload.total_cost / payload.fuel_quantity).quantize(Decimal("0.0001"))
    item.station_name = payload.station_name
    item.payment_method = payload.payment_method
    item.full_tank = payload.full_tank
    item.notes = payload.notes


def create_entry(db: Session, user: User, payload: EntryCreateRequest) -> EntryResponse:
    vehicle = _vehicle(db, user, payload.vehicle_id)
    _validate_odometer(db, user, payload)
    item = FuelEntry(owner_id=user.id, vehicle_id=vehicle.id, purchase_date=payload.purchase_date, fuel_quantity=payload.fuel_quantity, total_cost=payload.total_cost, unit_price=payload.unit_price or Decimal("0"))
    _apply_entry(item, payload)
    repository.add(db, item)
    db.commit()
    return _entry_response(repository.get_entry(db, item.id), repository.list_entries(db, user.id))


def get_entry(db: Session, user: User, entry_id: str) -> EntryResponse:
    return _entry_response(_entry(db, user, entry_id), repository.list_entries(db, user.id))


def update_entry(db: Session, user: User, entry_id: str, payload: EntryUpdateRequest) -> EntryResponse:
    item = _entry(db, user, entry_id)
    _vehicle(db, user, payload.vehicle_id)
    _validate_odometer(db, user, payload, entry_id)
    _apply_entry(item, payload)
    db.commit()
    return get_entry(db, user, entry_id)


def delete_entry(db: Session, user: User, entry_id: str) -> None:
    repository.delete(db, _entry(db, user, entry_id))
    db.commit()


def _filtered_entries(db: Session, user: User, q: str | None, vehicle_id: str | None, date_from: date | None, date_to: date | None, station: str | None, sort_by: EntrySort) -> list[FuelEntry]:
    entries = repository.list_entries(db, user.id)
    if vehicle_id:
        entries = [item for item in entries if item.vehicle_id == vehicle_id]
    if date_from:
        entries = [item for item in entries if item.purchase_date >= date_from]
    if date_to:
        entries = [item for item in entries if item.purchase_date <= date_to]
    if station:
        needle = station.lower()
        entries = [item for item in entries if item.station_name and needle in item.station_name.lower()]
    if q:
        needle = q.lower()
        entries = [item for item in entries if needle in " ".join([item.vehicle.vehicle_name, item.station_name or "", item.payment_method or "", item.notes or ""]).lower()]
    if sort_by == "cost":
        entries.sort(key=lambda item: item.total_cost, reverse=True)
    elif sort_by == "quantity":
        entries.sort(key=lambda item: item.fuel_quantity, reverse=True)
    elif sort_by == "vehicle":
        entries.sort(key=lambda item: (item.vehicle.vehicle_name, item.purchase_date))
    elif sort_by == "station":
        entries.sort(key=lambda item: (item.station_name or "", item.purchase_date))
    elif sort_by == "created":
        entries.sort(key=lambda item: item.created_at, reverse=True)
    else:
        entries.sort(key=lambda item: (item.purchase_date, item.created_at), reverse=True)
    return entries


def list_entries(db: Session, user: User, q: str | None, vehicle_id: str | None, date_from: date | None, date_to: date | None, station: str | None, sort_by: EntrySort, page: int, page_size: int) -> EntryListResponse:
    entries = _filtered_entries(db, user, q, vehicle_id, date_from, date_to, station, sort_by)
    all_entries = repository.list_entries(db, user.id)
    start = (page - 1) * page_size
    return EntryListResponse(items=[_entry_response(item, all_entries) for item in entries[start:start + page_size]], total=len(entries), page=page, page_size=page_size)


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    entries = repository.list_entries(db, user.id)
    vehicles = [v for v in repository.list_vehicles(db, user.id) if not v.archived]
    today = date.today()
    total_cost = sum((_money(e.total_cost) for e in entries), Decimal("0.00"))
    month_cost = sum((_money(e.total_cost) for e in entries if e.purchase_date.year == today.year and e.purchase_date.month == today.month), Decimal("0.00"))
    total_fuel = sum((_quantity(e.fuel_quantity) for e in entries), Decimal("0.000"))
    prices = [Decimal(str(e.unit_price)) for e in entries]
    economies = [eco for e in entries if (eco := _entry_economy(entries, e)) is not None]
    return DashboardResponse(total_cost=total_cost, monthly_cost=month_cost, total_fuel=total_fuel, average_fuel_price=(sum(prices, Decimal("0")) / len(prices)).quantize(Decimal("0.01")) if prices else Decimal("0.00"), average_fuel_economy=(sum(economies, Decimal("0")) / len(economies)).quantize(Decimal("0.01")) if economies else None, total_entries=len(entries), total_vehicles=len(vehicles))


def get_insights(db: Session, user: User) -> InsightsResponse:
    entries = repository.list_entries(db, user.id)
    vehicles = repository.list_vehicles(db, user.id)
    dashboard = get_dashboard(db, user)
    cost_month: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    cost_vehicle: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    station_counts: Counter[str] = Counter()
    for entry in entries:
        cost_month[entry.purchase_date.strftime("%Y-%m")] += _money(entry.total_cost)
        cost_vehicle[entry.vehicle.vehicle_name] += _money(entry.total_cost)
        station_counts[entry.station_name or "Not set"] += 1
    sorted_entries = sorted(entries, key=lambda e: e.purchase_date, reverse=True)
    highest = max(entries, key=lambda e: e.total_cost, default=None)
    lowest = min(entries, key=lambda e: e.total_cost, default=None)
    return InsightsResponse(**dashboard.model_dump(), vehicles=[_vehicle_response(v, entries) for v in vehicles], recent_entries=[_entry_response(e, entries) for e in sorted_entries[:8]], cost_by_month=[MoneyItem(label=k, amount=v) for k, v in sorted(cost_month.items(), reverse=True)[:12]], cost_by_vehicle=[MoneyItem(label=k, amount=v) for k, v in sorted(cost_vehicle.items())], purchases_by_station=[CountItem(label=k, count=v) for k, v in station_counts.most_common(8)], highest_expense=_entry_response(highest, entries) if highest else None, lowest_expense=_entry_response(lowest, entries) if lowest else None)
