from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.language_learning_buddy.db import LanguageLearningBuddyBase


def _uuid() -> str:
    return str(uuid4())


class LanguageVocabulary(LanguageLearningBuddyBase):
    __tablename__ = "LanguageVocabulary"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    word: Mapped[str] = mapped_column(String(180), nullable=False)
    translation: Mapped[str] = mapped_column(String(180), nullable=False)
    language: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(40), default="new", server_default="new", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sessions: Mapped[list["LanguagePracticeSession"]] = relationship(
        back_populates="vocabulary",
        cascade="all, delete-orphan",
    )


class LanguagePracticeSession(LanguageLearningBuddyBase):
    __tablename__ = "LanguagePracticeSessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vocabulary_id: Mapped[str] = mapped_column(
        "vocabularyId",
        String(36),
        ForeignKey("LanguageVocabulary.id"),
        index=True,
        nullable=False,
    )
    practiced_at: Mapped[str] = mapped_column("practicedAt", String(40), index=True, nullable=False)
    result: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    vocabulary: Mapped[LanguageVocabulary] = relationship(back_populates="sessions")
