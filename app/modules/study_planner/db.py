from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_study_planner_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_study_planner_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Study Planner libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


study_planner_engine = create_engine(
    _build_study_planner_database_url(settings.STUDY_PLANNER_DATABASE_URL),
    connect_args=_build_study_planner_connect_args(
        settings.STUDY_PLANNER_DATABASE_URL
    ),
    pool_pre_ping=True,
)

StudyPlannerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=study_planner_engine,
)


class StudyPlannerBase(DeclarativeBase):
    pass


def get_study_planner_db() -> Generator[Session, None, None]:
    db = StudyPlannerSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_study_planner_database() -> bool:
    with study_planner_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
