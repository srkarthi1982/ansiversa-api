from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.vehicle_maintenance_tracker.models import (
    VehicleMaintenanceRecord,
    VehicleMaintenanceReminder,
    VehicleMaintenanceVehicle,
)


def get_vehicle(db: Session, vehicle_id: str) -> VehicleMaintenanceVehicle | None:
    return db.get(VehicleMaintenanceVehicle, vehicle_id)


def get_record(db: Session, record_id: str) -> VehicleMaintenanceRecord | None:
    return db.get(VehicleMaintenanceRecord, record_id)


def get_reminder(db: Session, reminder_id: str) -> VehicleMaintenanceReminder | None:
    return db.get(VehicleMaintenanceReminder, reminder_id)


def list_vehicles(db: Session, owner_id: str) -> list[VehicleMaintenanceVehicle]:
    return list(
        db.execute(
            select(VehicleMaintenanceVehicle)
            .options(joinedload(VehicleMaintenanceVehicle.records), joinedload(VehicleMaintenanceVehicle.reminders))
            .where(VehicleMaintenanceVehicle.owner_id == owner_id)
            .order_by(VehicleMaintenanceVehicle.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_records(db: Session, owner_id: str) -> list[VehicleMaintenanceRecord]:
    return list(
        db.execute(
            select(VehicleMaintenanceRecord)
            .options(joinedload(VehicleMaintenanceRecord.vehicle))
            .where(VehicleMaintenanceRecord.owner_id == owner_id)
            .order_by(VehicleMaintenanceRecord.service_date.desc(), VehicleMaintenanceRecord.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_reminders(db: Session, owner_id: str) -> list[VehicleMaintenanceReminder]:
    return list(
        db.execute(
            select(VehicleMaintenanceReminder)
            .options(joinedload(VehicleMaintenanceReminder.vehicle))
            .where(VehicleMaintenanceReminder.owner_id == owner_id)
            .order_by(VehicleMaintenanceReminder.due_date.asc(), VehicleMaintenanceReminder.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
