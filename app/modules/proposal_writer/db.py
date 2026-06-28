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
            "TURSO_AUTH_TOKEN is required for Proposal Writer libSQL/Turso database URLs."
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


proposal_writer_engine = create_engine(
    _build_database_url(settings.PROPOSAL_WRITER_DATABASE_URL),
    connect_args=_build_connect_args(settings.PROPOSAL_WRITER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.PROPOSAL_WRITER_DATABASE_URL),
)
register_timing_engine(proposal_writer_engine, "proposal_writer")

ProposalWriterSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=proposal_writer_engine,
    class_=TimingSession,
)


class ProposalWriterBase(DeclarativeBase):
    pass


def get_proposal_writer_db() -> Generator[Session, None, None]:
    yield from get_timed_db(ProposalWriterSessionLocal, "proposal_writer")


def check_proposal_writer_database() -> bool:
    with proposal_writer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
