from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.car_pool.models import CarPoolPassenger, CarPoolRequest, CarPoolRide


def get_ride(db: Session, ride_id: str) -> CarPoolRide | None:
    return db.get(CarPoolRide, ride_id)


def get_passenger(db: Session, passenger_id: str) -> CarPoolPassenger | None:
    return db.get(CarPoolPassenger, passenger_id)


def get_request(db: Session, request_id: str) -> CarPoolRequest | None:
    return db.get(CarPoolRequest, request_id)


def list_rides(db: Session, owner_id: str) -> list[CarPoolRide]:
    return list(
        db.execute(
            select(CarPoolRide)
            .options(joinedload(CarPoolRide.passengers), joinedload(CarPoolRide.requests))
            .where(CarPoolRide.owner_id == owner_id)
            .order_by(CarPoolRide.departure_at.asc(), CarPoolRide.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_passengers(db: Session, owner_id: str) -> list[CarPoolPassenger]:
    return list(
        db.execute(
            select(CarPoolPassenger)
            .options(joinedload(CarPoolPassenger.ride))
            .where(CarPoolPassenger.owner_id == owner_id)
            .order_by(CarPoolPassenger.joined_at.desc(), CarPoolPassenger.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_requests(db: Session, owner_id: str) -> list[CarPoolRequest]:
    return list(
        db.execute(
            select(CarPoolRequest)
            .options(joinedload(CarPoolRequest.ride))
            .where(CarPoolRequest.owner_id == owner_id)
            .order_by(CarPoolRequest.requested_at.desc(), CarPoolRequest.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
