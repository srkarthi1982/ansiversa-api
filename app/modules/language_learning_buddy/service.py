from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.language_learning_buddy import repository
from app.modules.language_learning_buddy.models import LanguagePracticeSession, LanguageVocabulary
from app.modules.language_learning_buddy.schemas import (
    LanguageLearningBuddyDashboardResponse,
    PaginatedPracticeSessionResponse,
    PaginatedVocabularyResponse,
    PracticeSessionCreateRequest,
    PracticeSessionDetailResponse,
    PracticeSessionSummaryResponse,
    PracticeSessionUpdateRequest,
    VocabularyCreateRequest,
    VocabularyDetailResponse,
    VocabularySummaryResponse,
    VocabularyUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_vocabulary(db: Session, user: User, vocabulary_id: str) -> LanguageVocabulary:
    vocabulary = repository.get_vocabulary(db, vocabulary_id)
    if not vocabulary or vocabulary.owner_id != user.id:
        _not_found("Vocabulary item was not found.")
    return vocabulary


def _get_owned_session(db: Session, user: User, session_id: str) -> LanguagePracticeSession:
    session = repository.get_session(db, session_id)
    if not session or session.owner_id != user.id:
        _not_found("Practice session was not found.")
    return session


def _last_practiced_at(vocabulary: LanguageVocabulary) -> str | None:
    if not vocabulary.sessions:
        return None
    return max(session.practiced_at for session in vocabulary.sessions)


def _vocabulary_summary_response(vocabulary: LanguageVocabulary) -> VocabularySummaryResponse:
    return VocabularySummaryResponse(
        id=vocabulary.id,
        word=vocabulary.word,
        translation=vocabulary.translation,
        language=vocabulary.language,
        category=vocabulary.category,
        difficulty=vocabulary.difficulty,
        notes_preview=_preview(vocabulary.notes),
        session_count=len(vocabulary.sessions),
        last_practiced_at=_last_practiced_at(vocabulary),
        created_at=vocabulary.created_at,
        updated_at=vocabulary.updated_at,
    )


def _vocabulary_detail_response(vocabulary: LanguageVocabulary) -> VocabularyDetailResponse:
    sessions = sorted(vocabulary.sessions, key=lambda item: (item.practiced_at, item.created_at), reverse=True)
    return VocabularyDetailResponse(
        **_vocabulary_summary_response(vocabulary).model_dump(),
        notes=vocabulary.notes,
        sessions=[_session_summary_response(session) for session in sessions],
    )


def _session_summary_response(session: LanguagePracticeSession) -> PracticeSessionSummaryResponse:
    return PracticeSessionSummaryResponse(
        id=session.id,
        vocabulary_id=session.vocabulary_id,
        word=session.vocabulary.word,
        translation=session.vocabulary.translation,
        language=session.vocabulary.language,
        category=session.vocabulary.category,
        practiced_at=session.practiced_at,
        result=session.result,
        confidence=session.confidence,
        notes_preview=_preview(session.notes),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _session_detail_response(session: LanguagePracticeSession) -> PracticeSessionDetailResponse:
    return PracticeSessionDetailResponse(**_session_summary_response(session).model_dump(), notes=session.notes)


def _current_week_range() -> tuple[str, str]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat(), (monday + timedelta(days=7)).isoformat()


def list_vocabulary(
    db: Session,
    user: User,
    *,
    query: str | None,
    language: str | None,
    category: str | None,
    difficulty: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedVocabularyResponse:
    vocabulary, total = repository.list_vocabulary(
        db,
        user.id,
        query=query,
        language=language,
        category=category,
        difficulty=difficulty,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedVocabularyResponse(
        items=[_vocabulary_summary_response(item) for item in vocabulary],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_vocabulary(db: Session, user: User, payload: VocabularyCreateRequest) -> VocabularyDetailResponse:
    vocabulary = LanguageVocabulary(owner_id=user.id, **payload.model_dump())
    repository.add(db, vocabulary)
    db.commit()
    db.refresh(vocabulary)
    return _vocabulary_detail_response(vocabulary)


def get_vocabulary(db: Session, user: User, vocabulary_id: str) -> VocabularyDetailResponse:
    return _vocabulary_detail_response(_get_owned_vocabulary(db, user, vocabulary_id))


def update_vocabulary(
    db: Session,
    user: User,
    vocabulary_id: str,
    payload: VocabularyUpdateRequest,
) -> VocabularyDetailResponse:
    vocabulary = _get_owned_vocabulary(db, user, vocabulary_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vocabulary, field, value)
    db.commit()
    db.refresh(vocabulary)
    return _vocabulary_detail_response(vocabulary)


def delete_vocabulary(db: Session, user: User, vocabulary_id: str) -> None:
    vocabulary = _get_owned_vocabulary(db, user, vocabulary_id)
    repository.delete_record(db, vocabulary)
    db.commit()


def list_sessions(
    db: Session,
    user: User,
    *,
    query: str | None,
    vocabulary_id: str | None,
    language: str | None,
    result: str | None,
    date_from: str | None,
    date_before: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedPracticeSessionResponse:
    if vocabulary_id:
        _get_owned_vocabulary(db, user, vocabulary_id)
    sessions, total = repository.list_sessions(
        db,
        user.id,
        query=query,
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
    return PaginatedPracticeSessionResponse(
        items=[_session_summary_response(session) for session in sessions],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_session(db: Session, user: User, payload: PracticeSessionCreateRequest) -> PracticeSessionDetailResponse:
    data = payload.model_dump()
    _get_owned_vocabulary(db, user, data["vocabulary_id"])
    session = LanguagePracticeSession(owner_id=user.id, **data)
    repository.add(db, session)
    db.commit()
    db.refresh(session)
    return _session_detail_response(session)


def get_session(db: Session, user: User, session_id: str) -> PracticeSessionDetailResponse:
    return _session_detail_response(_get_owned_session(db, user, session_id))


def update_session(
    db: Session,
    user: User,
    session_id: str,
    payload: PracticeSessionUpdateRequest,
) -> PracticeSessionDetailResponse:
    session = _get_owned_session(db, user, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return _session_detail_response(session)


def delete_session(db: Session, user: User, session_id: str) -> None:
    session = _get_owned_session(db, user, session_id)
    repository.delete_record(db, session)
    db.commit()


def get_dashboard(db: Session, user: User) -> LanguageLearningBuddyDashboardResponse:
    vocabulary, _ = repository.list_vocabulary(db, user.id, page_size=200)
    sessions, _ = repository.list_sessions(db, user.id, page_size=200)
    recent_sessions, _ = repository.list_sessions(db, user.id, sort="updatedAt", direction="desc", page_size=5)
    week_start, week_end = _current_week_range()
    return LanguageLearningBuddyDashboardResponse(
        vocabulary=[_vocabulary_summary_response(item) for item in vocabulary],
        sessions=[_session_summary_response(session) for session in sessions],
        vocabulary_count=repository.count_vocabulary(db, user.id),
        language_count=repository.count_languages(db, user.id),
        practice_count=repository.count_sessions(db, user.id),
        mastered_count=repository.count_vocabulary(db, user.id, difficulty="mastered"),
        weekly_practice_count=repository.count_sessions(db, user.id, date_from=week_start, date_before=week_end),
        recent_sessions=[_session_summary_response(session) for session in recent_sessions],
    )
