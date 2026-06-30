from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.social_caption_generator.db import SocialCaptionGeneratorBase


class CaptionProject(SocialCaptionGeneratorBase):
    __tablename__ = "CaptionProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(80), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(180), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    campaign_brief: Mapped[str | None] = mapped_column("campaignBrief", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    captions: Mapped[list["SocialCaption"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    templates: Mapped[list["CaptionTemplate"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class SocialCaption(SocialCaptionGeneratorBase):
    __tablename__ = "SocialCaptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("CaptionProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    caption_text: Mapped[str | None] = mapped_column("captionText", Text, nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)
    call_to_action: Mapped[str | None] = mapped_column("callToAction", String(240), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[CaptionProject] = relationship(back_populates="captions")
    history: Mapped[list["CaptionHistory"]] = relationship(back_populates="caption", cascade="all, delete-orphan")


class CaptionTemplate(SocialCaptionGeneratorBase):
    __tablename__ = "CaptionTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("CaptionProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    template_text: Mapped[str | None] = mapped_column("templateText", Text, nullable=True)
    usage_notes: Mapped[str | None] = mapped_column("usageNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[CaptionProject] = relationship(back_populates="templates")


class CaptionHistory(SocialCaptionGeneratorBase):
    __tablename__ = "CaptionHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    caption_id: Mapped[int] = mapped_column("captionId", Integer, ForeignKey("SocialCaptions.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[str | None] = mapped_column("revisionNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    caption: Mapped[SocialCaption] = relationship(back_populates="history")
