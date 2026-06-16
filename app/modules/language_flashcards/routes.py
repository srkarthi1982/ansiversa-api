from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.language_flashcards.db import get_language_flashcards_db
from app.modules.language_flashcards.schemas import (
    LanguageFlashcardCardCreateRequest,
    LanguageFlashcardCardListResponse,
    LanguageFlashcardCardResponse,
    LanguageFlashcardCardUpdateRequest,
    LanguageFlashcardDeckCreateRequest,
    LanguageFlashcardDeckDetailResponse,
    LanguageFlashcardDeckListResponse,
    LanguageFlashcardDeckResponse,
    LanguageFlashcardDeckUpdateRequest,
    LanguageFlashcardReviewSubmitRequest,
    LanguageFlashcardReviewSummaryResponse,
    LanguageFlashcardSessionResponse,
)
from app.modules.language_flashcards.service import (
    create_card,
    create_deck,
    delete_card,
    delete_deck,
    get_deck_detail,
    list_cards,
    list_decks,
    start_session,
    submit_review,
    update_card,
    update_deck,
)

router = APIRouter()


@router.get("/decks", response_model=LanguageFlashcardDeckListResponse)
def get_language_flashcard_decks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardDeckListResponse:
    return LanguageFlashcardDeckListResponse(items=list_decks(db, current_user))


@router.post(
    "/decks",
    response_model=LanguageFlashcardDeckResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_language_flashcard_deck(
    payload: LanguageFlashcardDeckCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardDeckResponse:
    return create_deck(db, current_user, payload)


@router.get(
    "/decks/{deck_id}",
    response_model=LanguageFlashcardDeckDetailResponse,
)
def get_language_flashcard_deck(
    deck_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardDeckDetailResponse:
    deck, cards = get_deck_detail(db, current_user, deck_id)
    return LanguageFlashcardDeckDetailResponse(deck=deck, cards=cards)


@router.patch(
    "/decks/{deck_id}",
    response_model=LanguageFlashcardDeckResponse,
)
def update_language_flashcard_deck(
    deck_id: Annotated[str, Path(min_length=1)],
    payload: LanguageFlashcardDeckUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardDeckResponse:
    return update_deck(db, current_user, deck_id, payload)


@router.delete("/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_language_flashcard_deck(
    deck_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> None:
    delete_deck(db, current_user, deck_id)


@router.get(
    "/decks/{deck_id}/cards",
    response_model=LanguageFlashcardCardListResponse,
)
def get_language_flashcard_cards(
    deck_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardCardListResponse:
    return LanguageFlashcardCardListResponse(items=list_cards(db, current_user, deck_id))


@router.post(
    "/decks/{deck_id}/cards",
    response_model=LanguageFlashcardCardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_language_flashcard_card(
    deck_id: Annotated[str, Path(min_length=1)],
    payload: LanguageFlashcardCardCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardCardResponse:
    return create_card(db, current_user, deck_id, payload)


@router.patch(
    "/decks/{deck_id}/cards/{card_id}",
    response_model=LanguageFlashcardCardResponse,
)
def update_language_flashcard_card(
    deck_id: Annotated[str, Path(min_length=1)],
    card_id: Annotated[str, Path(min_length=1)],
    payload: LanguageFlashcardCardUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardCardResponse:
    return update_card(db, current_user, deck_id, card_id, payload)


@router.delete(
    "/decks/{deck_id}/cards/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_language_flashcard_card(
    deck_id: Annotated[str, Path(min_length=1)],
    card_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> None:
    delete_card(db, current_user, deck_id, card_id)


@router.post(
    "/decks/{deck_id}/sessions",
    response_model=LanguageFlashcardSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_language_flashcard_session(
    deck_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardSessionResponse:
    return start_session(db, current_user, deck_id)


@router.post(
    "/sessions/{session_id}/review",
    response_model=LanguageFlashcardReviewSummaryResponse,
)
def submit_language_flashcard_review(
    session_id: Annotated[str, Path(min_length=1)],
    payload: LanguageFlashcardReviewSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_language_flashcards_db)],
) -> LanguageFlashcardReviewSummaryResponse:
    return submit_review(db, current_user, session_id, payload)
