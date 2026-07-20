from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase
from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User


class ActivityTimelineEntry(ParentBase):
    __tablename__ = "ActivityTimeline"
    __table_args__ = (
        Index("ActivityTimeline_userId_createdAt_idx", "userId", "createdAt"),
        Index("ActivityTimeline_userId_activityType_createdAt_idx", "userId", "activityType", "createdAt"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("Users.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column("activityType", String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    source_app_id: Mapped[str | None] = mapped_column("sourceAppId", String(36), ForeignKey("Apps.id"), nullable=True)
    action_route: Mapped[str | None] = mapped_column("actionRoute", String(500), nullable=True)
    action_label: Mapped[str | None] = mapped_column("actionLabel", String(120), nullable=True)
    entity_type: Mapped[str | None] = mapped_column("entityType", String(80), nullable=True)
    entity_id: Mapped[str | None] = mapped_column("entityId", String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship()
    source_app: Mapped[AppCatalogItem | None] = relationship()
