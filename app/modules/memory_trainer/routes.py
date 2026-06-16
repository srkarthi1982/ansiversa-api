from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.memory_trainer.db import get_memory_trainer_db
from app.modules.memory_trainer.schemas import (
    MemoryGameCreateRequest,
    MemoryGameListResponse,
    MemoryGameResponse,
    MemoryGameUpdateRequest,
    MemoryPerformanceResponse,
    MemoryProgressResponse,
    MemoryReviewResponse,
    MemoryRoundResponse,
    MemoryRoundSubmitRequest,
    MemorySessionDetailResponse,
)
from app.modules.memory_trainer.service import (
    create_game,
    delete_game,
    get_game,
    get_progress,
    get_review,
    get_session,
    list_games,
    start_session,
    submit_round,
    submit_session,
    update_game,
)

router = APIRouter()


@router.get("/games", response_model=MemoryGameListResponse)
def get_games(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryGameListResponse:
    return MemoryGameListResponse(items=list_games(db, current_user))


@router.post(
    "/games",
    response_model=MemoryGameResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory_game(
    payload: MemoryGameCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryGameResponse:
    return create_game(db, current_user, payload)


@router.get("/games/{game_id}", response_model=MemoryGameResponse)
def get_memory_game(
    game_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryGameResponse:
    return get_game(db, current_user, game_id)


@router.patch("/games/{game_id}", response_model=MemoryGameResponse)
def update_memory_game(
    game_id: Annotated[str, Path(min_length=1)],
    payload: MemoryGameUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryGameResponse:
    return update_game(db, current_user, game_id, payload)


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory_game(
    game_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> None:
    delete_game(db, current_user, game_id)


@router.post(
    "/games/{game_id}/sessions",
    response_model=MemorySessionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory_session(
    game_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemorySessionDetailResponse:
    return start_session(db, current_user, game_id)


@router.get("/sessions/{session_id}", response_model=MemorySessionDetailResponse)
def get_memory_session(
    session_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemorySessionDetailResponse:
    return get_session(db, current_user, session_id)


@router.post("/sessions/{session_id}/rounds", response_model=MemoryRoundResponse)
def submit_memory_round(
    session_id: Annotated[str, Path(min_length=1)],
    payload: MemoryRoundSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryRoundResponse:
    return submit_round(db, current_user, session_id, payload)


@router.post("/sessions/{session_id}/submit", response_model=MemoryPerformanceResponse)
def submit_memory_session(
    session_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryPerformanceResponse:
    return submit_session(db, current_user, session_id)


@router.get("/sessions/{session_id}/review", response_model=MemoryReviewResponse)
def get_memory_review(
    session_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryReviewResponse:
    return get_review(db, current_user, session_id)


@router.get("/progress", response_model=MemoryProgressResponse)
def get_memory_progress(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_memory_trainer_db)],
) -> MemoryProgressResponse:
    return get_progress(db, current_user)
