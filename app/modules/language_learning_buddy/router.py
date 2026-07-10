from typing import Literal

from fastapi import APIRouter, Query, Response, status

from app.modules.language_learning_buddy import service
from app.modules.language_learning_buddy.dependencies import CurrentLanguageLearningBuddyUser, LanguageLearningBuddyDB
from app.modules.language_learning_buddy.schemas import (
    LanguageLearningBuddyDashboardResponse,
    PaginatedPracticeSessionResponse,
    PaginatedVocabularyResponse,
    PracticeSessionCreateRequest,
    PracticeSessionDetailResponse,
    PracticeSessionUpdateRequest,
    VocabularyCreateRequest,
    VocabularyDetailResponse,
    VocabularyUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=LanguageLearningBuddyDashboardResponse)
def get_dashboard(db: LanguageLearningBuddyDB, current_user: CurrentLanguageLearningBuddyUser):
    return service.get_dashboard(db, current_user)


@router.get("/vocabulary", response_model=PaginatedVocabularyResponse)
def list_vocabulary(
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
    q: str | None = Query(default=None, max_length=120),
    language: str | None = Query(default=None, max_length=80),
    category: str | None = Query(default=None, max_length=80),
    difficulty: str | None = Query(default=None, max_length=40),
    sort: Literal["word", "updatedAt"] = "updatedAt",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_vocabulary(
        db,
        current_user,
        query=q,
        language=language,
        category=category,
        difficulty=difficulty,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/vocabulary", response_model=VocabularyDetailResponse, status_code=status.HTTP_201_CREATED)
def create_vocabulary(
    payload: VocabularyCreateRequest,
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
):
    return service.create_vocabulary(db, current_user, payload)


@router.get("/vocabulary/{vocabulary_id}", response_model=VocabularyDetailResponse)
def get_vocabulary(vocabulary_id: str, db: LanguageLearningBuddyDB, current_user: CurrentLanguageLearningBuddyUser):
    return service.get_vocabulary(db, current_user, vocabulary_id)


@router.put("/vocabulary/{vocabulary_id}", response_model=VocabularyDetailResponse)
def update_vocabulary(
    vocabulary_id: str,
    payload: VocabularyUpdateRequest,
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
):
    return service.update_vocabulary(db, current_user, vocabulary_id, payload)


@router.delete("/vocabulary/{vocabulary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vocabulary(vocabulary_id: str, db: LanguageLearningBuddyDB, current_user: CurrentLanguageLearningBuddyUser):
    service.delete_vocabulary(db, current_user, vocabulary_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/practice-sessions", response_model=PaginatedPracticeSessionResponse)
def list_sessions(
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
    q: str | None = Query(default=None, max_length=120),
    vocabulary_id: str | None = Query(default=None, alias="vocabularyId", max_length=36),
    language: str | None = Query(default=None, max_length=80),
    result: str | None = Query(default=None, max_length=40),
    date_from: str | None = Query(default=None, alias="dateFrom", max_length=40),
    date_before: str | None = Query(default=None, alias="dateBefore", max_length=40),
    sort: Literal["practicedAt", "updatedAt"] = "practicedAt",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_sessions(
        db,
        current_user,
        query=q,
        vocabulary_id=vocabulary_id,
        language=language,
        result=result,
        date_from=date_from,
        date_before=date_before,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/practice-sessions", response_model=PracticeSessionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: PracticeSessionCreateRequest,
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
):
    return service.create_session(db, current_user, payload)


@router.get("/practice-sessions/{session_id}", response_model=PracticeSessionDetailResponse)
def get_session(session_id: str, db: LanguageLearningBuddyDB, current_user: CurrentLanguageLearningBuddyUser):
    return service.get_session(db, current_user, session_id)


@router.put("/practice-sessions/{session_id}", response_model=PracticeSessionDetailResponse)
def update_session(
    session_id: str,
    payload: PracticeSessionUpdateRequest,
    db: LanguageLearningBuddyDB,
    current_user: CurrentLanguageLearningBuddyUser,
):
    return service.update_session(db, current_user, session_id, payload)


@router.delete("/practice-sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: LanguageLearningBuddyDB, current_user: CurrentLanguageLearningBuddyUser):
    service.delete_session(db, current_user, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
