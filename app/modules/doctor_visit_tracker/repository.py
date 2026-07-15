from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.doctor_visit_tracker.models import DoctorSpecialty, DoctorVisit

def add(db: Session, item):
    db.add(item); return item

def delete_record(db: Session, item) -> None:
    db.delete(item)

def list_specialties(db: Session, owner_id: str) -> list[DoctorSpecialty]:
    return list(db.scalars(select(DoctorSpecialty).where(DoctorSpecialty.owner_id == owner_id).order_by(DoctorSpecialty.sort_order, DoctorSpecialty.name)))

def get_specialty(db: Session, item_id: str) -> DoctorSpecialty | None:
    return db.get(DoctorSpecialty, item_id)

def list_visits(db: Session, owner_id: str) -> list[DoctorVisit]:
    result = db.execute(select(DoctorVisit).options(joinedload(DoctorVisit.specialty)).where(DoctorVisit.owner_id == owner_id).order_by(DoctorVisit.visit_date, DoctorVisit.visit_time, DoctorVisit.doctor_name))
    return list(result.unique().scalars())

def get_visit(db: Session, visit_id: str) -> DoctorVisit | None:
    result = db.execute(select(DoctorVisit).options(joinedload(DoctorVisit.specialty)).where(DoctorVisit.id == visit_id))
    return result.unique().scalars().first()

def count_visits_for_specialty(db: Session, owner_id: str, specialty_id: str) -> int:
    return db.scalar(select(func.count()).select_from(DoctorVisit).where(DoctorVisit.owner_id == owner_id, DoctorVisit.specialty_id == specialty_id)) or 0

def visit_counts_by_specialty(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(DoctorVisit.specialty_id, func.count()).where(DoctorVisit.owner_id == owner_id).group_by(DoctorVisit.specialty_id))
    return {row[0]: row[1] for row in rows}
