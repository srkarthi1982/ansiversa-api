from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_connect_args, _build_database_url, _build_engine_kwargs


class FirstAidGuideBase(DeclarativeBase):
    pass


first_aid_guide_engine = create_engine(
    _build_database_url(settings.FIRST_AID_GUIDE_DATABASE_URL),
    connect_args=_build_connect_args(settings.FIRST_AID_GUIDE_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.FIRST_AID_GUIDE_DATABASE_URL),
)
FirstAidGuideSessionLocal = sessionmaker(bind=first_aid_guide_engine, autoflush=False, autocommit=False)


def get_first_aid_guide_db():
    db = FirstAidGuideSessionLocal()
    try:
        yield db
    finally:
        db.close()
