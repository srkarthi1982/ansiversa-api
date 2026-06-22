from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.visiting_card_maker.db import get_visiting_card_maker_db
from app.modules.visiting_card_maker.schemas import (
    CardCreateRequest,
    CardUpdateRequest,
    VisitingCardListResponse,
    VisitingCardMakerDashboardResponse,
    VisitingCardResponse,
)
from app.modules.visiting_card_maker.service import (
    create_card,
    delete_card,
    duplicate_card,
    get_dashboard,
    list_cards,
    update_card,
)

router = APIRouter()


@router.get("/dashboard", response_model=VisitingCardMakerDashboardResponse)
def get_visiting_card_maker_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> VisitingCardMakerDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/cards", response_model=VisitingCardListResponse)
def get_visiting_cards(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> VisitingCardListResponse:
    return VisitingCardListResponse(items=list_cards(db, current_user))


@router.post(
    "/cards",
    response_model=VisitingCardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_visiting_card(
    payload: CardCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> VisitingCardResponse:
    return create_card(db, current_user, payload)


@router.put("/cards/{card_id}", response_model=VisitingCardResponse)
def update_visiting_card(
    card_id: Annotated[str, Path(min_length=1, max_length=80)],
    payload: CardUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> VisitingCardResponse:
    return update_card(db, current_user, card_id, payload)


@router.post(
    "/cards/{card_id}/duplicate",
    response_model=VisitingCardResponse,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_visiting_card(
    card_id: Annotated[str, Path(min_length=1, max_length=80)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> VisitingCardResponse:
    return duplicate_card(db, current_user, card_id)


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_visiting_card(
    card_id: Annotated[str, Path(min_length=1, max_length=80)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_visiting_card_maker_db)],
) -> None:
    delete_card(db, current_user, card_id)
