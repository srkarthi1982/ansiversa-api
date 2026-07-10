from sqlalchemy import distinct, func, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select, select

from app.modules.language_learning_buddy.models import LanguagePracticeSession, LanguageVocabulary


def get_vocabulary(db: Session, vocabulary_id: str) -> LanguageVocabulary | None:
    return db.get(LanguageVocabulary, vocabulary_id)


def get_session(db: Session, session_id: str) -> LanguagePracticeSession | None:
    return db.get(LanguagePracticeSession, session_id)


def _paginate(statement: Select[tuple[object]], page: int, page_size: int) -> Select[tuple[object]]:
    return statement.offset((page - 1) * page_size).limit(page_size)


def _vocabulary_search(statement: Select[tuple[LanguageVocabulary]], query: str | None) -> Select[tuple[LanguageVocabulary]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(
        or_(
            LanguageVocabulary.word.ilike(pattern),
            LanguageVocabulary.translation.ilike(pattern),
            LanguageVocabulary.language.ilike(pattern),
            LanguageVocabulary.category.ilike(pattern),
            LanguageVocabulary.notes.ilike(pattern),
        )
    )


def _session_search(statement: Select[tuple[LanguagePracticeSession]], query: str | None) -> Select[tuple[LanguagePracticeSession]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(
        or_(
            LanguagePracticeSession.notes.ilike(pattern),
            LanguageVocabulary.word.ilike(pattern),
            LanguageVocabulary.translation.ilike(pattern),
            LanguageVocabulary.language.ilike(pattern),
        )
    )


def list_vocabulary(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    language: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    sort: str = "updatedAt",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[LanguageVocabulary], int]:
    statement = (
        select(LanguageVocabulary)
        .options(joinedload(LanguageVocabulary.sessions))
        .where(LanguageVocabulary.owner_id == owner_id)
    )
    if language:
        statement = statement.where(LanguageVocabulary.language == language)
    if category:
        statement = statement.where(LanguageVocabulary.category == category)
    if difficulty:
        statement = statement.where(LanguageVocabulary.difficulty == difficulty)
    statement = _vocabulary_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = LanguageVocabulary.word if sort == "word" else LanguageVocabulary.updated_at
    statement = statement.order_by(sort_column.asc() if direction == "asc" else sort_column.desc(), LanguageVocabulary.word.asc())
    return list(db.execute(_paginate(statement, page, page_size)).unique().scalars().all()), total


def list_sessions(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    vocabulary_id: str | None = None,
    language: str | None = None,
    result: str | None = None,
    date_from: str | None = None,
    date_before: str | None = None,
    sort: str = "practicedAt",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[LanguagePracticeSession], int]:
    statement = (
        select(LanguagePracticeSession)
        .join(LanguagePracticeSession.vocabulary)
        .options(joinedload(LanguagePracticeSession.vocabulary))
        .where(LanguagePracticeSession.owner_id == owner_id)
    )
    if vocabulary_id:
        statement = statement.where(LanguagePracticeSession.vocabulary_id == vocabulary_id)
    if language:
        statement = statement.where(LanguageVocabulary.language == language)
    if result:
        statement = statement.where(LanguagePracticeSession.result == result)
    if date_from:
        statement = statement.where(LanguagePracticeSession.practiced_at >= date_from)
    if date_before:
        statement = statement.where(LanguagePracticeSession.practiced_at < date_before)
    statement = _session_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = LanguagePracticeSession.updated_at if sort == "updatedAt" else LanguagePracticeSession.practiced_at
    statement = statement.order_by(
        sort_column.asc() if direction == "asc" else sort_column.desc(),
        LanguagePracticeSession.created_at.desc(),
    )
    return list(db.execute(_paginate(statement, page, page_size)).scalars().all()), total


def count_vocabulary(db: Session, owner_id: str, *, difficulty: str | None = None) -> int:
    statement = select(func.count()).select_from(LanguageVocabulary).where(LanguageVocabulary.owner_id == owner_id)
    if difficulty:
        statement = statement.where(LanguageVocabulary.difficulty == difficulty)
    return db.scalar(statement) or 0


def count_languages(db: Session, owner_id: str) -> int:
    statement = select(func.count(distinct(LanguageVocabulary.language))).where(LanguageVocabulary.owner_id == owner_id)
    return db.scalar(statement) or 0


def count_sessions(
    db: Session,
    owner_id: str,
    *,
    date_from: str | None = None,
    date_before: str | None = None,
) -> int:
    statement = select(func.count()).select_from(LanguagePracticeSession).where(LanguagePracticeSession.owner_id == owner_id)
    if date_from:
        statement = statement.where(LanguagePracticeSession.practiced_at >= date_from)
    if date_before:
        statement = statement.where(LanguagePracticeSession.practiced_at < date_before)
    return db.scalar(statement) or 0


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
