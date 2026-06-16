from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import ParentBase


class ExamPaper(ParentBase):
    __tablename__ = "ExamPapers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    subject: Mapped[str] = mapped_column(String(140), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(
        "durationMinutes",
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

    questions: Mapped[list["ExamQuestion"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class ExamQuestion(ParentBase):
    __tablename__ = "ExamQuestions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    paper_id: Mapped[str] = mapped_column(
        "paperId",
        String(36),
        ForeignKey("ExamPapers.id"),
        index=True,
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        "questionText",
        Text,
        nullable=False,
    )
    option_a: Mapped[str] = mapped_column("optionA", String(500), nullable=False)
    option_b: Mapped[str] = mapped_column("optionB", String(500), nullable=False)
    option_c: Mapped[str] = mapped_column("optionC", String(500), nullable=False)
    option_d: Mapped[str] = mapped_column("optionD", String(500), nullable=False)
    correct_option: Mapped[str] = mapped_column(
        "correctOption",
        String(1),
        nullable=False,
    )
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    marks: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
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

    paper: Mapped[ExamPaper] = relationship(back_populates="questions")


class ExamAttempt(ParentBase):
    __tablename__ = "ExamAttempts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        ForeignKey("Users.id"),
        index=True,
        nullable=False,
    )
    paper_id: Mapped[str] = mapped_column(
        "paperId",
        String(36),
        ForeignKey("ExamPapers.id"),
        index=True,
        nullable=False,
    )
    total_questions: Mapped[int] = mapped_column(
        "totalQuestions",
        Integer,
        nullable=False,
    )
    total_marks: Mapped[int] = mapped_column("totalMarks", Integer, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    submitted_at: Mapped[datetime | None] = mapped_column(
        "submittedAt",
        DateTime(timezone=True),
        nullable=True,
    )


class ExamAnswer(ParentBase):
    __tablename__ = "ExamAnswers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    attempt_id: Mapped[str] = mapped_column(
        "attemptId",
        String(36),
        ForeignKey("ExamAttempts.id"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(
        "questionId",
        String(36),
        ForeignKey("ExamQuestions.id"),
        index=True,
        nullable=False,
    )
    selected_option: Mapped[str] = mapped_column(
        "selectedOption",
        String(1),
        nullable=False,
    )
    is_correct: Mapped[bool | None] = mapped_column("isCorrect", nullable=True)
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
