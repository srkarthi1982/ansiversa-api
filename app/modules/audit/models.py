from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase
from app.modules.auth.models import User


class AuditLog(ParentBase):
    __tablename__ = "AuditLogs"
    __table_args__ = (
        Index("AuditLogs_actorUserId_createdAt_idx", "actorUserId", "createdAt"),
        Index("AuditLogs_entityType_entityId_idx", "entityType", "entityId"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        "actorUserId",
        String(36),
        ForeignKey("Users.id"),
        nullable=True,
    )
    actor_email: Mapped[str | None] = mapped_column(
        "actorEmail",
        String(255),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column("entityType", String(120), nullable=False)
    entity_id: Mapped[str | None] = mapped_column("entityId", String(255), nullable=True)
    entity_label: Mapped[str | None] = mapped_column(
        "entityLabel",
        String(500),
        nullable=True,
    )
    metadata_json: Mapped[str | None] = mapped_column(
        "metadataJson",
        Text,
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column("ipAddress", String(120), nullable=True)
    user_agent: Mapped[str | None] = mapped_column("userAgent", String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    actor: Mapped[User | None] = relationship()
