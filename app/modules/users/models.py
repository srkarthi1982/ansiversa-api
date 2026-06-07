from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import ParentBase


class UserSettings(ParentBase):
    __tablename__ = "UserSettings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    theme: Mapped[str] = mapped_column(
        String(40),
        default="system",
        server_default="system",
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(20),
        default="en",
        server_default="en",
        nullable=False,
    )
    marketing_emails: Mapped[bool] = mapped_column(
        "marketingEmails",
        Boolean,
        default=False,
        server_default="0",
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
