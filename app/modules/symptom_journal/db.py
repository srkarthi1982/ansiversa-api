from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_database_url, _build_engine_kwargs


class SymptomJournalBase(DeclarativeBase):
    pass


symptom_journal_engine = create_engine(
    _build_database_url(settings.SYMPTOM_JOURNAL_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.SYMPTOM_JOURNAL_DATABASE_URL),
)
SymptomJournalSessionLocal = sessionmaker(bind=symptom_journal_engine, autoflush=False, autocommit=False)


def get_symptom_journal_db():
    db = SymptomJournalSessionLocal()
    try:
        yield db
    finally:
        db.close()
