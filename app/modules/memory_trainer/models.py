from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.memory_trainer.db import MemoryTrainerBase


class MemoryGame(MemoryTrainerBase):
    __tablename__ = "MemoryGames"

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
    mode: Mapped[str] = mapped_column(String(40), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    sequence_length: Mapped[int] = mapped_column(
        "sequenceLength",
        Integer,
        nullable=False,
    )
    round_count: Mapped[int] = mapped_column(
        "roundCount",
        Integer,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    sessions: Mapped[list["MemorySession"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )


class MemorySession(MemoryTrainerBase):
    __tablename__ = "MemorySessions"

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
    game_id: Mapped[str] = mapped_column(
        "gameId",
        String(36),
        ForeignKey("MemoryGames.id"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="active",
        server_default="active",
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        "startedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        "completedAt",
        DateTime(timezone=True),
        nullable=True,
    )

    game: Mapped[MemoryGame] = relationship(back_populates="sessions")
    rounds: Mapped[list["MemoryRound"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    performance: Mapped["MemoryPerformance | None"] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class MemoryRound(MemoryTrainerBase):
    __tablename__ = "MemoryRounds"
    __table_args__ = (
        UniqueConstraint(
            "sessionId",
            "roundNumber",
            name="uq_MemoryRounds_sessionId_roundNumber",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        "sessionId",
        String(36),
        ForeignKey("MemorySessions.id"),
        index=True,
        nullable=False,
    )
    round_number: Mapped[int] = mapped_column(
        "roundNumber",
        Integer,
        nullable=False,
    )
    sequence: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str | None] = mapped_column(
        "userAnswer",
        Text,
        nullable=True,
    )
    is_correct: Mapped[bool | None] = mapped_column("isCorrect", nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(
        "responseTimeMs",
        Integer,
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

    session: Mapped[MemorySession] = relationship(back_populates="rounds")


class MemoryPerformance(MemoryTrainerBase):
    __tablename__ = "MemoryPerformance"

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
    game_id: Mapped[str] = mapped_column(
        "gameId",
        String(36),
        ForeignKey("MemoryGames.id"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[str] = mapped_column(
        "sessionId",
        String(36),
        ForeignKey("MemorySessions.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    total_rounds: Mapped[int] = mapped_column("totalRounds", Integer, nullable=False)
    correct_rounds: Mapped[int] = mapped_column(
        "correctRounds",
        Integer,
        nullable=False,
    )
    wrong_rounds: Mapped[int] = mapped_column("wrongRounds", Integer, nullable=False)
    accuracy: Mapped[int] = mapped_column(Integer, nullable=False)
    average_response_time_ms: Mapped[int] = mapped_column(
        "averageResponseTimeMs",
        Integer,
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        "completedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session: Mapped[MemorySession] = relationship(back_populates="performance")
