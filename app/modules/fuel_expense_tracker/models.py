from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.fuel_expense_tracker.db import FuelExpenseBase


def _uuid() -> str:
    return str(uuid4())


class FuelVehicle(FuelExpenseBase):
    __tablename__ = "FuelVehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_name: Mapped[str] = mapped_column("vehicleName", String(160), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[str | None] = mapped_column("fuelType", String(80), nullable=True)
    registration_nickname: Mapped[str | None] = mapped_column("registrationNickname", String(120), nullable=True)
    odometer_unit: Mapped[str] = mapped_column("odometerUnit", String(10), nullable=False, default="km")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    entries: Mapped[list["FuelEntry"]] = relationship(back_populates="vehicle")


class FuelEntry(FuelExpenseBase):
    __tablename__ = "FuelEntries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_id: Mapped[str] = mapped_column("vehicleId", String(36), ForeignKey("FuelVehicles.id"), index=True, nullable=False)
    purchase_date: Mapped[date] = mapped_column("purchaseDate", Date, index=True, nullable=False)
    odometer: Mapped[Decimal | None] = mapped_column(Numeric(12, 1), nullable=True)
    fuel_quantity: Mapped[Decimal] = mapped_column("fuelQuantity", Numeric(12, 3), nullable=False)
    fuel_unit: Mapped[str] = mapped_column("fuelUnit", String(10), nullable=False, default="L")
    total_cost: Mapped[Decimal] = mapped_column("totalCost", Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    unit_price: Mapped[Decimal] = mapped_column("unitPrice", Numeric(12, 4), nullable=False)
    station_name: Mapped[str | None] = mapped_column("stationName", String(180), nullable=True)
    payment_method: Mapped[str | None] = mapped_column("paymentMethod", String(120), nullable=True)
    full_tank: Mapped[bool] = mapped_column("fullTank", Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    vehicle: Mapped[FuelVehicle] = relationship(back_populates="entries")
