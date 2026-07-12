from collections import Counter, defaultdict
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.vehicle_maintenance_tracker import repository
from app.modules.vehicle_maintenance_tracker.models import (
    VehicleMaintenanceRecord,
    VehicleMaintenanceReminder,
    VehicleMaintenanceVehicle,
)
from app.modules.vehicle_maintenance_tracker.schemas import (
    VehicleMaintenanceDashboardResponse,
    VehicleMaintenanceMonthlyActivityResponse,
    VehicleMaintenanceRecordCreateRequest,
    VehicleMaintenanceRecordDetailResponse,
    VehicleMaintenanceRecordSummaryResponse,
    VehicleMaintenanceRecordUpdateRequest,
    VehicleMaintenanceReminderCreateRequest,
    VehicleMaintenanceReminderDetailResponse,
    VehicleMaintenanceReminderSummaryResponse,
    VehicleMaintenanceReminderUpdateRequest,
    VehicleMaintenanceServiceFrequencyResponse,
    VehicleMaintenanceVehicleCreateRequest,
    VehicleMaintenanceVehicleDetailResponse,
    VehicleMaintenanceVehicleDuplicateRequest,
    VehicleMaintenanceVehicleSummaryResponse,
    VehicleMaintenanceVehicleUpdateRequest,
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


def _get_owned_vehicle(db: Session, user: User, vehicle_id: str) -> VehicleMaintenanceVehicle:
    vehicle = repository.get_vehicle(db, vehicle_id)
    if not vehicle or vehicle.owner_id != user.id:
        _not_found("Vehicle was not found.")
    return vehicle


def _get_owned_record(db: Session, user: User, record_id: str) -> VehicleMaintenanceRecord:
    record = repository.get_record(db, record_id)
    if not record or record.owner_id != user.id:
        _not_found("Maintenance record was not found.")
    return record


def _get_owned_reminder(db: Session, user: User, reminder_id: str) -> VehicleMaintenanceReminder:
    reminder = repository.get_reminder(db, reminder_id)
    if not reminder or reminder.owner_id != user.id:
        _not_found("Reminder was not found.")
    return reminder


def _month_key(value: str) -> str:
    return value[:7] if len(value) >= 7 else value


def _vehicle_summary(vehicle: VehicleMaintenanceVehicle) -> VehicleMaintenanceVehicleSummaryResponse:
    reminders = list(vehicle.reminders)
    return VehicleMaintenanceVehicleSummaryResponse(
        id=vehicle.id,
        name=vehicle.name,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        plate_number=vehicle.plate_number,
        odometer=vehicle.odometer,
        fuel_type=vehicle.fuel_type,
        status=vehicle.status,
        notes_preview=_preview(vehicle.notes),
        record_count=len(vehicle.records),
        reminder_count=len(reminders),
        upcoming_reminder_count=len([item for item in reminders if item.status == "upcoming"]),
        overdue_reminder_count=len([item for item in reminders if item.status == "overdue"]),
        total_cost=round(sum(record.cost for record in vehicle.records), 2),
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
    )


def _vehicle_detail(vehicle: VehicleMaintenanceVehicle) -> VehicleMaintenanceVehicleDetailResponse:
    return VehicleMaintenanceVehicleDetailResponse(**_vehicle_summary(vehicle).model_dump(), vin=vehicle.vin, notes=vehicle.notes)


def _record_summary(record: VehicleMaintenanceRecord) -> VehicleMaintenanceRecordSummaryResponse:
    return VehicleMaintenanceRecordSummaryResponse(
        id=record.id,
        vehicle_id=record.vehicle_id,
        vehicle_name=record.vehicle.name if record.vehicle else "Vehicle",
        title=record.title,
        service_date=record.service_date,
        category=record.category,
        odometer=record.odometer,
        cost=record.cost,
        currency_code=record.currency_code,
        provider=record.provider,
        next_due_date=record.next_due_date,
        next_due_odometer=record.next_due_odometer,
        notes_preview=_preview(record.notes),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _record_detail(record: VehicleMaintenanceRecord) -> VehicleMaintenanceRecordDetailResponse:
    return VehicleMaintenanceRecordDetailResponse(**_record_summary(record).model_dump(), notes=record.notes)


def _reminder_status(reminder: VehicleMaintenanceReminder) -> str:
    if reminder.status in {"completed", "dismissed"}:
        return reminder.status
    if reminder.due_date < _today():
        return "overdue"
    return reminder.status


def _reminder_summary(reminder: VehicleMaintenanceReminder) -> VehicleMaintenanceReminderSummaryResponse:
    return VehicleMaintenanceReminderSummaryResponse(
        id=reminder.id,
        vehicle_id=reminder.vehicle_id,
        vehicle_name=reminder.vehicle.name if reminder.vehicle else "Vehicle",
        title=reminder.title,
        reminder_type=reminder.reminder_type,
        due_date=reminder.due_date,
        due_odometer=reminder.due_odometer,
        priority=reminder.priority,
        status=_reminder_status(reminder),
        completed_at=reminder.completed_at,
        notes_preview=_preview(reminder.notes),
        created_at=reminder.created_at,
        updated_at=reminder.updated_at,
    )


def _reminder_detail(reminder: VehicleMaintenanceReminder) -> VehicleMaintenanceReminderDetailResponse:
    return VehicleMaintenanceReminderDetailResponse(**_reminder_summary(reminder).model_dump(), notes=reminder.notes)


def list_vehicles(db: Session, user: User) -> list[VehicleMaintenanceVehicleSummaryResponse]:
    return [_vehicle_summary(vehicle) for vehicle in repository.list_vehicles(db, user.id)]


def create_vehicle(db: Session, user: User, payload: VehicleMaintenanceVehicleCreateRequest) -> VehicleMaintenanceVehicleDetailResponse:
    vehicle = VehicleMaintenanceVehicle(owner_id=user.id, **payload.model_dump())
    repository.add(db, vehicle)
    db.commit()
    db.refresh(vehicle)
    return _vehicle_detail(vehicle)


def get_vehicle(db: Session, user: User, vehicle_id: str) -> VehicleMaintenanceVehicleDetailResponse:
    return _vehicle_detail(_get_owned_vehicle(db, user, vehicle_id))


def update_vehicle(db: Session, user: User, vehicle_id: str, payload: VehicleMaintenanceVehicleUpdateRequest) -> VehicleMaintenanceVehicleDetailResponse:
    vehicle = _get_owned_vehicle(db, user, vehicle_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return _vehicle_detail(vehicle)


def duplicate_vehicle(db: Session, user: User, vehicle_id: str, payload: VehicleMaintenanceVehicleDuplicateRequest) -> VehicleMaintenanceVehicleDetailResponse:
    vehicle = _get_owned_vehicle(db, user, vehicle_id)
    duplicate = VehicleMaintenanceVehicle(
        owner_id=user.id,
        name=payload.name or f"{vehicle.name} copy",
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        plate_number=None,
        vin=None,
        odometer=vehicle.odometer,
        fuel_type=vehicle.fuel_type,
        status="active",
        notes=vehicle.notes,
    )
    repository.add(db, duplicate)
    db.commit()
    db.refresh(duplicate)
    return _vehicle_detail(duplicate)


def delete_vehicle(db: Session, user: User, vehicle_id: str) -> None:
    vehicle = _get_owned_vehicle(db, user, vehicle_id)
    repository.delete_record(db, vehicle)
    db.commit()


def list_records(db: Session, user: User) -> list[VehicleMaintenanceRecordSummaryResponse]:
    return [_record_summary(record) for record in repository.list_records(db, user.id)]


def create_record(db: Session, user: User, payload: VehicleMaintenanceRecordCreateRequest) -> VehicleMaintenanceRecordDetailResponse:
    data = payload.model_dump()
    vehicle = _get_owned_vehicle(db, user, data["vehicle_id"])
    record = VehicleMaintenanceRecord(owner_id=user.id, **data)
    vehicle.odometer = max(vehicle.odometer, record.odometer)
    repository.add(db, record)
    db.commit()
    db.refresh(record)
    return _record_detail(record)


def get_record(db: Session, user: User, record_id: str) -> VehicleMaintenanceRecordDetailResponse:
    return _record_detail(_get_owned_record(db, user, record_id))


def update_record(db: Session, user: User, record_id: str, payload: VehicleMaintenanceRecordUpdateRequest) -> VehicleMaintenanceRecordDetailResponse:
    record = _get_owned_record(db, user, record_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    if record.vehicle:
        record.vehicle.odometer = max(record.vehicle.odometer, record.odometer)
    db.commit()
    db.refresh(record)
    return _record_detail(record)


def delete_record(db: Session, user: User, record_id: str) -> None:
    record = _get_owned_record(db, user, record_id)
    repository.delete_record(db, record)
    db.commit()


def list_reminders(db: Session, user: User) -> list[VehicleMaintenanceReminderSummaryResponse]:
    return [_reminder_summary(reminder) for reminder in repository.list_reminders(db, user.id)]


def create_reminder(db: Session, user: User, payload: VehicleMaintenanceReminderCreateRequest) -> VehicleMaintenanceReminderDetailResponse:
    data = payload.model_dump()
    _get_owned_vehicle(db, user, data["vehicle_id"])
    reminder = VehicleMaintenanceReminder(owner_id=user.id, **data)
    repository.add(db, reminder)
    db.commit()
    db.refresh(reminder)
    return _reminder_detail(reminder)


def get_reminder(db: Session, user: User, reminder_id: str) -> VehicleMaintenanceReminderDetailResponse:
    return _reminder_detail(_get_owned_reminder(db, user, reminder_id))


def update_reminder(db: Session, user: User, reminder_id: str, payload: VehicleMaintenanceReminderUpdateRequest) -> VehicleMaintenanceReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.commit()
    db.refresh(reminder)
    return _reminder_detail(reminder)


def complete_reminder(db: Session, user: User, reminder_id: str) -> VehicleMaintenanceReminderDetailResponse:
    reminder = _get_owned_reminder(db, user, reminder_id)
    reminder.status = "completed"
    reminder.completed_at = _today()
    db.commit()
    db.refresh(reminder)
    return _reminder_detail(reminder)


def delete_reminder(db: Session, user: User, reminder_id: str) -> None:
    reminder = _get_owned_reminder(db, user, reminder_id)
    repository.delete_record(db, reminder)
    db.commit()


def get_dashboard(db: Session, user: User) -> VehicleMaintenanceDashboardResponse:
    vehicles = [_vehicle_summary(vehicle) for vehicle in repository.list_vehicles(db, user.id)]
    records = [_record_summary(record) for record in repository.list_records(db, user.id)]
    reminders = [_reminder_summary(reminder) for reminder in repository.list_reminders(db, user.id)]
    frequency = Counter(record.category for record in records)
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"records": 0, "reminders": 0, "cost": 0})
    for record in records:
        item = monthly[_month_key(record.service_date)]
        item["records"] += 1
        item["cost"] += record.cost
    for reminder in reminders:
        monthly[_month_key(reminder.due_date)]["reminders"] += 1
    return VehicleMaintenanceDashboardResponse(
        vehicles=vehicles,
        records=records,
        reminders=reminders,
        total_vehicles=len(vehicles),
        total_records=len(records),
        total_cost=round(sum(record.cost for record in records), 2),
        upcoming_reminders=len([reminder for reminder in reminders if reminder.status == "upcoming"]),
        overdue_reminders=len([reminder for reminder in reminders if reminder.status == "overdue"]),
        service_frequency=[
            VehicleMaintenanceServiceFrequencyResponse(category=category, count=count)
            for category, count in frequency.most_common()
        ],
        monthly_activity=[
            VehicleMaintenanceMonthlyActivityResponse(
                month=month,
                record_count=int(counts["records"]),
                reminder_count=int(counts["reminders"]),
                cost=round(counts["cost"], 2),
            )
            for month, counts in sorted(monthly.items())[-8:]
        ],
    )
