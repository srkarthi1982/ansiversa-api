from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_language_flashcards_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_language_flashcards_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Language Flashcards libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


language_flashcards_engine = create_engine(
    _build_language_flashcards_database_url(settings.LANGUAGE_FLASHCARDS_DATABASE_URL),
    connect_args=_build_language_flashcards_connect_args(
        settings.LANGUAGE_FLASHCARDS_DATABASE_URL
    ),
    pool_pre_ping=True,
)

LanguageFlashcardsSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=language_flashcards_engine,
)


class LanguageFlashcardsBase(DeclarativeBase):
    pass


def get_language_flashcards_db() -> Generator[Session, None, None]:
    db = LanguageFlashcardsSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_language_flashcards_database() -> bool:
    with language_flashcards_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
