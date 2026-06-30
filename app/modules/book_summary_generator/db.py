from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine
from app.modules.book_summary_generator.constants import TIMING_LABEL


def _build_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"
    return database_url


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError("TURSO_AUTH_TOKEN is required for Book Summary Generator libSQL/Turso database URLs.")
    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {"poolclass": QueuePool, "pool_size": 5, "max_overflow": 10}
    return {}


book_summary_generator_engine = create_engine(
    _build_database_url(settings.BOOK_SUMMARY_GENERATOR_DATABASE_URL),
    connect_args=_build_connect_args(settings.BOOK_SUMMARY_GENERATOR_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.BOOK_SUMMARY_GENERATOR_DATABASE_URL),
)
register_timing_engine(book_summary_generator_engine, TIMING_LABEL)

BookSummaryGeneratorSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=book_summary_generator_engine,
    class_=TimingSession,
)


class BookSummaryGeneratorBase(DeclarativeBase):
    pass


def get_book_summary_generator_db() -> Generator[Session, None, None]:
    yield from get_timed_db(BookSummaryGeneratorSessionLocal, TIMING_LABEL)


def check_book_summary_generator_database() -> bool:
    with book_summary_generator_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
