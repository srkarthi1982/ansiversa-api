from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from app.modules.emergency_contacts_organizer.db import EmergencyContactsOrganizerBase


def _uuid() -> str:
    return str(uuid4())


class EmergencyContactCategory(EmergencyContactsOrganizerBase):
    __tablename__ = "Categories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_emergency_contacts_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(240), nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    contacts: Mapped[list["EmergencyContact"]] = orm_relationship(back_populates="category")


class EmergencyContact(EmergencyContactsOrganizerBase):
    __tablename__ = "Contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("Categories.id"), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column("fullName", String(180), nullable=False)
    relationship: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    primary_phone: Mapped[str] = mapped_column("primaryPhone", String(60), nullable=False)
    alternate_phone: Mapped[str | None] = mapped_column("alternatePhone", String(60), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    country_or_region: Mapped[str | None] = mapped_column("countryOrRegion", String(120), index=True, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, index=True, nullable=False, default=50)
    is_favourite: Mapped[bool] = mapped_column("isFavourite", Boolean, index=True, nullable=False, default=False)
    is_primary: Mapped[bool] = mapped_column("isPrimary", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[EmergencyContactCategory] = orm_relationship(back_populates="contacts")
