from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase
from app.modules.auth.models import User


class Notification(ParentBase):
    __tablename__ = "Notifications"
    __table_args__ = (
        Index("Notifications_userId_idx", "userId"),
        Index("Notifications_userId_isRead_idx", "userId", "isRead"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(120), nullable=False)
    is_read: Mapped[bool] = mapped_column(
        "isRead",
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
    read_at: Mapped[datetime | None] = mapped_column(
        "readAt",
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_json: Mapped[str | None] = mapped_column(
        "metadataJson",
        Text,
        nullable=True,
    )

    user: Mapped[User] = relationship()
