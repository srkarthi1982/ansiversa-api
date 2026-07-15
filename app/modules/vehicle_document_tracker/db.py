from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs


class VehicleDocumentTrackerBase(DeclarativeBase):
    pass


vehicle_document_tracker_engine = create_engine(
    _build_database_url(settings.VEHICLE_DOCUMENT_TRACKER_DATABASE_URL),
    connect_args=_build_connect_args(settings.VEHICLE_DOCUMENT_TRACKER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.VEHICLE_DOCUMENT_TRACKER_DATABASE_URL),
)
VehicleDocumentTrackerSessionLocal = sessionmaker(bind=vehicle_document_tracker_engine, autoflush=False, autocommit=False)


def get_vehicle_document_tracker_db():
    db = VehicleDocumentTrackerSessionLocal()
    try:
        yield db
    finally:
        db.close()
