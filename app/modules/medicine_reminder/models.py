from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.medicine_reminder.db import MedicineReminderBase


def _uuid() -> str:
    return str(uuid4())


class MedicineReminderMedicine(MedicineReminderBase):
    __tablename__ = "MedicineReminderMedicines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(120), nullable=True)
    form: Mapped[str] = mapped_column(String(40), default="tablet", server_default="tablet", nullable=False)
    purpose: Mapped[str | None] = mapped_column(String(180), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    prescribing_doctor: Mapped[str | None] = mapped_column("prescribingDoctor", String(120), nullable=True)
    start_date: Mapped[str | None] = mapped_column("startDate", String(40), nullable=True)
    end_date: Mapped[str | None] = mapped_column("endDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    refill_quantity: Mapped[int | None] = mapped_column("refillQuantity", Integer, nullable=True)
    refill_reminder_date: Mapped[str | None] = mapped_column("refillReminderDate", String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    schedules: Mapped[list["MedicineReminderSchedule"]] = relationship(back_populates="medicine", cascade="all, delete-orphan")
    dose_logs: Mapped[list["MedicineReminderDoseLog"]] = relationship(back_populates="medicine", cascade="all, delete-orphan")
    notes: Mapped[list["MedicineReminderNote"]] = relationship(back_populates="medicine", cascade="all, delete-orphan")


class MedicineReminderSchedule(MedicineReminderBase):
    __tablename__ = "MedicineReminderSchedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    medicine_id: Mapped[str] = mapped_column("medicineId", String(36), ForeignKey("MedicineReminderMedicines.id"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    time_of_day: Mapped[str] = mapped_column("timeOfDay", String(20), nullable=False)
    frequency: Mapped[str] = mapped_column(String(40), default="daily", server_default="daily", nullable=False)
    days_of_week: Mapped[str | None] = mapped_column("daysOfWeek", String(80), nullable=True)
    dose_amount: Mapped[str | None] = mapped_column("doseAmount", String(80), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    medicine: Mapped[MedicineReminderMedicine] = relationship(back_populates="schedules")
    dose_logs: Mapped[list["MedicineReminderDoseLog"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")


class MedicineReminderDoseLog(MedicineReminderBase):
    __tablename__ = "MedicineReminderDoseLogs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    medicine_id: Mapped[str] = mapped_column("medicineId", String(36), ForeignKey("MedicineReminderMedicines.id"), index=True, nullable=False)
    schedule_id: Mapped[str | None] = mapped_column("scheduleId", String(36), ForeignKey("MedicineReminderSchedules.id"), index=True, nullable=True)
    scheduled_for: Mapped[str] = mapped_column("scheduledFor", String(40), nullable=False)
    taken_at: Mapped[str | None] = mapped_column("takenAt", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="taken", server_default="taken", nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    medicine: Mapped[MedicineReminderMedicine] = relationship(back_populates="dose_logs")
    schedule: Mapped[MedicineReminderSchedule | None] = relationship(back_populates="dose_logs")


class MedicineReminderNote(MedicineReminderBase):
    __tablename__ = "MedicineReminderNotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    medicine_id: Mapped[str] = mapped_column("medicineId", String(36), ForeignKey("MedicineReminderMedicines.id"), index=True, nullable=False)
    note_date: Mapped[str] = mapped_column("noteDate", String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(40), default="general", server_default="general", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    medicine: Mapped[MedicineReminderMedicine] = relationship(back_populates="notes")
