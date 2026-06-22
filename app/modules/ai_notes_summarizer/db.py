from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_ai_notes_summarizer_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_ai_notes_summarizer_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for AI Notes Summarizer libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


ai_notes_summarizer_engine = create_engine(
    _build_ai_notes_summarizer_database_url(
        settings.AI_NOTES_SUMMARIZER_DATABASE_URL
    ),
    connect_args=_build_ai_notes_summarizer_connect_args(
        settings.AI_NOTES_SUMMARIZER_DATABASE_URL
    ),
    pool_pre_ping=True,
)

AiNotesSummarizerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=ai_notes_summarizer_engine,
)


class AiNotesSummarizerBase(DeclarativeBase):
    pass


def get_ai_notes_summarizer_db() -> Generator[Session, None, None]:
    db = AiNotesSummarizerSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_ai_notes_summarizer_database() -> bool:
    with ai_notes_summarizer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
