from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_quiz_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_quiz_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.QUIZ_TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "QUIZ_TURSO_AUTH_TOKEN is required for Quiz libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.QUIZ_TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


quiz_engine = create_engine(
    _build_quiz_database_url(settings.QUIZ_DATABASE_URL),
    connect_args=_build_quiz_connect_args(settings.QUIZ_DATABASE_URL),
    pool_pre_ping=True,
)

QuizSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=quiz_engine,
)


class QuizBase(DeclarativeBase):
    pass


def get_quiz_db() -> Generator[Session, None, None]:
    db = QuizSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_quiz_database() -> bool:
    with quiz_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
