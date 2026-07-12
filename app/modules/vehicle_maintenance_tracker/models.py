from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.vehicle_maintenance_tracker.db import VehicleMaintenanceBase


def _uuid() -> str:
    return str(uuid4())


class VehicleMaintenanceVehicle(VehicleMaintenanceBase):
    __tablename__ = "VehicleMaintenanceVehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    make: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plate_number: Mapped[str | None] = mapped_column("plateNumber", String(60), nullable=True)
    vin: Mapped[str | None] = mapped_column(String(80), nullable=True)
    odometer: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    fuel_type: Mapped[str] = mapped_column("fuelType", String(40), default="gasoline", server_default="gasoline", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    records: Mapped[list["VehicleMaintenanceRecord"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")
    reminders: Mapped[list["VehicleMaintenanceReminder"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")


class VehicleMaintenanceRecord(VehicleMaintenanceBase):
    __tablename__ = "VehicleMaintenanceRecords"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_id: Mapped[str] = mapped_column("vehicleId", String(36), ForeignKey("VehicleMaintenanceVehicles.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    service_date: Mapped[str] = mapped_column("serviceDate", String(40), nullable=False)
    category: Mapped[str] = mapped_column(String(60), default="general", server_default="general", nullable=False)
    odometer: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    cost: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    provider: Mapped[str | None] = mapped_column(String(160), nullable=True)
    next_due_date: Mapped[str | None] = mapped_column("nextDueDate", String(40), nullable=True)
    next_due_odometer: Mapped[int | None] = mapped_column("nextDueOdometer", Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    vehicle: Mapped[VehicleMaintenanceVehicle] = relationship(back_populates="records")


class VehicleMaintenanceReminder(VehicleMaintenanceBase):
    __tablename__ = "VehicleMaintenanceReminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_id: Mapped[str] = mapped_column("vehicleId", String(36), ForeignKey("VehicleMaintenanceVehicles.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    reminder_type: Mapped[str] = mapped_column("reminderType", String(60), default="service", server_default="service", nullable=False)
    due_date: Mapped[str] = mapped_column("dueDate", String(40), nullable=False)
    due_odometer: Mapped[int | None] = mapped_column("dueOdometer", Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(40), default="normal", server_default="normal", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="upcoming", server_default="upcoming", nullable=False)
    completed_at: Mapped[str | None] = mapped_column("completedAt", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    vehicle: Mapped[VehicleMaintenanceVehicle] = relationship(back_populates="reminders")
