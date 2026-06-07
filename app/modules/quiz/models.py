from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.quiz.db import QuizBase


class Platform(QuizBase):
    __tablename__ = "Platform"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False)
    icon: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str | None] = mapped_column(String, nullable=True)
    question_count: Mapped[int] = mapped_column("qCount", Integer, nullable=False)


class Subject(QuizBase):
    __tablename__ = "Subject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False)
    question_count: Mapped[int] = mapped_column("qCount", Integer, nullable=False)


class Topic(QuizBase):
    __tablename__ = "Topic"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column("subjectId", Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False)
    question_count: Mapped[int] = mapped_column("qCount", Integer, nullable=False)


class Roadmap(QuizBase):
    __tablename__ = "Roadmap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column("subjectId", Integer, nullable=False)
    topic_id: Mapped[int] = mapped_column("topicId", Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False)
    question_count: Mapped[int] = mapped_column("qCount", Integer, nullable=False)


class Question(QuizBase):
    __tablename__ = "Question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column("subjectId", Integer, nullable=False)
    topic_id: Mapped[int] = mapped_column("topicId", Integer, nullable=False)
    roadmap_id: Mapped[int] = mapped_column("roadmapId", Integer, nullable=False)
    question_text: Mapped[str] = mapped_column("q", Text, nullable=False)
    options_json: Mapped[str] = mapped_column("o", Text, nullable=False)
    answer_key: Mapped[str] = mapped_column("a", Text, nullable=False)
    explanation: Mapped[str] = mapped_column("e", Text, nullable=False)
    level: Mapped[str] = mapped_column("l", String(1), nullable=False)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False)


class Result(QuizBase):
    __tablename__ = "Result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column("userId", String(36), nullable=False)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column("subjectId", Integer, nullable=False)
    topic_id: Mapped[int] = mapped_column("topicId", Integer, nullable=False)
    roadmap_id: Mapped[int] = mapped_column("roadmapId", Integer, nullable=False)
    level: Mapped[str] = mapped_column(String(1), nullable=False)
    responses_json: Mapped[str] = mapped_column("responses", Text, nullable=False)
    mark: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class QuizAttempt(QuizBase):
    __tablename__ = "QuizAttempt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    platform_id: Mapped[int] = mapped_column("platformId", Integer, nullable=False)
    subject_id: Mapped[int] = mapped_column("subjectId", Integer, nullable=False)
    topic_id: Mapped[int] = mapped_column("topicId", Integer, nullable=False)
    roadmap_id: Mapped[int] = mapped_column("roadmapId", Integer, nullable=False)
    level: Mapped[str] = mapped_column(String(1), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress", server_default="in_progress", nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        "expiresAt", DateTime(timezone=True), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        "submittedAt", DateTime(timezone=True), nullable=True
    )
    result_id: Mapped[int | None] = mapped_column(
        "resultId", Integer, ForeignKey("Result.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class QuizAttemptQuestion(QuizBase):
    __tablename__ = "QuizAttemptQuestion"
    __table_args__ = (
        UniqueConstraint("attemptId", "questionId", name="quiz_attempt_question_unique"),
        UniqueConstraint("attemptId", "position", name="quiz_attempt_position_unique"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(
        "attemptId", Integer, ForeignKey("QuizAttempt.id"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        "questionId", Integer, ForeignKey("Question.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
