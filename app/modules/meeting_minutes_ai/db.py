from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine


def _build_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Meeting Minutes AI libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 10,
        }

    return {}


meeting_minutes_ai_engine = create_engine(
    _build_database_url(settings.MEETING_MINUTES_AI_DATABASE_URL),
    connect_args=_build_connect_args(settings.MEETING_MINUTES_AI_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.MEETING_MINUTES_AI_DATABASE_URL),
)
register_timing_engine(meeting_minutes_ai_engine, "meeting_minutes_ai")

MeetingMinutesAiSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=meeting_minutes_ai_engine,
    class_=TimingSession,
)


class MeetingMinutesAiBase(DeclarativeBase):
    pass


def get_meeting_minutes_ai_db() -> Generator[Session, None, None]:
    yield from get_timed_db(MeetingMinutesAiSessionLocal, "meeting_minutes_ai")


def check_meeting_minutes_ai_database() -> bool:
    with meeting_minutes_ai_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
