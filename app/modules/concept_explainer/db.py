from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_concept_explainer_database_url(database_url: str) -> str:
    if database_url.startswith("libsql://"):
        return f"sqlite+{database_url}?secure=true"

    return database_url


def _build_concept_explainer_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("libsql://") and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is required for Concept Explainer libSQL/Turso database URLs."
        )

    if database_url.startswith("libsql://"):
        return {"auth_token": settings.TURSO_AUTH_TOKEN}

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


concept_explainer_engine = create_engine(
    _build_concept_explainer_database_url(settings.CONCEPT_EXPLAINER_DATABASE_URL),
    connect_args=_build_concept_explainer_connect_args(
        settings.CONCEPT_EXPLAINER_DATABASE_URL
    ),
    pool_pre_ping=True,
)

ConceptExplainerSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=concept_explainer_engine,
)


class ConceptExplainerBase(DeclarativeBase):
    pass


def get_concept_explainer_db() -> Generator[Session, None, None]:
    db = ConceptExplainerSessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_concept_explainer_database() -> bool:
    with concept_explainer_engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
