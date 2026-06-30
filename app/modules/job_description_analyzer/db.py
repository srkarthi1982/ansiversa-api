from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.timing import TimingSession, get_timed_db, register_timing_engine
from app.modules.job_description_analyzer.constants import TIMING_LABEL


def _build_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"
    return database_url


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError("TURSO_AUTH_TOKEN is required for Job Description Analyzer libSQL/Turso database URLs.")
    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://"):
        return {"poolclass": QueuePool, "pool_size": 5, "max_overflow": 10}
    return {}


job_description_analyzer_engine = create_engine(
    _build_database_url(settings.JOB_DESCRIPTION_ANALYZER_DATABASE_URL),
    connect_args=_build_connect_args(settings.JOB_DESCRIPTION_ANALYZER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.JOB_DESCRIPTION_ANALYZER_DATABASE_URL),
)
register_timing_engine(job_description_analyzer_engine, TIMING_LABEL)

JobDescriptionAnalyzerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=job_description_analyzer_engine,
    class_=TimingSession,
)


class JobDescriptionAnalyzerBase(DeclarativeBase):
    pass


def get_job_description_analyzer_db() -> Generator[Session, None, None]:
    yield from get_timed_db(JobDescriptionAnalyzerSessionLocal, TIMING_LABEL)


def check_job_description_analyzer_database() -> bool:
    with job_description_analyzer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
