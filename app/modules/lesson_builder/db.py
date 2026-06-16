from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_lesson_builder_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_lesson_builder_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Lesson Builder libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


lesson_builder_engine = create_engine(
    _build_lesson_builder_database_url(settings.LESSON_BUILDER_DATABASE_URL),
    connect_args=_build_lesson_builder_connect_args(
        settings.LESSON_BUILDER_DATABASE_URL
    ),
    pool_pre_ping=True,
)

LessonBuilderSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=lesson_builder_engine,
)


class LessonBuilderBase(DeclarativeBase):
    pass


def get_lesson_builder_db() -> Generator[Session, None, None]:
    db = LessonBuilderSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_lesson_builder_database() -> bool:
    with lesson_builder_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
