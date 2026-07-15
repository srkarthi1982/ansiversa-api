from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.database import _build_database_url, _build_engine_kwargs


class FuelExpenseBase(DeclarativeBase):
    pass


fuel_expense_engine = create_engine(
    _build_database_url(settings.FUEL_EXPENSE_TRACKER_DATABASE_URL),
    pool_pre_ping=True,
    **_build_engine_kwargs(settings.FUEL_EXPENSE_TRACKER_DATABASE_URL),
)
FuelExpenseSessionLocal = sessionmaker(bind=fuel_expense_engine, autoflush=False, autocommit=False)


def get_fuel_expense_db():
    db = FuelExpenseSessionLocal()
    try:
        yield db
    finally:
        db.close()
