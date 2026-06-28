from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.proposal_writer.db import ProposalWriterBase


class ProposalProject(ProposalWriterBase):
    __tablename__ = "ProposalWriterProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    client_name: Mapped[str] = mapped_column("clientName", String(180), nullable=False)
    opportunity: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_range: Mapped[str | None] = mapped_column("budgetRange", String(120), nullable=True)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
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

    sections: Mapped[list["ProposalSection"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    drafts: Mapped[list["ProposalDraft"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["ProposalHistoryItem"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProposalSection(ProposalWriterBase):
    __tablename__ = "ProposalWriterSections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("ProposalWriterProjects.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
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

    project: Mapped[ProposalProject] = relationship(back_populates="sections")


class ProposalDraft(ProposalWriterBase):
    __tablename__ = "ProposalWriterDrafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("ProposalWriterProjects.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
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

    project: Mapped[ProposalProject] = relationship(back_populates="drafts")
    history_items: Mapped[list["ProposalHistoryItem"]] = relationship(
        back_populates="draft",
        cascade="all, delete-orphan",
    )


class ProposalHistoryItem(ProposalWriterBase):
    __tablename__ = "ProposalWriterHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("ProposalWriterProjects.id"),
        index=True,
        nullable=True,
    )
    draft_id: Mapped[int | None] = mapped_column(
        "draftId",
        Integer,
        ForeignKey("ProposalWriterDrafts.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    action_type: Mapped[str] = mapped_column(
        "actionType",
        String(60),
        default="updated",
        server_default="updated",
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

    project: Mapped[ProposalProject | None] = relationship(back_populates="history_items")
    draft: Mapped[ProposalDraft | None] = relationship(back_populates="history_items")
