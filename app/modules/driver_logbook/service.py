from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.driver_logbook import repository
from app.modules.driver_logbook.models import DriverTrip, DriverVehicle
from app.modules.driver_logbook.schemas import ArchiveFilter, CountItem, DashboardResponse, DistanceItem, InsightsResponse, TripCreateRequest, TripListResponse, TripResponse, TripSort, TripUpdateRequest, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _vehicle(db: Session, user: User, vehicle_id: str) -> DriverVehicle:
    item = repository.get_vehicle(db, vehicle_id)
    if not item or item.owner_id != user.id:
        _not_found("Driver vehicle")
    return item


def _trip(db: Session, user: User, trip_id: str) -> DriverTrip:
    item = repository.get_trip(db, trip_id)
    if not item or item.owner_id != user.id:
        _not_found("Driver trip")
    return item


def _distance(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.1"))


def _duration_minutes(item: DriverTrip) -> int | None:
    if not item.start_time or not item.end_time:
        return None
    start = datetime.combine(item.trip_date, item.start_time)
    end = datetime.combine(item.trip_date, item.end_time)
    return int((end - start).total_seconds() // 60)


def _vehicle_response(item: DriverVehicle, trips: list[DriverTrip]) -> VehicleResponse:
    vehicle_trips = [trip for trip in trips if trip.vehicle_id == item.id and not trip.archived]
    return VehicleResponse(id=item.id, vehicle_name=item.vehicle_name, manufacturer=item.manufacturer, model=item.model, year=item.year, registration_nickname=item.registration_nickname, odometer_unit=item.odometer_unit, notes=item.notes, archived=item.archived, trip_count=len(vehicle_trips), total_distance=sum((_distance(t.distance) for t in vehicle_trips), Decimal("0.0")), created_at=item.created_at, updated_at=item.updated_at)


def _trip_response(item: DriverTrip) -> TripResponse:
    return TripResponse(id=item.id, vehicle_id=item.vehicle_id, vehicle_name=item.vehicle.vehicle_name, trip_date=item.trip_date, start_time=item.start_time, end_time=item.end_time, start_odometer=item.start_odometer, end_odometer=item.end_odometer, distance=item.distance, purpose=item.purpose, start_location=item.start_location, destination=item.destination, duration_minutes=_duration_minutes(item), archived=item.archived, notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)


def list_vehicles(db: Session, user: User, archive_filter: ArchiveFilter = "active") -> list[VehicleResponse]:
    vehicles = repository.list_vehicles(db, user.id)
    if archive_filter == "active":
        vehicles = [item for item in vehicles if not item.archived]
    elif archive_filter == "archived":
        vehicles = [item for item in vehicles if item.archived]
    trips = repository.list_trips(db, user.id)
    return [_vehicle_response(item, trips) for item in vehicles]


def create_vehicle(db: Session, user: User, payload: VehicleCreateRequest) -> VehicleResponse:
    item = DriverVehicle(owner_id=user.id, vehicle_name=payload.vehicle_name, manufacturer=payload.manufacturer, model=payload.model, year=payload.year, registration_nickname=payload.registration_nickname, odometer_unit=payload.odometer_unit, notes=payload.notes, archived=payload.archived)
    repository.add(db, item)
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_trips(db, user.id))


def update_vehicle(db: Session, user: User, vehicle_id: str, payload: VehicleUpdateRequest) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.vehicle_name = payload.vehicle_name
    item.manufacturer = payload.manufacturer
    item.model = payload.model
    item.year = payload.year
    item.registration_nickname = payload.registration_nickname
    item.odometer_unit = payload.odometer_unit
    item.notes = payload.notes
    item.archived = payload.archived
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_trips(db, user.id))


def set_vehicle_archived(db: Session, user: User, vehicle_id: str, archived: bool) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.archived = archived
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_trips(db, user.id))


def delete_vehicle(db: Session, user: User, vehicle_id: str) -> None:
    item = _vehicle(db, user, vehicle_id)
    if repository.count_trips_for_vehicle(db, user.id, vehicle_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked trips before deleting this vehicle.")
    repository.delete(db, item)
    db.commit()


def _validate_odometer(db: Session, user: User, payload: TripCreateRequest | TripUpdateRequest, ignore_trip_id: str | None = None) -> None:
    if payload.start_odometer is None and payload.end_odometer is None:
        return
    trips = [trip for trip in repository.list_trips(db, user.id) if trip.vehicle_id == payload.vehicle_id and not trip.archived and trip.id != ignore_trip_id]
    for trip in trips:
        stored_end = trip.end_odometer if trip.end_odometer is not None else trip.start_odometer
        stored_start = trip.start_odometer if trip.start_odometer is not None else trip.end_odometer
        new_start = payload.start_odometer if payload.start_odometer is not None else payload.end_odometer
        new_end = payload.end_odometer if payload.end_odometer is not None else payload.start_odometer
        if stored_end is not None and new_start is not None and trip.trip_date <= payload.trip_date and stored_end > new_start:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Trip odometer cannot be lower than an earlier stored reading for this vehicle.")
        if stored_start is not None and new_end is not None and trip.trip_date >= payload.trip_date and stored_start < new_end:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Trip odometer cannot be higher than a later stored reading for this vehicle.")


def _apply_trip(item: DriverTrip, payload: TripCreateRequest | TripUpdateRequest) -> None:
    item.vehicle_id = payload.vehicle_id
    item.trip_date = payload.trip_date
    item.start_time = payload.start_time
    item.end_time = payload.end_time
    item.start_odometer = payload.start_odometer
    item.end_odometer = payload.end_odometer
    item.distance = payload.distance or Decimal("0.0")
    item.purpose = payload.purpose
    item.start_location = payload.start_location
    item.destination = payload.destination
    item.archived = payload.archived
    item.notes = payload.notes


def create_trip(db: Session, user: User, payload: TripCreateRequest) -> TripResponse:
    vehicle = _vehicle(db, user, payload.vehicle_id)
    _validate_odometer(db, user, payload)
    item = DriverTrip(owner_id=user.id, vehicle_id=vehicle.id, trip_date=payload.trip_date, distance=payload.distance or Decimal("0.0"), purpose=payload.purpose)
    _apply_trip(item, payload)
    repository.add(db, item)
    db.commit()
    return _trip_response(repository.get_trip(db, item.id))


def get_trip(db: Session, user: User, trip_id: str) -> TripResponse:
    return _trip_response(_trip(db, user, trip_id))


def update_trip(db: Session, user: User, trip_id: str, payload: TripUpdateRequest) -> TripResponse:
    item = _trip(db, user, trip_id)
    _vehicle(db, user, payload.vehicle_id)
    _validate_odometer(db, user, payload, trip_id)
    _apply_trip(item, payload)
    db.commit()
    return get_trip(db, user, trip_id)


def set_trip_archived(db: Session, user: User, trip_id: str, archived: bool) -> TripResponse:
    item = _trip(db, user, trip_id)
    item.archived = archived
    db.commit()
    return get_trip(db, user, trip_id)


def delete_trip(db: Session, user: User, trip_id: str) -> None:
    repository.delete(db, _trip(db, user, trip_id))
    db.commit()


def _filtered_trips(db: Session, user: User, q: str | None, vehicle_id: str | None, date_from: date | None, date_to: date | None, purpose: str | None, archive_filter: ArchiveFilter, sort_by: TripSort) -> list[DriverTrip]:
    trips = repository.list_trips(db, user.id)
    if archive_filter == "active":
        trips = [item for item in trips if not item.archived]
    elif archive_filter == "archived":
        trips = [item for item in trips if item.archived]
    if vehicle_id:
        trips = [item for item in trips if item.vehicle_id == vehicle_id]
    if date_from:
        trips = [item for item in trips if item.trip_date >= date_from]
    if date_to:
        trips = [item for item in trips if item.trip_date <= date_to]
    if purpose:
        trips = [item for item in trips if item.purpose == purpose]
    if q:
        needle = q.lower()
        trips = [item for item in trips if needle in " ".join([item.vehicle.vehicle_name, item.purpose, item.start_location or "", item.destination or "", item.notes or ""]).lower()]
    if sort_by == "distance":
        trips.sort(key=lambda item: item.distance, reverse=True)
    elif sort_by == "duration":
        trips.sort(key=lambda item: _duration_minutes(item) or 0, reverse=True)
    elif sort_by == "vehicle":
        trips.sort(key=lambda item: (item.vehicle.vehicle_name, item.trip_date))
    elif sort_by == "purpose":
        trips.sort(key=lambda item: (item.purpose, item.trip_date))
    elif sort_by == "created":
        trips.sort(key=lambda item: item.created_at, reverse=True)
    else:
        trips.sort(key=lambda item: (item.trip_date, item.created_at), reverse=True)
    return trips


def list_trips(db: Session, user: User, q: str | None, vehicle_id: str | None, date_from: date | None, date_to: date | None, purpose: str | None, archive_filter: ArchiveFilter, sort_by: TripSort, page: int, page_size: int) -> TripListResponse:
    trips = _filtered_trips(db, user, q, vehicle_id, date_from, date_to, purpose, archive_filter, sort_by)
    start = (page - 1) * page_size
    return TripListResponse(items=[_trip_response(item) for item in trips[start:start + page_size]], total=len(trips), page=page, page_size=page_size)


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    trips = [trip for trip in repository.list_trips(db, user.id) if not trip.archived]
    vehicles = [vehicle for vehicle in repository.list_vehicles(db, user.id) if not vehicle.archived]
    today = date.today()
    total_distance = sum((_distance(t.distance) for t in trips), Decimal("0.0"))
    month_distance = sum((_distance(t.distance) for t in trips if t.trip_date.year == today.year and t.trip_date.month == today.month), Decimal("0.0"))
    durations = [_duration_minutes(t) or 0 for t in trips]
    return DashboardResponse(total_trips=len(trips), total_distance=total_distance, monthly_distance=month_distance, driving_minutes=sum(durations), average_trip_distance=(total_distance / len(trips)).quantize(Decimal("0.1")) if trips else Decimal("0.0"), total_vehicles=len(vehicles))


def get_insights(db: Session, user: User) -> InsightsResponse:
    trips = [trip for trip in repository.list_trips(db, user.id) if not trip.archived]
    vehicles = repository.list_vehicles(db, user.id)
    dashboard = get_dashboard(db, user)
    distance_month: dict[str, Decimal] = defaultdict(lambda: Decimal("0.0"))
    distance_vehicle: dict[str, Decimal] = defaultdict(lambda: Decimal("0.0"))
    distance_purpose: dict[str, Decimal] = defaultdict(lambda: Decimal("0.0"))
    purpose_counts: Counter[str] = Counter()
    for trip in trips:
        distance_month[trip.trip_date.strftime("%Y-%m")] += _distance(trip.distance)
        distance_vehicle[trip.vehicle.vehicle_name] += _distance(trip.distance)
        distance_purpose[trip.purpose] += _distance(trip.distance)
        purpose_counts[trip.purpose] += 1
    sorted_trips = sorted(trips, key=lambda item: (item.trip_date, item.created_at), reverse=True)
    longest = max(trips, key=lambda item: item.distance, default=None)
    return InsightsResponse(**dashboard.model_dump(), vehicles=[_vehicle_response(v, trips) for v in vehicles], recent_trips=[_trip_response(t) for t in sorted_trips[:8]], distance_by_month=[DistanceItem(label=k, distance=v) for k, v in sorted(distance_month.items(), reverse=True)[:12]], distance_by_vehicle=[DistanceItem(label=k, distance=v) for k, v in sorted(distance_vehicle.items())], distance_by_purpose=[DistanceItem(label=k, distance=v) for k, v in sorted(distance_purpose.items())], trips_by_purpose=[CountItem(label=k, count=v) for k, v in purpose_counts.most_common()], longest_trip=_trip_response(longest) if longest else None)
