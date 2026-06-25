from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine


def _build_research_assistant_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_research_assistant_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Research Assistant libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


research_assistant_engine = create_engine(
    _build_research_assistant_database_url(settings.RESEARCH_ASSISTANT_DATABASE_URL),
    connect_args=_build_research_assistant_connect_args(
        settings.RESEARCH_ASSISTANT_DATABASE_URL
    ),
    pool_pre_ping=True,
)
register_timing_engine(research_assistant_engine, "research_assistant")

ResearchAssistantSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=research_assistant_engine,
    class_=TimingSession,
)


class ResearchAssistantBase(DeclarativeBase):
    pass


def get_research_assistant_db() -> Generator[Session, None, None]:
    yield from get_timed_db(ResearchAssistantSessionLocal, "research_assistant")


def check_research_assistant_database() -> bool:
    with research_assistant_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
