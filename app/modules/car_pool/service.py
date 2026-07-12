from collections import defaultdict
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.car_pool import repository
from app.modules.car_pool.models import CarPoolPassenger, CarPoolRequest, CarPoolRide
from app.modules.car_pool.schemas import (
    CarPoolDashboardResponse,
    CarPoolPassengerDetailResponse,
    CarPoolPassengerJoinRequest,
    CarPoolPassengerSummaryResponse,
    CarPoolPassengerUpdateRequest,
    CarPoolRequestCreateRequest,
    CarPoolRequestDecisionRequest,
    CarPoolRequestDetailResponse,
    CarPoolRequestSummaryResponse,
    CarPoolRequestUpdateRequest,
    CarPoolRideCreateRequest,
    CarPoolRideDetailResponse,
    CarPoolRideDuplicateRequest,
    CarPoolRideSummaryResponse,
    CarPoolRideUpdateRequest,
    CarPoolWeeklyActivityResponse,
)

PREVIEW_LENGTH = 220


def _today() -> str:
    return date.today().isoformat()


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _week_key(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def _get_owned_ride(db: Session, user: User, ride_id: str) -> CarPoolRide:
    ride = repository.get_ride(db, ride_id)
    if not ride or ride.owner_id != user.id:
        _not_found("Ride was not found.")
    return ride


def _get_owned_passenger(db: Session, user: User, passenger_id: str) -> CarPoolPassenger:
    passenger = repository.get_passenger(db, passenger_id)
    if not passenger or passenger.owner_id != user.id:
        _not_found("Trip was not found.")
    return passenger


def _get_owned_request(db: Session, user: User, request_id: str) -> CarPoolRequest:
    request = repository.get_request(db, request_id)
    if not request or request.owner_id != user.id:
        _not_found("Request was not found.")
    return request


def _available_seats(ride: CarPoolRide) -> int:
    return max(ride.seats_offered - ride.seats_filled, 0)


def _validate_ride_seats(seats_offered: int, seats_filled: int) -> None:
    if seats_filled > seats_offered:
        _bad_request("Seats filled cannot exceed seats offered.")


def _ride_summary(ride: CarPoolRide) -> CarPoolRideSummaryResponse:
    pending = [request for request in ride.requests if request.status == "pending"]
    return CarPoolRideSummaryResponse(
        id=ride.id,
        title=ride.title,
        origin=ride.origin,
        destination=ride.destination,
        departure_at=ride.departure_at,
        return_at=ride.return_at,
        meeting_point=ride.meeting_point,
        vehicle_label=ride.vehicle_label,
        seats_offered=ride.seats_offered,
        seats_filled=ride.seats_filled,
        available_seats=_available_seats(ride),
        price_per_seat=ride.price_per_seat,
        currency_code=ride.currency_code,
        recurrence=ride.recurrence,
        status=ride.status,
        visibility=ride.visibility,
        notes_preview=_preview(ride.notes),
        passenger_count=len([passenger for passenger in ride.passengers if passenger.status == "joined"]),
        request_count=len(ride.requests),
        pending_request_count=len(pending),
        created_at=ride.created_at,
        updated_at=ride.updated_at,
    )


def _ride_detail(ride: CarPoolRide) -> CarPoolRideDetailResponse:
    return CarPoolRideDetailResponse(**_ride_summary(ride).model_dump(), driver_name=ride.driver_name, notes=ride.notes)


def _passenger_summary(passenger: CarPoolPassenger) -> CarPoolPassengerSummaryResponse:
    ride = passenger.ride
    return CarPoolPassengerSummaryResponse(
        id=passenger.id,
        ride_id=passenger.ride_id,
        ride_title=ride.title if ride else "Ride",
        origin=ride.origin if ride else "",
        destination=ride.destination if ride else "",
        departure_at=ride.departure_at if ride else "",
        passenger_name=passenger.passenger_name,
        seats=passenger.seats,
        contact_note=passenger.contact_note,
        joined_at=passenger.joined_at,
        status=passenger.status,
        notes_preview=_preview(passenger.notes),
        created_at=passenger.created_at,
        updated_at=passenger.updated_at,
    )


def _passenger_detail(passenger: CarPoolPassenger) -> CarPoolPassengerDetailResponse:
    return CarPoolPassengerDetailResponse(**_passenger_summary(passenger).model_dump(), notes=passenger.notes)


def _request_summary(request: CarPoolRequest) -> CarPoolRequestSummaryResponse:
    ride = request.ride
    return CarPoolRequestSummaryResponse(
        id=request.id,
        ride_id=request.ride_id,
        ride_title=ride.title if ride else "Ride",
        origin=ride.origin if ride else "",
        destination=ride.destination if ride else "",
        departure_at=ride.departure_at if ride else "",
        requester_name=request.requester_name,
        seats_requested=request.seats_requested,
        pickup_note=request.pickup_note,
        message_preview=_preview(request.message),
        requested_at=request.requested_at,
        status=request.status,
        response_note=request.response_note,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


def _request_detail(request: CarPoolRequest) -> CarPoolRequestDetailResponse:
    return CarPoolRequestDetailResponse(**_request_summary(request).model_dump(), message=request.message)


def list_rides(db: Session, user: User) -> list[CarPoolRideSummaryResponse]:
    return [_ride_summary(ride) for ride in repository.list_rides(db, user.id)]


def create_ride(db: Session, user: User, payload: CarPoolRideCreateRequest) -> CarPoolRideDetailResponse:
    data = payload.model_dump()
    _validate_ride_seats(data["seats_offered"], data["seats_filled"])
    ride = CarPoolRide(owner_id=user.id, **data)
    repository.add(db, ride)
    db.commit()
    db.refresh(ride)
    return _ride_detail(ride)


def get_ride(db: Session, user: User, ride_id: str) -> CarPoolRideDetailResponse:
    return _ride_detail(_get_owned_ride(db, user, ride_id))


def update_ride(db: Session, user: User, ride_id: str, payload: CarPoolRideUpdateRequest) -> CarPoolRideDetailResponse:
    ride = _get_owned_ride(db, user, ride_id)
    data = payload.model_dump(exclude_unset=True)
    seats_offered = data.get("seats_offered", ride.seats_offered)
    seats_filled = data.get("seats_filled", ride.seats_filled)
    _validate_ride_seats(seats_offered, seats_filled)
    for field, value in data.items():
        setattr(ride, field, value)
    db.commit()
    db.refresh(ride)
    return _ride_detail(ride)


def duplicate_ride(db: Session, user: User, ride_id: str, payload: CarPoolRideDuplicateRequest) -> CarPoolRideDetailResponse:
    ride = _get_owned_ride(db, user, ride_id)
    duplicate = CarPoolRide(
        owner_id=user.id,
        title=payload.title or f"{ride.title} copy",
        origin=ride.origin,
        destination=ride.destination,
        departure_at=ride.departure_at,
        return_at=ride.return_at,
        meeting_point=ride.meeting_point,
        vehicle_label=ride.vehicle_label,
        driver_name=ride.driver_name,
        seats_offered=ride.seats_offered,
        seats_filled=0,
        price_per_seat=ride.price_per_seat,
        currency_code=ride.currency_code,
        recurrence=ride.recurrence,
        status="open",
        visibility=ride.visibility,
        notes=ride.notes,
    )
    repository.add(db, duplicate)
    db.commit()
    db.refresh(duplicate)
    return _ride_detail(duplicate)


def delete_ride(db: Session, user: User, ride_id: str) -> None:
    ride = _get_owned_ride(db, user, ride_id)
    repository.delete_record(db, ride)
    db.commit()


def list_passengers(db: Session, user: User) -> list[CarPoolPassengerSummaryResponse]:
    return [_passenger_summary(passenger) for passenger in repository.list_passengers(db, user.id)]


def join_ride(db: Session, user: User, payload: CarPoolPassengerJoinRequest) -> CarPoolPassengerDetailResponse:
    data = payload.model_dump()
    ride = _get_owned_ride(db, user, data["ride_id"])
    if ride.status in {"completed", "cancelled"}:
        _bad_request("Completed or cancelled rides cannot be joined.")
    if data["seats"] > _available_seats(ride):
        _bad_request("Not enough available seats remain on this ride.")
    passenger = CarPoolPassenger(owner_id=user.id, status="joined", **data)
    ride.seats_filled += data["seats"]
    if ride.seats_filled >= ride.seats_offered:
        ride.status = "full"
    repository.add(db, passenger)
    db.commit()
    db.refresh(passenger)
    return _passenger_detail(passenger)


def get_passenger(db: Session, user: User, passenger_id: str) -> CarPoolPassengerDetailResponse:
    return _passenger_detail(_get_owned_passenger(db, user, passenger_id))


def update_passenger(db: Session, user: User, passenger_id: str, payload: CarPoolPassengerUpdateRequest) -> CarPoolPassengerDetailResponse:
    passenger = _get_owned_passenger(db, user, passenger_id)
    data = payload.model_dump(exclude_unset=True)
    old_joined_seats = passenger.seats if passenger.status == "joined" else 0
    new_status = data.get("status", passenger.status)
    new_seats = data.get("seats", passenger.seats)
    new_joined_seats = new_seats if new_status == "joined" else 0
    seat_delta = new_joined_seats - old_joined_seats
    if seat_delta > _available_seats(passenger.ride):
        _bad_request("Not enough available seats remain on this ride.")
    for field, value in data.items():
        setattr(passenger, field, value)
    passenger.ride.seats_filled = max(passenger.ride.seats_filled + seat_delta, 0)
    if passenger.ride.status == "full" and passenger.ride.seats_filled < passenger.ride.seats_offered:
        passenger.ride.status = "open"
    db.commit()
    db.refresh(passenger)
    return _passenger_detail(passenger)


def leave_trip(db: Session, user: User, passenger_id: str) -> CarPoolPassengerDetailResponse:
    passenger = _get_owned_passenger(db, user, passenger_id)
    if passenger.status == "joined":
        passenger.ride.seats_filled = max(passenger.ride.seats_filled - passenger.seats, 0)
        if passenger.ride.status == "full":
            passenger.ride.status = "open"
    passenger.status = "left"
    db.commit()
    db.refresh(passenger)
    return _passenger_detail(passenger)


def delete_passenger(db: Session, user: User, passenger_id: str) -> None:
    passenger = _get_owned_passenger(db, user, passenger_id)
    if passenger.status == "joined":
        passenger.ride.seats_filled = max(passenger.ride.seats_filled - passenger.seats, 0)
    repository.delete_record(db, passenger)
    db.commit()


def list_requests(db: Session, user: User) -> list[CarPoolRequestSummaryResponse]:
    return [_request_summary(request) for request in repository.list_requests(db, user.id)]


def create_request(db: Session, user: User, payload: CarPoolRequestCreateRequest) -> CarPoolRequestDetailResponse:
    data = payload.model_dump()
    _get_owned_ride(db, user, data["ride_id"])
    request = CarPoolRequest(owner_id=user.id, status="pending", **data)
    repository.add(db, request)
    db.commit()
    db.refresh(request)
    return _request_detail(request)


def get_request(db: Session, user: User, request_id: str) -> CarPoolRequestDetailResponse:
    return _request_detail(_get_owned_request(db, user, request_id))


def update_request(db: Session, user: User, request_id: str, payload: CarPoolRequestUpdateRequest) -> CarPoolRequestDetailResponse:
    request = _get_owned_request(db, user, request_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(request, field, value)
    db.commit()
    db.refresh(request)
    return _request_detail(request)


def approve_request(db: Session, user: User, request_id: str, payload: CarPoolRequestDecisionRequest) -> CarPoolRequestDetailResponse:
    request = _get_owned_request(db, user, request_id)
    request.status = "approved"
    request.response_note = payload.response_note
    db.commit()
    db.refresh(request)
    return _request_detail(request)


def reject_request(db: Session, user: User, request_id: str, payload: CarPoolRequestDecisionRequest) -> CarPoolRequestDetailResponse:
    request = _get_owned_request(db, user, request_id)
    request.status = "rejected"
    request.response_note = payload.response_note
    db.commit()
    db.refresh(request)
    return _request_detail(request)


def delete_request(db: Session, user: User, request_id: str) -> None:
    request = _get_owned_request(db, user, request_id)
    repository.delete_record(db, request)
    db.commit()


def get_dashboard(db: Session, user: User) -> CarPoolDashboardResponse:
    rides = [_ride_summary(ride) for ride in repository.list_rides(db, user.id)]
    passengers = [_passenger_summary(passenger) for passenger in repository.list_passengers(db, user.id)]
    requests = [_request_summary(request) for request in repository.list_requests(db, user.id)]
    today = _today()
    completed_rides = [ride for ride in rides if ride.status == "completed"]
    cancelled_rides = [ride for ride in rides if ride.status == "cancelled"]
    upcoming_trips = [trip for trip in passengers if trip.status == "joined" and trip.departure_at >= today]
    past_trips = [trip for trip in passengers if trip.status in {"completed", "left", "cancelled"} or trip.departure_at < today]
    weekly: dict[str, dict[str, int]] = defaultdict(lambda: {"rides": 0, "trips": 0, "requests": 0})
    for ride in rides:
        weekly[_week_key(ride.created_at)]["rides"] += 1
    for trip in passengers:
        weekly[_week_key(trip.created_at)]["trips"] += 1
    for request in requests:
        weekly[_week_key(request.created_at)]["requests"] += 1
    return CarPoolDashboardResponse(
        rides=rides,
        passengers=passengers,
        requests=requests,
        total_rides=len(rides),
        seats_offered=sum(ride.seats_offered for ride in rides),
        seats_filled=sum(ride.seats_filled for ride in rides),
        trips_completed=len(completed_rides) + len([trip for trip in passengers if trip.status == "completed"]),
        cancellation_rate=round((len(cancelled_rides) / len(rides)) * 100, 1) if rides else 0,
        pending_requests=len([request for request in requests if request.status == "pending"]),
        approved_requests=len([request for request in requests if request.status == "approved"]),
        rejected_requests=len([request for request in requests if request.status == "rejected"]),
        upcoming_trips=sorted(upcoming_trips, key=lambda trip: trip.departure_at)[:8],
        past_trips=sorted(past_trips, key=lambda trip: trip.departure_at, reverse=True)[:8],
        recently_updated_rides=sorted(rides, key=lambda ride: ride.updated_at, reverse=True)[:8],
        weekly_activity=[
            CarPoolWeeklyActivityResponse(week=week, ride_count=counts["rides"], trip_count=counts["trips"], request_count=counts["requests"])
            for week, counts in sorted(weekly.items())[-8:]
        ],
    )
