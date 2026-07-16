from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs


class MeetingSchedulerBase(DeclarativeBase):
    pass


meeting_scheduler_engine = create_engine(
    _build_database_url(settings.MEETING_SCHEDULER_DATABASE_URL),
    connect_args=_build_connect_args(settings.MEETING_SCHEDULER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.MEETING_SCHEDULER_DATABASE_URL),
)
MeetingSchedulerSessionLocal = sessionmaker(bind=meeting_scheduler_engine, autoflush=False, autocommit=False)


def get_meeting_scheduler_db():
    db = MeetingSchedulerSessionLocal()
    try:
        yield db
    finally:
        db.close()
