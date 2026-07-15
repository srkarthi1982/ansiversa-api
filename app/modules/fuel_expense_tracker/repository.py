from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.fuel_expense_tracker.models import FuelEntry, FuelVehicle


def add(db: Session, item):
    db.add(item)
    return item


def delete(db: Session, item) -> None:
    db.delete(item)


def list_vehicles(db: Session, owner_id: str) -> list[FuelVehicle]:
    return list(db.scalars(select(FuelVehicle).where(FuelVehicle.owner_id == owner_id).order_by(FuelVehicle.archived, FuelVehicle.vehicle_name)))


def get_vehicle(db: Session, item_id: str) -> FuelVehicle | None:
    return db.get(FuelVehicle, item_id)


def list_entries(db: Session, owner_id: str) -> list[FuelEntry]:
    result = db.execute(select(FuelEntry).options(joinedload(FuelEntry.vehicle)).where(FuelEntry.owner_id == owner_id).order_by(FuelEntry.purchase_date.desc(), FuelEntry.created_at.desc()))
    return list(result.unique().scalars())


def get_entry(db: Session, item_id: str) -> FuelEntry | None:
    result = db.execute(select(FuelEntry).options(joinedload(FuelEntry.vehicle)).where(FuelEntry.id == item_id))
    return result.unique().scalars().first()


def count_entries_for_vehicle(db: Session, owner_id: str, vehicle_id: str) -> int:
    return db.scalar(select(func.count()).select_from(FuelEntry).where(FuelEntry.owner_id == owner_id, FuelEntry.vehicle_id == vehicle_id)) or 0
