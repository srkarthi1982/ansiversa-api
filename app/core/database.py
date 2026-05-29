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
        raise RuntimeError("TURSO_AUTH_TOKEN is required for libSQL/Turso database URLs.")

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    return {}


parent_engine = create_engine(
    _build_database_url(settings.PARENT_DATABASE_URL),
    connect_args=_build_connect_args(settings.PARENT_DATABASE_URL),
    pool_pre_ping=True,
)

ParentSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=parent_engine,
)


class ParentBase(DeclarativeBase):
    pass


def get_parent_db() -> Generator[Session, None, None]:
    db = ParentSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_parent_database() -> bool:
    with parent_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True