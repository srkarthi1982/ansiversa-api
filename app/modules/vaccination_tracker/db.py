from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs

class VaccinationBase(DeclarativeBase):
    pass

vaccination_engine = create_engine(
    _build_database_url(settings.VACCINATION_TRACKER_DATABASE_URL),
    connect_args=_build_connect_args(settings.VACCINATION_TRACKER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.VACCINATION_TRACKER_DATABASE_URL),
)
VaccinationSessionLocal = sessionmaker(bind=vaccination_engine, autoflush=False, autocommit=False)

def get_vaccination_db():
    db = VaccinationSessionLocal()
    try:
        yield db
    finally:
        db.close()
