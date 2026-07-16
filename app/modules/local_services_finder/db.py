from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args,_build_database_url,_build_engine_kwargs
class Base(DeclarativeBase):pass
url=settings.LOCAL_SERVICES_FINDER_DATABASE_URL
engine=create_engine(_build_database_url(url),connect_args=_build_connect_args(url),pool_pre_ping=True,**_build_engine_kwargs(url));SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def get_db():
 d=SessionLocal()
 try:yield d
 finally:d.close()
