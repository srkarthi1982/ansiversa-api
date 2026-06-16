from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.language_flashcards.db import LanguageFlashcardsBase


class LanguageDeck(LanguageFlashcardsBase):
    __tablename__ = "LanguageDecks"

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
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    language: Mapped[str] = mapped_column(String(120), nullable=False)
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

    cards: Mapped[list["LanguageCard"]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
    )


class LanguageCard(LanguageFlashcardsBase):
    __tablename__ = "LanguageCards"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    deck_id: Mapped[str] = mapped_column(
        "deckId",
        String(36),
        ForeignKey("LanguageDecks.id"),
        index=True,
        nullable=False,
    )
    front: Mapped[str] = mapped_column(String(500), nullable=False)
    back: Mapped[str] = mapped_column(String(500), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(
        "exampleSentence",
        Text,
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

    deck: Mapped[LanguageDeck] = relationship(back_populates="cards")


class StudySession(LanguageFlashcardsBase):
    __tablename__ = "StudySessions"

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
    deck_id: Mapped[str] = mapped_column(
        "deckId",
        String(36),
        ForeignKey("LanguageDecks.id"),
        index=True,
        nullable=False,
    )
    total_cards: Mapped[int] = mapped_column(
        "totalCards",
        Integer,
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


class ReviewLog(LanguageFlashcardsBase):
    __tablename__ = "ReviewLogs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        "sessionId",
        String(36),
        ForeignKey("StudySessions.id"),
        index=True,
        nullable=False,
    )
    card_id: Mapped[str] = mapped_column(
        "cardId",
        String(36),
        ForeignKey("LanguageCards.id"),
        index=True,
        nullable=False,
    )
    is_known: Mapped[bool] = mapped_column(
        "isKnown",
        Boolean,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
