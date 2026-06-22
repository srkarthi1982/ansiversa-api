from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Resume Builder libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


resume_builder_engine = create_engine(
    _build_database_url(settings.RESUME_BUILDER_DATABASE_URL),
    connect_args=_build_connect_args(settings.RESUME_BUILDER_DATABASE_URL),
    pool_pre_ping=True,
)

ResumeBuilderSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=resume_builder_engine,
)


class ResumeBuilderBase(DeclarativeBase):
    pass


def get_resume_builder_db() -> Generator[Session, None, None]:
    db = ResumeBuilderSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_resume_builder_database() -> bool:
    with resume_builder_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
