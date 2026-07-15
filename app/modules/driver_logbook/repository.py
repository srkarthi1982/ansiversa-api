from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.driver_logbook.models import DriverTrip, DriverVehicle


def add(db: Session, item):
    db.add(item)
    return item


def delete(db: Session, item) -> None:
    db.delete(item)


def list_vehicles(db: Session, owner_id: str) -> list[DriverVehicle]:
    return list(db.scalars(select(DriverVehicle).where(DriverVehicle.owner_id == owner_id).order_by(DriverVehicle.archived, DriverVehicle.vehicle_name)))


def get_vehicle(db: Session, item_id: str) -> DriverVehicle | None:
    return db.get(DriverVehicle, item_id)


def list_trips(db: Session, owner_id: str) -> list[DriverTrip]:
    result = db.execute(select(DriverTrip).options(joinedload(DriverTrip.vehicle)).where(DriverTrip.owner_id == owner_id).order_by(DriverTrip.trip_date.desc(), DriverTrip.created_at.desc()))
    return list(result.unique().scalars())


def get_trip(db: Session, item_id: str) -> DriverTrip | None:
    result = db.execute(select(DriverTrip).options(joinedload(DriverTrip.vehicle)).where(DriverTrip.id == item_id))
    return result.unique().scalars().first()


def count_trips_for_vehicle(db: Session, owner_id: str, vehicle_id: str) -> int:
    return db.scalar(select(func.count()).select_from(DriverTrip).where(DriverTrip.owner_id == owner_id, DriverTrip.vehicle_id == vehicle_id)) or 0
