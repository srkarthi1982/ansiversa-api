from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase
from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User


class Favorite(ParentBase):
    __tablename__ = "Favorites"
    __table_args__ = (
        Index("Favorites_appId_userId_idx", "appId", "userId", unique=True),
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
    app_id: Mapped[str] = mapped_column(
        "appId",
        String(36),
        ForeignKey("Apps.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    app: Mapped[AppCatalogItem] = relationship()
    user: Mapped[User] = relationship()
