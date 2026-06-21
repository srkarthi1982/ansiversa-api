from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.concept_explainer.db import ConceptExplainerBase


class Concept(ConceptExplainerBase):
    __tablename__ = "Concepts"

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
    topic: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(40),
        default="learning",
        server_default="learning",
        nullable=False,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        "reviewedAt",
        DateTime(timezone=True),
        nullable=True,
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

    steps: Mapped[list["ConceptStep"]] = relationship(
        back_populates="concept",
        cascade="all, delete-orphan",
    )
    checks: Mapped[list["ConceptCheck"]] = relationship(
        back_populates="concept",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[list["ConceptJob"]] = relationship(
        back_populates="concept",
        cascade="all, delete-orphan",
    )


class ConceptStep(ConceptExplainerBase):
    __tablename__ = "ConceptSteps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    concept_id: Mapped[str] = mapped_column(
        "conceptId",
        String(36),
        ForeignKey("Concepts.id"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
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

    concept: Mapped[Concept] = relationship(back_populates="steps")


class ConceptCheck(ConceptExplainerBase):
    __tablename__ = "ConceptChecks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    concept_id: Mapped[str] = mapped_column(
        "conceptId",
        String(36),
        ForeignKey("Concepts.id"),
        index=True,
        nullable=False,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str] = mapped_column(
        "expectedAnswer",
        Text,
        nullable=False,
    )
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

    concept: Mapped[Concept] = relationship(back_populates="checks")


class ConceptJob(ConceptExplainerBase):
    __tablename__ = "ConceptJobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    concept_id: Mapped[str] = mapped_column(
        "conceptId",
        String(36),
        ForeignKey("Concepts.id"),
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

    concept: Mapped[Concept] = relationship(back_populates="jobs")
