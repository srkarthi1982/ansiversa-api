from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.first_aid_guide.db import FirstAidGuideBase


def _uuid() -> str:
    return str(uuid4())


class FirstAidCategory(FirstAidGuideBase):
    __tablename__ = "FirstAidCategories"
    __table_args__ = (UniqueConstraint("name", name="uq_first_aid_categories_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    guides: Mapped[list["FirstAidGuide"]] = relationship(back_populates="category")


class FirstAidGuide(FirstAidGuideBase):
    __tablename__ = "FirstAidGuides"
    __table_args__ = (UniqueConstraint("title", name="uq_first_aid_guides_title"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("FirstAidCategories.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    overview: Mapped[str] = mapped_column(Text, nullable=False)
    first_aid_steps: Mapped[str] = mapped_column("firstAidSteps", Text, nullable=False)
    avoid_actions: Mapped[str] = mapped_column("avoidActions", Text, nullable=False)
    emergency_warning: Mapped[str] = mapped_column("emergencyWarning", Text, nullable=False)
    prevention: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_topics: Mapped[str | None] = mapped_column("relatedTopics", Text, nullable=True)
    display_order: Mapped[int] = mapped_column("displayOrder", Integer, nullable=False, default=0)
    last_reviewed: Mapped[date | None] = mapped_column("lastReviewed", Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    category: Mapped[FirstAidCategory] = relationship(back_populates="guides")


class UserGuideBookmark(FirstAidGuideBase):
    __tablename__ = "UserGuideBookmarks"
    __table_args__ = (UniqueConstraint("userId", "guideId", name="uq_user_guide_bookmarks_owner_guide"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    guide_id: Mapped[str] = mapped_column("guideId", String(36), ForeignKey("FirstAidGuides.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    guide: Mapped[FirstAidGuide] = relationship()


class UserGuideHistory(FirstAidGuideBase):
    __tablename__ = "UserGuideHistory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    guide_id: Mapped[str] = mapped_column("guideId", String(36), ForeignKey("FirstAidGuides.id"), index=True, nullable=False)
    viewed_at: Mapped[datetime] = mapped_column("viewedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    guide: Mapped[FirstAidGuide] = relationship()
