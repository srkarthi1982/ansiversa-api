from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase


class Category(ParentBase):
    __tablename__ = "Categories"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    key: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(
        "sortOrder",
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="active",
        server_default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    apps: Mapped[list["AppCatalogItem"]] = relationship(back_populates="category")


class AppCatalogItem(ParentBase):
    __tablename__ = "Apps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[str] = mapped_column(
        "categoryId",
        String(36),
        ForeignKey("Categories.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        server_default="1.0.0",
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(
        "isFeatured",
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
    website_url: Mapped[str | None] = mapped_column(
        "websiteUrl",
        String(500),
        nullable=True,
    )
    admin_url: Mapped[str | None] = mapped_column(
        "adminUrl",
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    capabilities: Mapped[str | None] = mapped_column(
        Text,
        default="[]",
        server_default="[]",
        nullable=True,
    )
    launch_status: Mapped[str] = mapped_column(
        "launchStatus",
        String(40),
        default="comingSoon",
        server_default="comingSoon",
        nullable=False,
    )
    visibility: Mapped[str] = mapped_column(
        String(40),
        default="public",
        server_default="public",
        nullable=False,
    )
    pricing_gate: Mapped[str] = mapped_column(
        "pricingGate",
        String(40),
        default="free",
        server_default="free",
        nullable=False,
    )
    logo_key: Mapped[str | None] = mapped_column("logoKey", String(120), nullable=True)

    category: Mapped[Category] = relationship(back_populates="apps")
