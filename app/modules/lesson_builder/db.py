from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine


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


def _build_lesson_builder_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 10,
        }

    return {}


lesson_builder_engine = create_engine(
    _build_lesson_builder_database_url(settings.LESSON_BUILDER_DATABASE_URL),
    connect_args=_build_lesson_builder_connect_args(
        settings.LESSON_BUILDER_DATABASE_URL
    ),
    pool_pre_ping=True,
    **_build_lesson_builder_engine_kwargs(settings.LESSON_BUILDER_DATABASE_URL),
)
register_timing_engine(lesson_builder_engine, "lesson_builder")

LessonBuilderSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=lesson_builder_engine,
    class_=TimingSession,
)


class LessonBuilderBase(DeclarativeBase):
    pass


def get_lesson_builder_db() -> Generator[Session, None, None]:
    yield from get_timed_db(LessonBuilderSessionLocal, "lesson_builder")


def check_lesson_builder_database() -> bool:
    with lesson_builder_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
