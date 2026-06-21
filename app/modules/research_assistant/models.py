from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.research_assistant.db import ResearchAssistantBase


class ResearchTopic(ResearchAssistantBase):
    __tablename__ = "ResearchTopics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(40),
        default="collecting",
        server_default="collecting",
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

    notes: Mapped[list["ResearchNote"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    references: Mapped[list["ResearchReference"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[list["ResearchJob"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )


class ResearchNote(ResearchAssistantBase):
    __tablename__ = "ResearchNotes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    topic_id: Mapped[str] = mapped_column(
        "topicId",
        String(36),
        ForeignKey("ResearchTopics.id"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
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

    topic: Mapped[ResearchTopic] = relationship(back_populates="notes")


class ResearchReference(ResearchAssistantBase):
    __tablename__ = "ResearchReferences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    topic_id: Mapped[str] = mapped_column(
        "topicId",
        String(36),
        ForeignKey("ResearchTopics.id"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
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

    topic: Mapped[ResearchTopic] = relationship(back_populates="references")


class ResearchJob(ResearchAssistantBase):
    __tablename__ = "ResearchJobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    topic_id: Mapped[str] = mapped_column(
        "topicId",
        String(36),
        ForeignKey("ResearchTopics.id"),
        index=True,
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column("jobType", String(80), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="queued",
        server_default="queued",
        nullable=False,
    )
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    topic: Mapped[ResearchTopic] = relationship(back_populates="jobs")
