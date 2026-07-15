from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.vaccination_tracker.models import VaccinationProfile, VaccinationRecord, VaccineType

def add(db: Session, item):
    db.add(item)
    return item

def delete_record(db: Session, item) -> None:
    db.delete(item)

def list_profiles(db: Session, owner_id: str) -> list[VaccinationProfile]:
    return list(db.scalars(select(VaccinationProfile).where(VaccinationProfile.owner_id == owner_id).order_by(VaccinationProfile.archived, VaccinationProfile.full_name)))

def get_profile(db: Session, item_id: str) -> VaccinationProfile | None:
    return db.get(VaccinationProfile, item_id)

def list_vaccine_types(db: Session, owner_id: str) -> list[VaccineType]:
    return list(db.scalars(select(VaccineType).where(VaccineType.owner_id == owner_id).order_by(VaccineType.sort_order, VaccineType.name)))

def get_vaccine_type(db: Session, item_id: str) -> VaccineType | None:
    return db.get(VaccineType, item_id)

def list_records(db: Session, owner_id: str) -> list[VaccinationRecord]:
    result = db.execute(select(VaccinationRecord).options(joinedload(VaccinationRecord.profile), joinedload(VaccinationRecord.vaccine_type)).where(VaccinationRecord.owner_id == owner_id).order_by(VaccinationRecord.created_at.desc()))
    return list(result.unique().scalars())

def get_record(db: Session, item_id: str) -> VaccinationRecord | None:
    result = db.execute(select(VaccinationRecord).options(joinedload(VaccinationRecord.profile), joinedload(VaccinationRecord.vaccine_type)).where(VaccinationRecord.id == item_id))
    return result.unique().scalars().first()

def record_counts_by_profile(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(VaccinationRecord.profile_id, func.count()).where(VaccinationRecord.owner_id == owner_id).group_by(VaccinationRecord.profile_id))
    return {row[0]: row[1] for row in rows}

def record_counts_by_vaccine_type(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(VaccinationRecord.vaccine_type_id, func.count()).where(VaccinationRecord.owner_id == owner_id, VaccinationRecord.vaccine_type_id.is_not(None)).group_by(VaccinationRecord.vaccine_type_id))
    return {row[0]: row[1] for row in rows}

def count_records_for_profile(db: Session, owner_id: str, profile_id: str) -> int:
    return db.scalar(select(func.count()).select_from(VaccinationRecord).where(VaccinationRecord.owner_id == owner_id, VaccinationRecord.profile_id == profile_id)) or 0

def count_records_for_vaccine_type(db: Session, owner_id: str, vaccine_type_id: str) -> int:
    return db.scalar(select(func.count()).select_from(VaccinationRecord).where(VaccinationRecord.owner_id == owner_id, VaccinationRecord.vaccine_type_id == vaccine_type_id)) or 0
