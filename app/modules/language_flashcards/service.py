from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.language_flashcards.models import (
    LanguageCard,
    LanguageDeck,
    ReviewLog,
    StudySession,
)
from app.modules.language_flashcards.schemas import (
    LanguageFlashcardCardCreateRequest,
    LanguageFlashcardCardResponse,
    LanguageFlashcardCardUpdateRequest,
    LanguageFlashcardDeckCreateRequest,
    LanguageFlashcardDeckResponse,
    LanguageFlashcardDeckUpdateRequest,
    LanguageFlashcardReviewSubmitRequest,
    LanguageFlashcardReviewSummaryResponse,
    LanguageFlashcardSessionResponse,
)


@dataclass(frozen=True)
class DeckWithCount:
    id: str
    name: str
    language: str
    description: str | None
    card_count: int
    created_at: datetime
    updated_at: datetime


def _deck_response(deck: LanguageDeck, card_count: int) -> LanguageFlashcardDeckResponse:
    return LanguageFlashcardDeckResponse(
        id=deck.id,
        name=deck.name,
        language=deck.language,
        description=deck.description,
        card_count=card_count,
        created_at=deck.created_at,
        updated_at=deck.updated_at,
    )


def _get_owned_deck(db: Session, user: User, deck_id: str) -> LanguageDeck:
    deck = db.get(LanguageDeck, deck_id)
    if not deck or deck.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language flashcard deck was not found.",
        )

    return deck


def _get_owned_card(
    db: Session,
    user: User,
    deck_id: str,
    card_id: str,
) -> LanguageCard:
    deck = _get_owned_deck(db, user, deck_id)
    card = db.get(LanguageCard, card_id)
    if not card or card.deck_id != deck.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language flashcard card was not found.",
        )

    return card


def _count_cards(db: Session, deck_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(LanguageCard).where(
                LanguageCard.deck_id == deck_id
            )
        ).scalar_one()
    )


def list_decks(db: Session, user: User) -> list[LanguageFlashcardDeckResponse]:
    statement = (
        select(LanguageDeck, func.count(LanguageCard.id))
        .outerjoin(LanguageCard, LanguageCard.deck_id == LanguageDeck.id)
        .where(LanguageDeck.user_id == user.id)
        .group_by(LanguageDeck.id)
        .order_by(LanguageDeck.updated_at.desc(), LanguageDeck.name.asc())
    )

    return [
        _deck_response(deck, int(card_count))
        for deck, card_count in db.execute(statement).all()
    ]


def get_deck_detail(
    db: Session,
    user: User,
    deck_id: str,
) -> tuple[LanguageFlashcardDeckResponse, list[LanguageCard]]:
    deck = _get_owned_deck(db, user, deck_id)
    cards = list(
        db.execute(
            select(LanguageCard)
            .where(LanguageCard.deck_id == deck.id)
            .order_by(LanguageCard.created_at.asc())
        )
        .scalars()
        .all()
    )

    return _deck_response(deck, len(cards)), cards


def create_deck(
    db: Session,
    user: User,
    payload: LanguageFlashcardDeckCreateRequest,
) -> LanguageFlashcardDeckResponse:
    deck = LanguageDeck(
        user_id=user.id,
        name=payload.name,
        language=payload.language,
        description=payload.description,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)

    return _deck_response(deck, 0)


def update_deck(
    db: Session,
    user: User,
    deck_id: str,
    payload: LanguageFlashcardDeckUpdateRequest,
) -> LanguageFlashcardDeckResponse:
    deck = _get_owned_deck(db, user, deck_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(deck, field, value)
    db.commit()
    db.refresh(deck)

    return _deck_response(deck, _count_cards(db, deck.id))


def delete_deck(db: Session, user: User, deck_id: str) -> None:
    deck = _get_owned_deck(db, user, deck_id)
    session_ids = select(StudySession.id).where(StudySession.deck_id == deck.id)
    db.execute(delete(ReviewLog).where(ReviewLog.session_id.in_(session_ids)))
    db.execute(delete(StudySession).where(StudySession.deck_id == deck.id))
    db.execute(delete(LanguageCard).where(LanguageCard.deck_id == deck.id))
    db.delete(deck)
    db.commit()


def list_cards(db: Session, user: User, deck_id: str) -> list[LanguageCard]:
    deck = _get_owned_deck(db, user, deck_id)
    return list(
        db.execute(
            select(LanguageCard)
            .where(LanguageCard.deck_id == deck.id)
            .order_by(LanguageCard.created_at.asc())
        )
        .scalars()
        .all()
    )


def create_card(
    db: Session,
    user: User,
    deck_id: str,
    payload: LanguageFlashcardCardCreateRequest,
) -> LanguageCard:
    deck = _get_owned_deck(db, user, deck_id)
    card = LanguageCard(
        deck_id=deck.id,
        front=payload.front,
        back=payload.back,
        example_sentence=payload.example_sentence,
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return card


def update_card(
    db: Session,
    user: User,
    deck_id: str,
    card_id: str,
    payload: LanguageFlashcardCardUpdateRequest,
) -> LanguageCard:
    card = _get_owned_card(db, user, deck_id, card_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(card, field, value)
    db.commit()
    db.refresh(card)

    return card


def delete_card(db: Session, user: User, deck_id: str, card_id: str) -> None:
    card = _get_owned_card(db, user, deck_id, card_id)
    db.execute(delete(ReviewLog).where(ReviewLog.card_id == card.id))
    db.delete(card)
    db.commit()


def start_session(
    db: Session,
    user: User,
    deck_id: str,
) -> LanguageFlashcardSessionResponse:
    deck = _get_owned_deck(db, user, deck_id)
    cards = list_cards(db, user, deck.id)
    if not cards:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Add at least one card before starting practice.",
        )

    session = StudySession(
        user_id=user.id,
        deck_id=deck.id,
        total_cards=len(cards),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return LanguageFlashcardSessionResponse(
        id=session.id,
        deck_id=session.deck_id,
        total_cards=session.total_cards,
        started_at=session.started_at,
        cards=[
            LanguageFlashcardCardResponse.model_validate(card)
            for card in cards
        ],
    )


def submit_review(
    db: Session,
    user: User,
    session_id: str,
    payload: LanguageFlashcardReviewSubmitRequest,
) -> LanguageFlashcardReviewSummaryResponse:
    session = db.get(StudySession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language flashcard session was not found.",
        )
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This practice session has already been completed.",
        )

    deck = _get_owned_deck(db, user, session.deck_id)
    valid_card_ids = {
        card_id
        for card_id in db.execute(
            select(LanguageCard.id).where(LanguageCard.deck_id == deck.id)
        ).scalars()
    }
    submitted_card_ids = [review.card_id for review in payload.reviews]
    submitted_card_id_set = set(submitted_card_ids)

    if len(submitted_card_ids) != len(submitted_card_id_set):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review contains duplicate cards.",
        )

    if not submitted_card_id_set.issubset(valid_card_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review contains a card outside this deck.",
        )

    if submitted_card_id_set != valid_card_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review must include every card in this session.",
        )

    for review in payload.reviews:
        db.add(
            ReviewLog(
                session_id=session.id,
                card_id=review.card_id,
                is_known=review.is_known,
            )
        )

    completed_at = datetime.now(timezone.utc)
    known = sum(1 for review in payload.reviews if review.is_known)
    total = len(payload.reviews)
    session.status = "completed"
    session.completed_at = completed_at
    db.commit()

    return LanguageFlashcardReviewSummaryResponse(
        session_id=session.id,
        total_cards=total,
        known=known,
        unknown=total - known,
        accuracy=round((known / total) * 100),
        completed_at=completed_at,
    )
