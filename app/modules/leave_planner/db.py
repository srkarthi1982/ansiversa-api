from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs

class LeavePlannerBase(DeclarativeBase): pass

leave_planner_engine = create_engine(_build_database_url(settings.LEAVE_PLANNER_DATABASE_URL), connect_args=_build_connect_args(settings.LEAVE_PLANNER_DATABASE_URL), pool_pre_ping=True, **_build_engine_kwargs(settings.LEAVE_PLANNER_DATABASE_URL))
LeavePlannerSessionLocal = sessionmaker(bind=leave_planner_engine, autoflush=False, autocommit=False)

def get_leave_planner_db():
    db = LeavePlannerSessionLocal()
    try: yield db
    finally: db.close()
