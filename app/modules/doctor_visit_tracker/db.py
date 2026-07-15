from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

class DoctorVisitBase(DeclarativeBase):
    pass

def _build_database_url(database_url: str) -> str:
    if database_url.startswith('libsql://'):
        return f'sqlite+{database_url}?secure=true'
    return database_url

def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith('libsql://') and not settings.TURSO_AUTH_TOKEN:
        raise RuntimeError('TURSO_AUTH_TOKEN is required for libSQL database connections.')
    if database_url.startswith('libsql://'):
        return {'auth_token': settings.TURSO_AUTH_TOKEN}
    if database_url.startswith('sqlite'):
        return {'check_same_thread': False}
    return {}

def _build_engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith('libsql://'):
        return {'poolclass': QueuePool, 'pool_size': 5, 'max_overflow': 10}
    return {}

doctor_visit_engine = create_engine(_build_database_url(settings.DOCTOR_VISIT_TRACKER_DATABASE_URL), connect_args=_build_connect_args(settings.DOCTOR_VISIT_TRACKER_DATABASE_URL), **_build_engine_kwargs(settings.DOCTOR_VISIT_TRACKER_DATABASE_URL))
DoctorVisitSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_visit_engine)

def get_doctor_visit_db() -> Generator[Session, None, None]:
    db = DoctorVisitSessionLocal()
    try:
        yield db
    finally:
        db.close()
