from sqlalchemy import Boolean, Integer, String, Text
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
