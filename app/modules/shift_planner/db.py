from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs

class ShiftPlannerBase(DeclarativeBase): pass
shift_planner_engine=create_engine(_build_database_url(settings.SHIFT_PLANNER_DATABASE_URL),connect_args=_build_connect_args(settings.SHIFT_PLANNER_DATABASE_URL),pool_pre_ping=True,**_build_engine_kwargs(settings.SHIFT_PLANNER_DATABASE_URL))
ShiftPlannerSessionLocal=sessionmaker(bind=shift_planner_engine,autoflush=False,autocommit=False)
def get_shift_planner_db():
    db=ShiftPlannerSessionLocal()
    try: yield db
    finally: db.close()
