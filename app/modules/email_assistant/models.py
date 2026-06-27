from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.email_assistant.db import EmailAssistantBase


class EmailProject(EmailAssistantBase):
    __tablename__ = "EmailAssistantProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    audience: Mapped[str | None] = mapped_column(String(180), nullable=True)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone: Mapped[str] = mapped_column(
        String(40),
        default="professional",
        server_default="professional",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        server_default="draft",
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

    drafts: Mapped[list["EmailDraft"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["EmailHistoryItem"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class EmailDraft(EmailAssistantBase):
    __tablename__ = "EmailAssistantDrafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("EmailAssistantProjects.id"),
        index=True,
        nullable=False,
    )
    template_id: Mapped[int | None] = mapped_column(
        "templateId",
        Integer,
        ForeignKey("EmailAssistantTemplates.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(220), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(
        String(40),
        default="professional",
        server_default="professional",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        server_default="draft",
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

    project: Mapped[EmailProject] = relationship(back_populates="drafts")
    template: Mapped["EmailTemplate | None"] = relationship(back_populates="drafts")
    history_items: Mapped[list["EmailHistoryItem"]] = relationship(
        back_populates="draft",
        cascade="all, delete-orphan",
    )


class EmailTemplate(EmailAssistantBase):
    __tablename__ = "EmailAssistantTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(
        String(80),
        default="general",
        server_default="general",
        nullable=False,
    )
    subject_pattern: Mapped[str | None] = mapped_column("subjectPattern", String(220), nullable=True)
    body_pattern: Mapped[str] = mapped_column("bodyPattern", Text, nullable=False)
    tone: Mapped[str] = mapped_column(
        String(40),
        default="professional",
        server_default="professional",
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

    drafts: Mapped[list[EmailDraft]] = relationship(back_populates="template")


class EmailHistoryItem(EmailAssistantBase):
    __tablename__ = "EmailAssistantHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("EmailAssistantProjects.id"),
        index=True,
        nullable=True,
    )
    draft_id: Mapped[int | None] = mapped_column(
        "draftId",
        Integer,
        ForeignKey("EmailAssistantDrafts.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    action_type: Mapped[str] = mapped_column(
        "actionType",
        String(60),
        default="drafted",
        server_default="drafted",
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    project: Mapped[EmailProject | None] = relationship(back_populates="history_items")
    draft: Mapped[EmailDraft | None] = relationship(back_populates="history_items")
