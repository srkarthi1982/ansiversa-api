from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.car_pool.db import CarPoolBase


def _uuid() -> str:
    return str(uuid4())


class CarPoolRide(CarPoolBase):
    __tablename__ = "CarPoolRides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    origin: Mapped[str] = mapped_column(String(180), nullable=False)
    destination: Mapped[str] = mapped_column(String(180), nullable=False)
    departure_at: Mapped[str] = mapped_column("departureAt", String(40), nullable=False)
    return_at: Mapped[str | None] = mapped_column("returnAt", String(40), nullable=True)
    meeting_point: Mapped[str | None] = mapped_column("meetingPoint", String(220), nullable=True)
    vehicle_label: Mapped[str | None] = mapped_column("vehicleLabel", String(160), nullable=True)
    driver_name: Mapped[str | None] = mapped_column("driverName", String(120), nullable=True)
    seats_offered: Mapped[int] = mapped_column("seatsOffered", Integer, default=1, server_default="1", nullable=False)
    seats_filled: Mapped[int] = mapped_column("seatsFilled", Integer, default=0, server_default="0", nullable=False)
    price_per_seat: Mapped[float | None] = mapped_column("pricePerSeat", Float, nullable=True)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    recurrence: Mapped[str] = mapped_column(String(40), default="one_time", server_default="one_time", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="open", server_default="open", nullable=False)
    visibility: Mapped[str] = mapped_column(String(40), default="private", server_default="private", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    passengers: Mapped[list["CarPoolPassenger"]] = relationship(back_populates="ride", cascade="all, delete-orphan")
    requests: Mapped[list["CarPoolRequest"]] = relationship(back_populates="ride", cascade="all, delete-orphan")


class CarPoolPassenger(CarPoolBase):
    __tablename__ = "CarPoolPassengers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    ride_id: Mapped[str] = mapped_column("rideId", String(36), ForeignKey("CarPoolRides.id"), index=True, nullable=False)
    passenger_name: Mapped[str] = mapped_column("passengerName", String(120), nullable=False)
    seats: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    contact_note: Mapped[str | None] = mapped_column("contactNote", String(220), nullable=True)
    joined_at: Mapped[str] = mapped_column("joinedAt", String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="joined", server_default="joined", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    ride: Mapped[CarPoolRide] = relationship(back_populates="passengers")


class CarPoolRequest(CarPoolBase):
    __tablename__ = "CarPoolRequests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    ride_id: Mapped[str] = mapped_column("rideId", String(36), ForeignKey("CarPoolRides.id"), index=True, nullable=False)
    requester_name: Mapped[str] = mapped_column("requesterName", String(120), nullable=False)
    seats_requested: Mapped[int] = mapped_column("seatsRequested", Integer, default=1, server_default="1", nullable=False)
    pickup_note: Mapped[str | None] = mapped_column("pickupNote", String(220), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_at: Mapped[str] = mapped_column("requestedAt", String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="pending", server_default="pending", nullable=False)
    response_note: Mapped[str | None] = mapped_column("responseNote", String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    ride: Mapped[CarPoolRide] = relationship(back_populates="requests")
