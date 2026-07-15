from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.packing_checklist.db import PackingChecklistBase


def _uuid() -> str:
    return str(uuid4())


class PackingCategory(PackingChecklistBase):
    __tablename__ = "PackingCategories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_packing_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items: Mapped[list["PackingItem"]] = relationship(back_populates="category")


class PackingTripChecklist(PackingChecklistBase):
    __tablename__ = "PackingChecklists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    destination: Mapped[str | None] = mapped_column(String(180), index=True, nullable=True)
    trip_type: Mapped[str] = mapped_column("tripType", String(80), index=True, nullable=False)
    start_date: Mapped[date | None] = mapped_column("startDate", Date, index=True, nullable=True)
    end_date: Mapped[date | None] = mapped_column("endDate", Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False, default="planning")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items: Mapped[list["PackingItem"]] = relationship(back_populates="checklist", cascade="all, delete-orphan")


class PackingItem(PackingChecklistBase):
    __tablename__ = "PackingItems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    checklist_id: Mapped[str] = mapped_column("checklistId", String(36), ForeignKey("PackingChecklists.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("PackingCategories.id"), index=True, nullable=False)
    item_name: Mapped[str] = mapped_column("itemName", String(180), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    packed: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="normal")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    checklist: Mapped[PackingTripChecklist] = relationship(back_populates="items")
    category: Mapped[PackingCategory] = relationship(back_populates="items")
