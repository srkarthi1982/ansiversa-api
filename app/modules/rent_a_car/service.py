from collections import Counter
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.rent_a_car import repository
from app.modules.rent_a_car.models import RentACarBooking, RentACarSearch, RentACarVehicleOption
from app.modules.rent_a_car.schemas import (
    RentACarBookingCreateRequest,
    RentACarBookingDetailResponse,
    RentACarBookingSummaryResponse,
    RentACarBookingUpdateRequest,
    RentACarClassDistributionResponse,
    RentACarDashboardResponse,
    RentACarProviderDistributionResponse,
    RentACarSearchCreateRequest,
    RentACarSearchDetailResponse,
    RentACarSearchDuplicateRequest,
    RentACarSearchSummaryResponse,
    RentACarSearchUpdateRequest,
    RentACarVehicleOptionCreateRequest,
    RentACarVehicleOptionDetailResponse,
    RentACarVehicleOptionDuplicateRequest,
    RentACarVehicleOptionSummaryResponse,
    RentACarVehicleOptionUpdateRequest,
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


def _estimated_total(option: RentACarVehicleOption) -> float:
    total = (option.daily_base_rate * option.rental_days) + option.taxes_and_fees + option.addon_estimate
    return round(total, 2)


def _get_owned_search(db: Session, user: User, search_id: str) -> RentACarSearch:
    search = repository.get_search(db, search_id)
    if not search or search.owner_id != user.id:
        _not_found("Rental search was not found.")
    return search


def _get_owned_option(db: Session, user: User, option_id: str) -> RentACarVehicleOption:
    option = repository.get_vehicle_option(db, option_id)
    if not option or option.owner_id != user.id:
        _not_found("Vehicle option was not found.")
    return option


def _get_owned_booking(db: Session, user: User, booking_id: str) -> RentACarBooking:
    booking = repository.get_booking(db, booking_id)
    if not booking or booking.owner_id != user.id:
        _not_found("Booking was not found.")
    return booking


def _validate_search_dates(pickup_at: str, return_at: str) -> None:
    if return_at <= pickup_at:
        _bad_request("Return date and time must be after pickup date and time.")


def _validate_option_parent(db: Session, user: User, search_id: str) -> RentACarSearch:
    return _get_owned_search(db, user, search_id)


def _validate_booking_links(db: Session, user: User, search_id: str, option_id: str | None) -> tuple[RentACarSearch, RentACarVehicleOption | None]:
    search = _get_owned_search(db, user, search_id)
    option = None
    if option_id:
        option = _get_owned_option(db, user, option_id)
        if option.search_id != search.id:
            _bad_request("Vehicle option must belong to the selected rental search.")
    return search, option


def _search_summary(search: RentACarSearch) -> RentACarSearchSummaryResponse:
    preferred = next((option for option in search.vehicle_options if option.is_preferred), None)
    return RentACarSearchSummaryResponse(
        id=search.id,
        title=search.title,
        pickup_location=search.pickup_location,
        dropoff_location=search.dropoff_location,
        pickup_at=search.pickup_at,
        return_at=search.return_at,
        vehicle_type=search.vehicle_type,
        transmission=search.transmission,
        passengers=search.passengers,
        luggage=search.luggage,
        budget=search.budget,
        currency_code=search.currency_code,
        notes_preview=_preview(search.notes),
        status=search.status,
        option_count=len(search.vehicle_options),
        booking_count=len(search.bookings),
        preferred_option_id=preferred.id if preferred else None,
        created_at=search.created_at,
        updated_at=search.updated_at,
    )


def _search_detail(search: RentACarSearch) -> RentACarSearchDetailResponse:
    return RentACarSearchDetailResponse(
        **_search_summary(search).model_dump(),
        driver_age_group=search.driver_age_group,
        notes=search.notes,
    )


def _option_summary(option: RentACarVehicleOption) -> RentACarVehicleOptionSummaryResponse:
    return RentACarVehicleOptionSummaryResponse(
        id=option.id,
        search_id=option.search_id,
        search_title=option.search.title if option.search else "Rental search",
        provider_name=option.provider_name,
        vehicle_name=option.vehicle_name,
        vehicle_class=option.vehicle_class,
        transmission=option.transmission,
        seats=option.seats,
        luggage_capacity=option.luggage_capacity,
        daily_base_rate=option.daily_base_rate,
        rental_days=option.rental_days,
        taxes_and_fees=option.taxes_and_fees,
        deposit=option.deposit,
        addon_estimate=option.addon_estimate,
        estimated_total=_estimated_total(option),
        notes_preview=_preview(option.notes),
        is_preferred=option.is_preferred,
        availability_status=option.availability_status,
        last_checked=option.last_checked,
        created_at=option.created_at,
        updated_at=option.updated_at,
    )


def _option_detail(option: RentACarVehicleOption) -> RentACarVehicleOptionDetailResponse:
    return RentACarVehicleOptionDetailResponse(
        **_option_summary(option).model_dump(),
        fuel_policy=option.fuel_policy,
        mileage_policy=option.mileage_policy,
        cancellation_terms=option.cancellation_terms,
        pickup_method=option.pickup_method,
        reference_url=option.reference_url,
        notes=option.notes,
    )


def _booking_summary(booking: RentACarBooking) -> RentACarBookingSummaryResponse:
    return RentACarBookingSummaryResponse(
        id=booking.id,
        search_id=booking.search_id,
        search_title=booking.search.title if booking.search else "Rental search",
        vehicle_option_id=booking.vehicle_option_id,
        vehicle_name=booking.vehicle_option.vehicle_name if booking.vehicle_option else None,
        booking_reference=booking.booking_reference,
        provider_name=booking.provider_name,
        confirmed_total=booking.confirmed_total,
        currency_code=booking.currency_code,
        deposit_amount=booking.deposit_amount,
        booking_date=booking.booking_date,
        cancellation_deadline=booking.cancellation_deadline,
        status=booking.status,
        notes_preview=_preview(booking.notes),
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


def _booking_detail(booking: RentACarBooking) -> RentACarBookingDetailResponse:
    return RentACarBookingDetailResponse(
        **_booking_summary(booking).model_dump(),
        pickup_instructions=booking.pickup_instructions,
        dropoff_instructions=booking.dropoff_instructions,
        contact_information=booking.contact_information,
        notes=booking.notes,
    )


def _unset_preferred_options(db: Session, owner_id: str, search_id: str, except_option_id: str | None = None) -> None:
    for option in repository.list_vehicle_options_for_search(db, owner_id, search_id):
        if option.search_id == search_id and option.id != except_option_id:
            option.is_preferred = False


def list_searches(db: Session, user: User) -> list[RentACarSearchSummaryResponse]:
    return [_search_summary(search) for search in repository.list_searches(db, user.id)]


def create_search(db: Session, user: User, payload: RentACarSearchCreateRequest) -> RentACarSearchDetailResponse:
    data = payload.model_dump()
    _validate_search_dates(data["pickup_at"], data["return_at"])
    search = RentACarSearch(owner_id=user.id, **data)
    repository.add(db, search)
    db.commit()
    db.refresh(search)
    return _search_detail(search)


def get_search(db: Session, user: User, search_id: str) -> RentACarSearchDetailResponse:
    return _search_detail(_get_owned_search(db, user, search_id))


def update_search(db: Session, user: User, search_id: str, payload: RentACarSearchUpdateRequest) -> RentACarSearchDetailResponse:
    search = _get_owned_search(db, user, search_id)
    data = payload.model_dump(exclude_unset=True)
    pickup_at = data.get("pickup_at", search.pickup_at)
    return_at = data.get("return_at", search.return_at)
    _validate_search_dates(pickup_at, return_at)
    for field, value in data.items():
        setattr(search, field, value)
    db.commit()
    db.refresh(search)
    return _search_detail(search)


def duplicate_search(db: Session, user: User, search_id: str, payload: RentACarSearchDuplicateRequest) -> RentACarSearchDetailResponse:
    search = _get_owned_search(db, user, search_id)
    duplicate = RentACarSearch(
        owner_id=user.id,
        title=payload.title or f"{search.title} copy",
        pickup_location=search.pickup_location,
        dropoff_location=search.dropoff_location,
        pickup_at=search.pickup_at,
        return_at=search.return_at,
        driver_age_group=search.driver_age_group,
        vehicle_type=search.vehicle_type,
        transmission=search.transmission,
        passengers=search.passengers,
        luggage=search.luggage,
        budget=search.budget,
        currency_code=search.currency_code,
        notes=search.notes,
        status="planning",
    )
    repository.add(db, duplicate)
    db.commit()
    db.refresh(duplicate)
    return _search_detail(duplicate)


def delete_search(db: Session, user: User, search_id: str) -> None:
    search = _get_owned_search(db, user, search_id)
    repository.delete_record(db, search)
    db.commit()


def list_vehicle_options(db: Session, user: User) -> list[RentACarVehicleOptionSummaryResponse]:
    return [_option_summary(option) for option in repository.list_vehicle_options(db, user.id)]


def create_vehicle_option(db: Session, user: User, payload: RentACarVehicleOptionCreateRequest) -> RentACarVehicleOptionDetailResponse:
    data = payload.model_dump()
    _validate_option_parent(db, user, data["search_id"])
    if data.get("is_preferred"):
        _unset_preferred_options(db, user.id, data["search_id"])
    option = RentACarVehicleOption(owner_id=user.id, **data)
    repository.add(db, option)
    db.commit()
    db.refresh(option)
    return _option_detail(option)


def get_vehicle_option(db: Session, user: User, option_id: str) -> RentACarVehicleOptionDetailResponse:
    return _option_detail(_get_owned_option(db, user, option_id))


def update_vehicle_option(db: Session, user: User, option_id: str, payload: RentACarVehicleOptionUpdateRequest) -> RentACarVehicleOptionDetailResponse:
    option = _get_owned_option(db, user, option_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_preferred"):
        _unset_preferred_options(db, user.id, option.search_id, except_option_id=option.id)
    for field, value in data.items():
        setattr(option, field, value)
    db.commit()
    db.refresh(option)
    return _option_detail(option)


def duplicate_vehicle_option(db: Session, user: User, option_id: str, payload: RentACarVehicleOptionDuplicateRequest) -> RentACarVehicleOptionDetailResponse:
    option = _get_owned_option(db, user, option_id)
    duplicate = RentACarVehicleOption(
        owner_id=user.id,
        search_id=option.search_id,
        provider_name=option.provider_name,
        vehicle_name=payload.vehicle_name or f"{option.vehicle_name} copy",
        vehicle_class=option.vehicle_class,
        transmission=option.transmission,
        fuel_policy=option.fuel_policy,
        seats=option.seats,
        luggage_capacity=option.luggage_capacity,
        daily_base_rate=option.daily_base_rate,
        rental_days=option.rental_days,
        taxes_and_fees=option.taxes_and_fees,
        deposit=option.deposit,
        addon_estimate=option.addon_estimate,
        mileage_policy=option.mileage_policy,
        cancellation_terms=option.cancellation_terms,
        pickup_method=option.pickup_method,
        reference_url=option.reference_url,
        last_checked=option.last_checked,
        notes=option.notes,
        is_preferred=False,
        availability_status=option.availability_status,
    )
    repository.add(db, duplicate)
    db.commit()
    db.refresh(duplicate)
    return _option_detail(duplicate)


def mark_vehicle_option_preferred(db: Session, user: User, option_id: str) -> RentACarVehicleOptionDetailResponse:
    option = _get_owned_option(db, user, option_id)
    _unset_preferred_options(db, user.id, option.search_id, except_option_id=option.id)
    option.is_preferred = True
    db.commit()
    db.refresh(option)
    return _option_detail(option)


def unmark_vehicle_option_preferred(db: Session, user: User, option_id: str) -> RentACarVehicleOptionDetailResponse:
    option = _get_owned_option(db, user, option_id)
    option.is_preferred = False
    db.commit()
    db.refresh(option)
    return _option_detail(option)


def delete_vehicle_option(db: Session, user: User, option_id: str) -> None:
    option = _get_owned_option(db, user, option_id)
    for booking in option.bookings:
        booking.vehicle_option_id = None
    repository.delete_record(db, option)
    db.commit()


def list_bookings(db: Session, user: User) -> list[RentACarBookingSummaryResponse]:
    return [_booking_summary(booking) for booking in repository.list_bookings(db, user.id)]


def create_booking(db: Session, user: User, payload: RentACarBookingCreateRequest) -> RentACarBookingDetailResponse:
    data = payload.model_dump()
    _validate_booking_links(db, user, data["search_id"], data.get("vehicle_option_id"))
    booking = RentACarBooking(owner_id=user.id, **data)
    repository.add(db, booking)
    db.commit()
    db.refresh(booking)
    return _booking_detail(booking)


def get_booking(db: Session, user: User, booking_id: str) -> RentACarBookingDetailResponse:
    return _booking_detail(_get_owned_booking(db, user, booking_id))


def update_booking(db: Session, user: User, booking_id: str, payload: RentACarBookingUpdateRequest) -> RentACarBookingDetailResponse:
    booking = _get_owned_booking(db, user, booking_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(booking, field, value)
    db.commit()
    db.refresh(booking)
    return _booking_detail(booking)


def delete_booking(db: Session, user: User, booking_id: str) -> None:
    booking = _get_owned_booking(db, user, booking_id)
    repository.delete_record(db, booking)
    db.commit()


def get_dashboard(db: Session, user: User) -> RentACarDashboardResponse:
    searches = [_search_summary(search) for search in repository.list_searches(db, user.id)]
    options = [_option_summary(option) for option in repository.list_vehicle_options(db, user.id)]
    bookings = [_booking_summary(booking) for booking in repository.list_bookings(db, user.id)]
    today = _today()
    active_bookings = [booking for booking in bookings if booking.status == "confirmed"]
    upcoming_bookings = [booking for booking in active_bookings if booking.booking_date >= today]
    completed_bookings = [booking for booking in bookings if booking.status == "completed"]
    average_rate = round(sum(option.daily_base_rate for option in options) / len(options), 2) if options else 0
    provider_counts = Counter(option.provider_name for option in options)
    class_counts = Counter(option.vehicle_class for option in options)
    cancellation_deadlines = sorted(
        [booking for booking in active_bookings if booking.cancellation_deadline and booking.cancellation_deadline >= today],
        key=lambda booking: booking.cancellation_deadline or "",
    )[:8]
    return RentACarDashboardResponse(
        searches=searches,
        vehicle_options=options,
        bookings=bookings,
        total_searches=len(searches),
        comparing_searches=len([search for search in searches if search.status == "comparing"]),
        confirmed_bookings=len(active_bookings),
        upcoming_bookings=len(upcoming_bookings),
        completed_bookings=len(completed_bookings),
        average_estimated_daily_rate=average_rate,
        estimated_total_spend=round(sum(booking.confirmed_total for booking in bookings), 2),
        most_used_class=class_counts.most_common(1)[0][0] if class_counts else None,
        most_used_provider=provider_counts.most_common(1)[0][0] if provider_counts else None,
        recently_updated_searches=sorted(searches, key=lambda search: search.updated_at, reverse=True)[:8],
        upcoming_cancellation_deadlines=cancellation_deadlines,
        provider_distribution=[
            RentACarProviderDistributionResponse(provider_name=name, option_count=count)
            for name, count in provider_counts.most_common()
        ],
        class_distribution=[
            RentACarClassDistributionResponse(vehicle_class=name, option_count=count)
            for name, count in class_counts.most_common()
        ],
    )
