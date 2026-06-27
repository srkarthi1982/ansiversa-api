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
            "TURSO_AUTH_TOKEN is required for Email Assistant libSQL/Turso database URLs."
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


email_assistant_engine = create_engine(
    _build_database_url(settings.EMAIL_ASSISTANT_DATABASE_URL),
    connect_args=_build_connect_args(settings.EMAIL_ASSISTANT_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.EMAIL_ASSISTANT_DATABASE_URL),
)
register_timing_engine(email_assistant_engine, "email_assistant")

EmailAssistantSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=email_assistant_engine,
    class_=TimingSession,
)


class EmailAssistantBase(DeclarativeBase):
    pass


def get_email_assistant_db() -> Generator[Session, None, None]:
    yield from get_timed_db(EmailAssistantSessionLocal, "email_assistant")


def check_email_assistant_database() -> bool:
    with email_assistant_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
