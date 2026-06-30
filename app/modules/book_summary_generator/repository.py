from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.book_summary_generator.models import (
    BookCollection,
    BookSummary,
    SummaryHistory,
    SummaryNote,
)


def get_book(db: Session, book_id: int) -> BookCollection | None:
    return db.get(BookCollection, book_id)


def get_summary(db: Session, summary_id: int) -> BookSummary | None:
    return db.get(BookSummary, summary_id)


def get_note(db: Session, note_id: int) -> SummaryNote | None:
    return db.get(SummaryNote, note_id)


def get_history(db: Session, history_id: int) -> SummaryHistory | None:
    return db.get(SummaryHistory, history_id)


def list_books(db: Session, owner_id: str) -> list[BookCollection]:
    return list(
        db.execute(
            select(BookCollection)
            .where(BookCollection.owner_id == owner_id)
            .order_by(BookCollection.updated_at.desc(), BookCollection.title.asc())
        )
        .scalars()
        .all()
    )


def list_summaries(db: Session, owner_id: str) -> list[tuple[BookSummary, BookCollection]]:
    return list(
        db.execute(
            select(BookSummary, BookCollection)
            .join(BookCollection, BookCollection.id == BookSummary.book_id)
            .where(BookSummary.owner_id == owner_id)
            .order_by(BookSummary.updated_at.desc(), BookSummary.title.asc())
        ).all()
    )


def list_notes(db: Session, owner_id: str) -> list[tuple[SummaryNote, BookSummary]]:
    return list(
        db.execute(
            select(SummaryNote, BookSummary)
            .join(BookSummary, BookSummary.id == SummaryNote.summary_id)
            .where(SummaryNote.owner_id == owner_id)
            .order_by(SummaryNote.updated_at.desc(), SummaryNote.title.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[SummaryHistory, BookSummary]]:
    return list(
        db.execute(
            select(SummaryHistory, BookSummary)
            .join(BookSummary, BookSummary.id == SummaryHistory.summary_id)
            .where(SummaryHistory.owner_id == owner_id)
            .order_by(SummaryHistory.updated_at.desc(), SummaryHistory.occurred_at.desc())
        ).all()
    )


def count_summaries(db: Session, book_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(BookSummary).where(BookSummary.book_id == book_id)).scalar_one())


def count_notes(db: Session, summary_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SummaryNote).where(SummaryNote.summary_id == summary_id)).scalar_one())


def count_history(db: Session, summary_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SummaryHistory).where(SummaryHistory.summary_id == summary_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_book_children(db: Session, book_id: int) -> None:
    summary_ids = list(db.execute(select(BookSummary.id).where(BookSummary.book_id == book_id)).scalars().all())
    if summary_ids:
        db.execute(delete(SummaryNote).where(SummaryNote.summary_id.in_(summary_ids)))
        db.execute(delete(SummaryHistory).where(SummaryHistory.summary_id.in_(summary_ids)))
    db.execute(delete(BookSummary).where(BookSummary.book_id == book_id))


def delete_summary_children(db: Session, summary_id: int) -> None:
    db.execute(delete(SummaryNote).where(SummaryNote.summary_id == summary_id))
    db.execute(delete(SummaryHistory).where(SummaryHistory.summary_id == summary_id))
