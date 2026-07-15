from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_database_url, _build_engine_kwargs


class DriverLogbookBase(DeclarativeBase):
    pass


driver_logbook_engine = create_engine(
    _build_database_url(settings.DRIVER_LOGBOOK_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.DRIVER_LOGBOOK_DATABASE_URL),
)
DriverLogbookSessionLocal = sessionmaker(bind=driver_logbook_engine, autoflush=False, autocommit=False)


def get_driver_logbook_db():
    db = DriverLogbookSessionLocal()
    try:
        yield db
    finally:
        db.close()
