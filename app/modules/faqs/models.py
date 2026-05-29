from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import ParentBase


class Faq(ParentBase):
    __tablename__ = "Faqs"
    __table_args__ = (
        Index(
            "Faqs_appKey_audience_is_published_idx",
            "appKey",
            "audience",
            "is_published",
        ),
        Index("Faqs_sortOrder_createdAt_idx", "sortOrder", "createdAt"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(
        "sortOrder",
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    app_key: Mapped[str | None] = mapped_column("appKey", String(120), nullable=True)
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
    audience: Mapped[str] = mapped_column(
        String(80),
        default="user",
        server_default="user",
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    answer_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
