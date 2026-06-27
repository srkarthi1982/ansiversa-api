from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine


def _build_memory_trainer_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_memory_trainer_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Memory Trainer libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


def _build_memory_trainer_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 10,
        }

    return {}


memory_trainer_engine = create_engine(
    _build_memory_trainer_database_url(settings.MEMORY_TRAINER_DATABASE_URL),
    connect_args=_build_memory_trainer_connect_args(
        settings.MEMORY_TRAINER_DATABASE_URL
    ),
    pool_pre_ping=True,
    **_build_memory_trainer_engine_kwargs(settings.MEMORY_TRAINER_DATABASE_URL),
)
register_timing_engine(memory_trainer_engine, "memory_trainer")

MemoryTrainerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=memory_trainer_engine,
    class_=TimingSession,
)


class MemoryTrainerBase(DeclarativeBase):
    pass


def get_memory_trainer_db() -> Generator[Session, None, None]:
    yield from get_timed_db(MemoryTrainerSessionLocal, "memory_trainer")


def check_memory_trainer_database() -> bool:
    with memory_trainer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
