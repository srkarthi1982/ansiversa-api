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
            "TURSO_AUTH_TOKEN is required for LinkedIn Bio Optimizer libSQL/Turso database URLs."
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


linkedin_bio_optimizer_engine = create_engine(
    _build_database_url(settings.LINKEDIN_BIO_OPTIMIZER_DATABASE_URL),
    connect_args=_build_connect_args(settings.LINKEDIN_BIO_OPTIMIZER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.LINKEDIN_BIO_OPTIMIZER_DATABASE_URL),
)
register_timing_engine(linkedin_bio_optimizer_engine, "linkedin_bio_optimizer")

LinkedinBioOptimizerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=linkedin_bio_optimizer_engine,
    class_=TimingSession,
)


class LinkedinBioOptimizerBase(DeclarativeBase):
    pass


def get_linkedin_bio_optimizer_db() -> Generator[Session, None, None]:
    yield from get_timed_db(LinkedinBioOptimizerSessionLocal, "linkedin_bio_optimizer")


def check_linkedin_bio_optimizer_database() -> bool:
    with linkedin_bio_optimizer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
