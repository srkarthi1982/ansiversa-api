from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import ParentBase


class AppCatalogItem(ParentBase):
    __tablename__ = "apps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    key: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="active",
        server_default="active",
        nullable=False,
    )
    launch_status: Mapped[str] = mapped_column(
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
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    admin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
