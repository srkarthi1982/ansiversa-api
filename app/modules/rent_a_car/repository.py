from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.rent_a_car.models import RentACarBooking, RentACarSearch, RentACarVehicleOption


def get_search(db: Session, search_id: str) -> RentACarSearch | None:
    return db.get(RentACarSearch, search_id)


def get_vehicle_option(db: Session, option_id: str) -> RentACarVehicleOption | None:
    return db.get(RentACarVehicleOption, option_id)


def get_booking(db: Session, booking_id: str) -> RentACarBooking | None:
    return db.get(RentACarBooking, booking_id)


def list_searches(db: Session, owner_id: str) -> list[RentACarSearch]:
    return list(
        db.execute(
            select(RentACarSearch)
            .options(joinedload(RentACarSearch.vehicle_options), joinedload(RentACarSearch.bookings))
            .where(RentACarSearch.owner_id == owner_id)
            .order_by(RentACarSearch.pickup_at.asc(), RentACarSearch.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_vehicle_options(db: Session, owner_id: str) -> list[RentACarVehicleOption]:
    return list(
        db.execute(
            select(RentACarVehicleOption)
            .options(joinedload(RentACarVehicleOption.search))
            .where(RentACarVehicleOption.owner_id == owner_id)
            .order_by(RentACarVehicleOption.is_preferred.desc(), RentACarVehicleOption.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_vehicle_options_for_search(db: Session, owner_id: str, search_id: str) -> list[RentACarVehicleOption]:
    return list(
        db.execute(
            select(RentACarVehicleOption)
            .options(joinedload(RentACarVehicleOption.search))
            .where(RentACarVehicleOption.owner_id == owner_id, RentACarVehicleOption.search_id == search_id)
            .order_by(RentACarVehicleOption.is_preferred.desc(), RentACarVehicleOption.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_bookings(db: Session, owner_id: str) -> list[RentACarBooking]:
    return list(
        db.execute(
            select(RentACarBooking)
            .options(joinedload(RentACarBooking.search), joinedload(RentACarBooking.vehicle_option))
            .where(RentACarBooking.owner_id == owner_id)
            .order_by(RentACarBooking.booking_date.desc(), RentACarBooking.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
