from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args,_build_database_url,_build_engine_kwargs
class WorkLogBase(DeclarativeBase):pass
engine=create_engine(_build_database_url(settings.WORK_LOG_TRACKER_DATABASE_URL),connect_args=_build_connect_args(settings.WORK_LOG_TRACKER_DATABASE_URL),pool_pre_ping=True,**_build_engine_kwargs(settings.WORK_LOG_TRACKER_DATABASE_URL));SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def get_db():
 d=SessionLocal()
 try:yield d
 finally:d.close()
