from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.rent_a_car.db import RentACarBase


def _uuid() -> str:
    return str(uuid4())


class RentACarSearch(RentACarBase):
    __tablename__ = "RentACarSearches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    pickup_location: Mapped[str] = mapped_column("pickupLocation", String(180), nullable=False)
    dropoff_location: Mapped[str] = mapped_column("dropoffLocation", String(180), nullable=False)
    pickup_at: Mapped[str] = mapped_column("pickupAt", String(40), nullable=False)
    return_at: Mapped[str] = mapped_column("returnAt", String(40), nullable=False)
    driver_age_group: Mapped[str] = mapped_column("driverAgeGroup", String(60), default="30-64", server_default="30-64", nullable=False)
    vehicle_type: Mapped[str] = mapped_column("vehicleType", String(80), default="any", server_default="any", nullable=False)
    transmission: Mapped[str] = mapped_column(String(40), default="any", server_default="any", nullable=False)
    passengers: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    luggage: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planning", server_default="planning", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    vehicle_options: Mapped[list["RentACarVehicleOption"]] = relationship(back_populates="search", cascade="all, delete-orphan")
    bookings: Mapped[list["RentACarBooking"]] = relationship(back_populates="search", cascade="all, delete-orphan")


class RentACarVehicleOption(RentACarBase):
    __tablename__ = "RentACarVehicleOptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    search_id: Mapped[str] = mapped_column("searchId", String(36), ForeignKey("RentACarSearches.id"), index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column("providerName", String(160), nullable=False)
    vehicle_name: Mapped[str] = mapped_column("vehicleName", String(180), nullable=False)
    vehicle_class: Mapped[str] = mapped_column("vehicleClass", String(80), nullable=False)
    transmission: Mapped[str] = mapped_column(String(40), default="automatic", server_default="automatic", nullable=False)
    fuel_policy: Mapped[str | None] = mapped_column("fuelPolicy", String(160), nullable=True)
    seats: Mapped[int] = mapped_column(Integer, default=4, server_default="4", nullable=False)
    luggage_capacity: Mapped[int] = mapped_column("luggageCapacity", Integer, default=1, server_default="1", nullable=False)
    daily_base_rate: Mapped[float] = mapped_column("dailyBaseRate", Float, default=0, server_default="0", nullable=False)
    rental_days: Mapped[int] = mapped_column("rentalDays", Integer, default=1, server_default="1", nullable=False)
    taxes_and_fees: Mapped[float] = mapped_column("taxesAndFees", Float, default=0, server_default="0", nullable=False)
    deposit: Mapped[float | None] = mapped_column(Float, nullable=True)
    addon_estimate: Mapped[float] = mapped_column("addonEstimate", Float, default=0, server_default="0", nullable=False)
    mileage_policy: Mapped[str | None] = mapped_column("mileagePolicy", String(180), nullable=True)
    cancellation_terms: Mapped[str | None] = mapped_column("cancellationTerms", String(220), nullable=True)
    pickup_method: Mapped[str | None] = mapped_column("pickupMethod", String(160), nullable=True)
    reference_url: Mapped[str | None] = mapped_column("referenceUrl", String(600), nullable=True)
    last_checked: Mapped[str | None] = mapped_column("lastChecked", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_preferred: Mapped[bool] = mapped_column("isPreferred", Boolean, default=False, server_default="0", nullable=False)
    availability_status: Mapped[str] = mapped_column("availabilityStatus", String(40), default="unconfirmed", server_default="unconfirmed", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    search: Mapped[RentACarSearch] = relationship(back_populates="vehicle_options")
    bookings: Mapped[list["RentACarBooking"]] = relationship(back_populates="vehicle_option")


class RentACarBooking(RentACarBase):
    __tablename__ = "RentACarBookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    search_id: Mapped[str] = mapped_column("searchId", String(36), ForeignKey("RentACarSearches.id"), index=True, nullable=False)
    vehicle_option_id: Mapped[str | None] = mapped_column("vehicleOptionId", String(36), ForeignKey("RentACarVehicleOptions.id"), index=True, nullable=True)
    booking_reference: Mapped[str] = mapped_column("bookingReference", String(160), nullable=False)
    provider_name: Mapped[str] = mapped_column("providerName", String(160), nullable=False)
    pickup_instructions: Mapped[str | None] = mapped_column("pickupInstructions", Text, nullable=True)
    dropoff_instructions: Mapped[str | None] = mapped_column("dropoffInstructions", Text, nullable=True)
    confirmed_total: Mapped[float] = mapped_column("confirmedTotal", Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    deposit_amount: Mapped[float | None] = mapped_column("depositAmount", Float, nullable=True)
    contact_information: Mapped[str | None] = mapped_column("contactInformation", String(220), nullable=True)
    booking_date: Mapped[str] = mapped_column("bookingDate", String(40), nullable=False)
    cancellation_deadline: Mapped[str | None] = mapped_column("cancellationDeadline", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="confirmed", server_default="confirmed", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    search: Mapped[RentACarSearch] = relationship(back_populates="bookings")
    vehicle_option: Mapped[RentACarVehicleOption | None] = relationship(back_populates="bookings")
