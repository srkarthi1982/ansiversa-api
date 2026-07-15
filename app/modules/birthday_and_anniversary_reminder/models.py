from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from app.modules.birthday_and_anniversary_reminder.db import BirthdayReminderBase


def _uuid() -> str:
    return str(uuid4())


class ReminderType(BirthdayReminderBase):
    __tablename__ = "ReminderTypes"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_reminder_types_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reminders: Mapped[list["ReminderContact"]] = orm_relationship(back_populates="reminder_type")


class ReminderContact(BirthdayReminderBase):
    __tablename__ = "ReminderContacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    reminder_type_id: Mapped[str] = mapped_column("reminderTypeId", String(36), ForeignKey("ReminderTypes.id"), index=True, nullable=False)
    person_name: Mapped[str] = mapped_column("personName", String(180), nullable=False)
    relationship: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    event_date: Mapped[date] = mapped_column("eventDate", Date, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    gift_ideas: Mapped[str | None] = mapped_column("giftIdeas", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    favourite: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reminder_type: Mapped[ReminderType] = orm_relationship(back_populates="reminders")
    acknowledgements: Mapped[list["ReminderAcknowledgement"]] = orm_relationship(back_populates="reminder", cascade="all, delete-orphan")


class ReminderAcknowledgement(BirthdayReminderBase):
    __tablename__ = "ReminderAcknowledgements"
    __table_args__ = (UniqueConstraint("reminderContactId", "acknowledgementYear", name="uq_reminder_ack_contact_year"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    reminder_contact_id: Mapped[str] = mapped_column("reminderContactId", String(36), ForeignKey("ReminderContacts.id", ondelete="CASCADE"), index=True, nullable=False)
    acknowledgement_year: Mapped[int] = mapped_column("acknowledgementYear", Integer, index=True, nullable=False)
    acknowledged_at: Mapped[datetime] = mapped_column("acknowledgedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    reminder: Mapped[ReminderContact] = orm_relationship(back_populates="acknowledgements")
