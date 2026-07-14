from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.home_inventory_manager.db import HomeInventoryManagerBase


def _uuid() -> str:
    return str(uuid4())


class InventoryCategory(HomeInventoryManagerBase):
    __tablename__ = "Categories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_home_inventory_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items: Mapped[list["InventoryItem"]] = relationship(back_populates="category")


class InventoryItem(HomeInventoryManagerBase):
    __tablename__ = "Items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("Categories.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    room: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    purchase_date: Mapped[str | None] = mapped_column("purchaseDate", String(40), index=True, nullable=True)
    purchase_price: Mapped[float | None] = mapped_column("purchasePrice", Numeric(12, 2), nullable=True)
    estimated_value: Mapped[float | None] = mapped_column("estimatedValue", Numeric(12, 2), index=True, nullable=True)
    warranty_expiry: Mapped[str | None] = mapped_column("warrantyExpiry", String(40), index=True, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    serial_number: Mapped[str | None] = mapped_column("serialNumber", String(160), nullable=True)
    condition: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[InventoryCategory] = relationship(back_populates="items")
