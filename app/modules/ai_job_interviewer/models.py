from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.ai_job_interviewer.db import AiJobInterviewerBase


class AiJobInterviewSession(AiJobInterviewerBase):
    __tablename__ = "AiJobInterviewSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    role_title: Mapped[str] = mapped_column("roleTitle", String(140), nullable=False)
    company_name: Mapped[str | None] = mapped_column("companyName", String(140), nullable=True)
    experience_level: Mapped[str] = mapped_column(
        "experienceLevel",
        String(40),
        default="mid",
        server_default="mid",
        nullable=False,
    )
    interview_type: Mapped[str] = mapped_column(
        "interviewType",
        String(40),
        default="behavioral",
        server_default="behavioral",
        nullable=False,
    )
    target_date: Mapped[date | None] = mapped_column("targetDate", Date(), nullable=True)
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

    questions: Mapped[list["AiJobInterviewQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    answers: Mapped[list["AiJobInterviewAnswer"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    results: Mapped[list["AiJobInterviewResult"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class AiJobInterviewQuestion(AiJobInterviewerBase):
    __tablename__ = "AiJobInterviewQuestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        "sessionId",
        Integer,
        ForeignKey("AiJobInterviewSessions.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(80),
        default="behavioral",
        server_default="behavioral",
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
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

    session: Mapped[AiJobInterviewSession] = relationship(back_populates="questions")
    answers: Mapped[list["AiJobInterviewAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )


class AiJobInterviewAnswer(AiJobInterviewerBase):
    __tablename__ = "AiJobInterviewAnswers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        "sessionId",
        Integer,
        ForeignKey("AiJobInterviewSessions.id"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        "questionId",
        Integer,
        ForeignKey("AiJobInterviewQuestions.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column("answerText", Text, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=3, server_default="3", nullable=False)
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

    session: Mapped[AiJobInterviewSession] = relationship(back_populates="answers")
    question: Mapped[AiJobInterviewQuestion] = relationship(back_populates="answers")


class AiJobInterviewResult(AiJobInterviewerBase):
    __tablename__ = "AiJobInterviewResults"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        "sessionId",
        Integer,
        ForeignKey("AiJobInterviewSessions.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    progress_score: Mapped[int] = mapped_column(
        "progressScore",
        Integer,
        default=3,
        server_default="3",
        nullable=False,
    )
    strengths: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvements: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column("nextSteps", Text, nullable=True)
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

    session: Mapped[AiJobInterviewSession] = relationship(back_populates="results")
