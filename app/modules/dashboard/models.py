from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase
from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User


class Dashboard(ParentBase):
    __tablename__ = "Dashboard"
    __table_args__ = (
        Index("Dashboard_userId_lastActivityAt_idx", "userId", "lastActivityAt"),
        Index("Dashboard_userId_appId_idx", "userId", "appId", unique=True),
    )

    id: Mapped[str] = mapped_column(
        "_id",
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
    app_id: Mapped[str] = mapped_column(
        "appId",
        String(36),
        ForeignKey("Apps.id"),
        nullable=False,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(
        "lastActivityAt",
        DateTime(timezone=True),
        nullable=True,
    )
    summary_version: Mapped[int] = mapped_column(
        "summaryVersion",
        Integer,
        default=1,
        server_default="1",
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
    summary_json: Mapped[str | None] = mapped_column(
        "summaryJson",
        Text,
        nullable=True,
    )

    app: Mapped[AppCatalogItem] = relationship()
    user: Mapped[User] = relationship()
