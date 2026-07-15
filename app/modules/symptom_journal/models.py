from datetime import date, datetime, time
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.symptom_journal.db import SymptomJournalBase


def _uuid() -> str:
    return str(uuid4())


class SymptomCategory(SymptomJournalBase):
    __tablename__ = "SymptomCategories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_symptom_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    entries: Mapped[list["SymptomEntry"]] = relationship(back_populates="category")


class SymptomEntry(SymptomJournalBase):
    __tablename__ = "SymptomEntries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str | None] = mapped_column("categoryId", String(36), ForeignKey("SymptomCategories.id"), index=True, nullable=True)
    entry_date: Mapped[date] = mapped_column("entryDate", Date, index=True, nullable=False)
    entry_time: Mapped[time | None] = mapped_column("entryTime", Time, nullable=True)
    symptom_title: Mapped[str] = mapped_column("symptomTitle", String(180), nullable=False)
    severity: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    duration: Mapped[str | None] = mapped_column(String(120), nullable=True)
    body_location: Mapped[str | None] = mapped_column("bodyLocation", String(180), nullable=True)
    mood: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    triggers: Mapped[str | None] = mapped_column(Text, nullable=True)
    relief_methods: Mapped[str | None] = mapped_column("reliefMethods", Text, nullable=True)
    follow_up_notes: Mapped[str | None] = mapped_column("followUpNotes", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    category: Mapped[SymptomCategory | None] = relationship(back_populates="entries")
