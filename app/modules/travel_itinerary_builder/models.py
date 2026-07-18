from datetime import date, datetime, time
from uuid import uuid4

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def uid() -> str:
    return str(uuid4())


class TravelActivityCategory(Base):
    __tablename__ = "TravelActivityCategories"
    __table_args__ = (
        UniqueConstraint(
            "userId",
            "name",
            name="uq_travel_activity_category_user_name",
        ),
        Index("ix_travel_activity_categories_user_sort", "userId", "sortOrder"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column("userId", String(36), index=True)
    name: Mapped[str] = mapped_column(String(80))
    color: Mapped[str | None] = mapped_column(String(40))
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    activities: Mapped[list["TravelActivity"]] = relationship(
        back_populates="category",
    )


class TravelItinerary(Base):
    __tablename__ = "TravelItineraries"
    __table_args__ = (
        UniqueConstraint("userId", "name", name="uq_travel_itinerary_user_name"),
        Index("ix_travel_itineraries_user_status", "userId", "status"),
        Index("ix_travel_itineraries_user_start", "userId", "startDate"),
        Index("ix_travel_itineraries_user_destination", "userId", "destination"),
        Index("ix_travel_itineraries_user_updated", "userId", "updatedAt"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column("userId", String(36), index=True)
    name: Mapped[str] = mapped_column(String(180))
    destination: Mapped[str] = mapped_column(String(180))
    start_date: Mapped[date] = mapped_column("startDate", Date)
    end_date: Mapped[date] = mapped_column("endDate", Date)
    status: Mapped[str] = mapped_column(String(16))
    purpose: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    days: Mapped[list["TravelItineraryDay"]] = relationship(
        back_populates="itinerary",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TravelItineraryDay.day_date",
    )


class TravelItineraryDay(Base):
    __tablename__ = "TravelItineraryDays"
    __table_args__ = (
        UniqueConstraint("itineraryId", "dayDate", name="uq_travel_day_trip_date"),
        Index("ix_travel_days_itinerary_date", "itineraryId", "dayDate"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    itinerary_id: Mapped[str] = mapped_column(
        "itineraryId",
        String(36),
        ForeignKey("TravelItineraries.id", ondelete="CASCADE"),
        index=True,
    )
    day_date: Mapped[date] = mapped_column("dayDate", Date)
    title: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    itinerary: Mapped[TravelItinerary] = relationship(back_populates="days")
    activities: Mapped[list["TravelActivity"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=lambda: (TravelActivity.start_time, TravelActivity.created_at),
    )


class TravelActivity(Base):
    __tablename__ = "TravelActivities"
    __table_args__ = (
        Index("ix_travel_activities_day_time", "dayId", "startTime"),
        Index("ix_travel_activities_category", "categoryId"),
        Index("ix_travel_activities_updated", "updatedAt"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    day_id: Mapped[str] = mapped_column(
        "dayId",
        String(36),
        ForeignKey("TravelItineraryDays.id", ondelete="CASCADE"),
        index=True,
    )
    category_id: Mapped[str | None] = mapped_column(
        "categoryId",
        String(36),
        ForeignKey("TravelActivityCategories.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(180))
    start_time: Mapped[time | None] = mapped_column("startTime", Time)
    end_time: Mapped[time | None] = mapped_column("endTime", Time)
    location: Mapped[str | None] = mapped_column(String(240))
    booking_reference: Mapped[str | None] = mapped_column(
        "bookingReference",
        String(160),
    )
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    day: Mapped[TravelItineraryDay] = relationship(back_populates="activities")
    category: Mapped[TravelActivityCategory | None] = relationship(
        back_populates="activities",
    )
