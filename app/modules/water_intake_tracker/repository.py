from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.water_intake_tracker.models import WaterEntry, WaterGoal

def add(db: Session, item):
    db.add(item)
    return item

def delete_record(db: Session, item) -> None:
    db.delete(item)

def get_goal(db: Session, owner_id: str) -> WaterGoal | None:
    return db.scalars(select(WaterGoal).where(WaterGoal.owner_id == owner_id)).first()

def get_entry(db: Session, entry_id: str) -> WaterEntry | None:
    return db.get(WaterEntry, entry_id)

def list_entries(db: Session, owner_id: str) -> list[WaterEntry]:
    return list(db.scalars(select(WaterEntry).where(WaterEntry.owner_id == owner_id).order_by(WaterEntry.entry_date.desc(), WaterEntry.entry_time.desc(), WaterEntry.created_at.desc())))

def count_entries(db: Session, owner_id: str) -> int:
    return db.scalar(select(func.count()).select_from(WaterEntry).where(WaterEntry.owner_id == owner_id)) or 0

def list_entries_between(db: Session, owner_id: str, start: date, end: date) -> list[WaterEntry]:
    return list(db.scalars(select(WaterEntry).where(WaterEntry.owner_id == owner_id, WaterEntry.entry_date >= start, WaterEntry.entry_date <= end).order_by(WaterEntry.entry_date, WaterEntry.entry_time)))
