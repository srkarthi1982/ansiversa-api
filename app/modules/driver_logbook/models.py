from datetime import date, datetime, time
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.driver_logbook.db import DriverLogbookBase


def _uuid() -> str:
    return str(uuid4())


class DriverVehicle(DriverLogbookBase):
    __tablename__ = "DriverVehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_name: Mapped[str] = mapped_column("vehicleName", String(160), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_nickname: Mapped[str | None] = mapped_column("registrationNickname", String(120), nullable=True)
    odometer_unit: Mapped[str] = mapped_column("odometerUnit", String(10), nullable=False, default="km")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    trips: Mapped[list["DriverTrip"]] = relationship(back_populates="vehicle")


class DriverTrip(DriverLogbookBase):
    __tablename__ = "DriverTrips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_id: Mapped[str] = mapped_column("vehicleId", String(36), ForeignKey("DriverVehicles.id"), index=True, nullable=False)
    trip_date: Mapped[date] = mapped_column("tripDate", Date, index=True, nullable=False)
    start_time: Mapped[time | None] = mapped_column("startTime", Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column("endTime", Time, nullable=True)
    start_odometer: Mapped[Decimal | None] = mapped_column("startOdometer", Numeric(12, 1), nullable=True)
    end_odometer: Mapped[Decimal | None] = mapped_column("endOdometer", Numeric(12, 1), nullable=True)
    distance: Mapped[Decimal] = mapped_column(Numeric(12, 1), nullable=False)
    purpose: Mapped[str] = mapped_column(String(40), nullable=False, default="personal")
    start_location: Mapped[str | None] = mapped_column("startLocation", String(180), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(180), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    vehicle: Mapped[DriverVehicle] = relationship(back_populates="trips")
