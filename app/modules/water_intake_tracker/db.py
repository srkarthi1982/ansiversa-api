from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_database_url, _build_engine_kwargs

class WaterIntakeBase(DeclarativeBase):
    pass

water_intake_engine = create_engine(
    _build_database_url(settings.WATER_INTAKE_TRACKER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.WATER_INTAKE_TRACKER_DATABASE_URL),
)
WaterIntakeSessionLocal = sessionmaker(bind=water_intake_engine, autoflush=False, autocommit=False)

def get_water_intake_db():
    db = WaterIntakeSessionLocal()
    try:
        yield db
    finally:
        db.close()
