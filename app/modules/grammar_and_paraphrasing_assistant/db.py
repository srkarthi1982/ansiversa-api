from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine
from app.modules.grammar_and_paraphrasing_assistant.constants import TIMING_LABEL


def _build_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"
    return database_url


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError("TURSO_AUTH_TOKEN is required for Grammar and Paraphrasing Assistant libSQL/Turso database URLs.")
    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {"poolclass": QueuePool, "pool_size": 5, "max_overflow": 10}
    return {}


grammar_and_paraphrasing_assistant_engine = create_engine(
    _build_database_url(settings.GRAMMAR_AND_PARAPHRASING_ASSISTANT_DATABASE_URL),
    connect_args=_build_connect_args(settings.GRAMMAR_AND_PARAPHRASING_ASSISTANT_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.GRAMMAR_AND_PARAPHRASING_ASSISTANT_DATABASE_URL),
)
register_timing_engine(grammar_and_paraphrasing_assistant_engine, TIMING_LABEL)

GrammarAndParaphrasingAssistantSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=grammar_and_paraphrasing_assistant_engine,
    class_=TimingSession,
)


class GrammarAndParaphrasingAssistantBase(DeclarativeBase):
    pass


def get_grammar_and_paraphrasing_assistant_db() -> Generator[Session, None, None]:
    yield from get_timed_db(GrammarAndParaphrasingAssistantSessionLocal, TIMING_LABEL)


def check_grammar_and_paraphrasing_assistant_database() -> bool:
    with grammar_and_paraphrasing_assistant_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
