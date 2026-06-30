from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.book_summary_generator import repository
from app.modules.book_summary_generator.models import BookCollection, BookSummary, SummaryHistory, SummaryNote
from app.modules.book_summary_generator.schemas import (
    BookCollectionCreateRequest,
    BookCollectionDetailResponse,
    BookCollectionSummaryResponse,
    BookCollectionUpdateRequest,
    BookSummaryCreateRequest,
    BookSummaryDetailResponse,
    BookSummaryGeneratorDashboardResponse,
    BookSummarySummaryResponse,
    BookSummaryUpdateRequest,
    SummaryHistoryCreateRequest,
    SummaryHistoryDetailResponse,
    SummaryHistorySummaryResponse,
    SummaryHistoryUpdateRequest,
    SummaryNoteCreateRequest,
    SummaryNoteDetailResponse,
    SummaryNoteSummaryResponse,
    SummaryNoteUpdateRequest,
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


def _get_owned_book(db: Session, user: User, book_id: int) -> BookCollection:
    book = repository.get_book(db, book_id)
    if not book or book.owner_id != user.id:
        _not_found("Book collection was not found.")
    return book


def _get_owned_summary(db: Session, user: User, summary_id: int) -> BookSummary:
    summary = repository.get_summary(db, summary_id)
    if not summary or summary.owner_id != user.id:
        _not_found("Book summary was not found.")
    return summary


def _get_owned_note(db: Session, user: User, note_id: int) -> SummaryNote:
    note = repository.get_note(db, note_id)
    if not note or note.owner_id != user.id:
        _not_found("Summary note was not found.")
    return note


def _get_owned_history(db: Session, user: User, history_id: int) -> SummaryHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Summary history record was not found.")
    return history


def _book_summary_response(db: Session, book: BookCollection) -> BookCollectionSummaryResponse:
    return BookCollectionSummaryResponse(
        id=book.id,
        platform_id=book.platform_id,
        title=book.title,
        author=book.author,
        category=book.category,
        source_type=book.source_type,
        status=book.status,
        source_preview=_preview(book.source_text),
        summary_count=repository.count_summaries(db, book.id),
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


def _book_detail_response(db: Session, book: BookCollection) -> BookCollectionDetailResponse:
    summary = _book_summary_response(db, book)
    return BookCollectionDetailResponse(
        **summary.model_dump(),
        source_text=book.source_text,
        notes=book.notes,
    )


def _summary_summary_response(db: Session, summary: BookSummary, book_title: str) -> BookSummarySummaryResponse:
    return BookSummarySummaryResponse(
        id=summary.id,
        platform_id=summary.platform_id,
        book_id=summary.book_id,
        book_title=book_title,
        title=summary.title,
        summary_type=summary.summary_type,
        status=summary.status,
        summary_preview=_preview(summary.summary_text),
        note_count=repository.count_notes(db, summary.id),
        history_count=repository.count_history(db, summary.id),
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


def _summary_detail_response(db: Session, summary: BookSummary, book_title: str) -> BookSummaryDetailResponse:
    item = _summary_summary_response(db, summary, book_title)
    return BookSummaryDetailResponse(
        **item.model_dump(),
        summary_text=summary.summary_text,
        key_points=summary.key_points,
        action_items=summary.action_items,
    )


def _note_summary_response(note: SummaryNote, summary_title: str) -> SummaryNoteSummaryResponse:
    return SummaryNoteSummaryResponse(
        id=note.id,
        platform_id=note.platform_id,
        summary_id=note.summary_id,
        summary_title=summary_title,
        title=note.title,
        note_type=note.note_type,
        content_preview=_preview(note.content),
        highlight_preview=_preview(note.highlight),
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _note_detail_response(note: SummaryNote, summary_title: str) -> SummaryNoteDetailResponse:
    item = _note_summary_response(note, summary_title)
    return SummaryNoteDetailResponse(
        **item.model_dump(),
        content=note.content,
        highlight=note.highlight,
    )


def _history_summary_response(history: SummaryHistory, summary_title: str) -> SummaryHistorySummaryResponse:
    return SummaryHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        summary_id=history.summary_id,
        summary_title=summary_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: SummaryHistory, summary_title: str) -> SummaryHistoryDetailResponse:
    item = _history_summary_response(history, summary_title)
    return SummaryHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_books(db: Session, user: User) -> list[BookCollectionSummaryResponse]:
    return [_book_summary_response(db, book) for book in repository.list_books(db, user.id)]


def create_book(db: Session, user: User, payload: BookCollectionCreateRequest) -> BookCollectionDetailResponse:
    book = BookCollection(owner_id=user.id, **payload.model_dump())
    repository.add(db, book)
    db.commit()
    db.refresh(book)
    return _book_detail_response(db, book)


def get_book(db: Session, user: User, book_id: int) -> BookCollectionDetailResponse:
    return _book_detail_response(db, _get_owned_book(db, user, book_id))


def update_book(db: Session, user: User, book_id: int, payload: BookCollectionUpdateRequest) -> BookCollectionDetailResponse:
    book = _get_owned_book(db, user, book_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return _book_detail_response(db, book)


def delete_book(db: Session, user: User, book_id: int) -> None:
    book = _get_owned_book(db, user, book_id)
    repository.delete_book_children(db, book.id)
    repository.delete_record(db, book)
    db.commit()


def list_summaries(db: Session, user: User) -> list[BookSummarySummaryResponse]:
    return [
        _summary_summary_response(db, summary, book.title)
        for summary, book in repository.list_summaries(db, user.id)
    ]


def create_summary(db: Session, user: User, payload: BookSummaryCreateRequest) -> BookSummaryDetailResponse:
    book = _get_owned_book(db, user, payload.book_id)
    summary = BookSummary(owner_id=user.id, **payload.model_dump())
    repository.add(db, summary)
    db.commit()
    db.refresh(summary)
    return _summary_detail_response(db, summary, book.title)


def get_summary(db: Session, user: User, summary_id: int) -> BookSummaryDetailResponse:
    summary = _get_owned_summary(db, user, summary_id)
    book = _get_owned_book(db, user, summary.book_id)
    return _summary_detail_response(db, summary, book.title)


def update_summary(db: Session, user: User, summary_id: int, payload: BookSummaryUpdateRequest) -> BookSummaryDetailResponse:
    summary = _get_owned_summary(db, user, summary_id)
    book = _get_owned_book(db, user, summary.book_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(summary, field, value)
    db.commit()
    db.refresh(summary)
    return _summary_detail_response(db, summary, book.title)


def delete_summary(db: Session, user: User, summary_id: int) -> None:
    summary = _get_owned_summary(db, user, summary_id)
    repository.delete_summary_children(db, summary.id)
    repository.delete_record(db, summary)
    db.commit()


def list_notes(db: Session, user: User) -> list[SummaryNoteSummaryResponse]:
    return [
        _note_summary_response(note, summary.title)
        for note, summary in repository.list_notes(db, user.id)
    ]


def create_note(db: Session, user: User, payload: SummaryNoteCreateRequest) -> SummaryNoteDetailResponse:
    summary = _get_owned_summary(db, user, payload.summary_id)
    note = SummaryNote(owner_id=user.id, **payload.model_dump())
    repository.add(db, note)
    db.commit()
    db.refresh(note)
    return _note_detail_response(note, summary.title)


def get_note(db: Session, user: User, note_id: int) -> SummaryNoteDetailResponse:
    note = _get_owned_note(db, user, note_id)
    summary = _get_owned_summary(db, user, note.summary_id)
    return _note_detail_response(note, summary.title)


def update_note(db: Session, user: User, note_id: int, payload: SummaryNoteUpdateRequest) -> SummaryNoteDetailResponse:
    note = _get_owned_note(db, user, note_id)
    summary = _get_owned_summary(db, user, note.summary_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return _note_detail_response(note, summary.title)


def delete_note(db: Session, user: User, note_id: int) -> None:
    note = _get_owned_note(db, user, note_id)
    repository.delete_record(db, note)
    db.commit()


def list_history(db: Session, user: User) -> list[SummaryHistorySummaryResponse]:
    return [
        _history_summary_response(history, summary.title)
        for history, summary in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: SummaryHistoryCreateRequest) -> SummaryHistoryDetailResponse:
    summary = _get_owned_summary(db, user, payload.summary_id)
    history = SummaryHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, summary.title)


def get_history(db: Session, user: User, history_id: int) -> SummaryHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    summary = _get_owned_summary(db, user, history.summary_id)
    return _history_detail_response(history, summary.title)


def update_history(db: Session, user: User, history_id: int, payload: SummaryHistoryUpdateRequest) -> SummaryHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    summary = _get_owned_summary(db, user, history.summary_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, summary.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> BookSummaryGeneratorDashboardResponse:
    books = list_books(db, user)
    summaries = list_summaries(db, user)
    notes = list_notes(db, user)
    history = list_history(db, user)
    return BookSummaryGeneratorDashboardResponse(
        books=books,
        summaries=summaries,
        notes=notes,
        history=history,
        book_count=len(books),
        summary_count=len(summaries),
        note_count=len(notes),
        history_count=len(history),
        reviewed_book_count=sum(1 for item in books if item.status == "reviewed"),
        completed_summary_count=sum(1 for item in summaries if item.status == "complete"),
    )
