from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship
from app.modules.vaccination_tracker.db import VaccinationBase

def _uuid() -> str:
    return str(uuid4())

class VaccinationProfile(VaccinationBase):
    __tablename__ = 'VaccinationProfiles'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column('fullName', String(180), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column('dateOfBirth', Date, nullable=True)
    relationship: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    records: Mapped[list['VaccinationRecord']] = orm_relationship(back_populates='profile')

class VaccineType(VaccinationBase):
    __tablename__ = 'VaccineTypes'
    __table_args__ = (UniqueConstraint('userId', 'name', name='uq_vaccine_types_owner_name'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    disease_or_purpose: Mapped[str | None] = mapped_column('diseaseOrPurpose', String(180), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column('sortOrder', Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column('isSystem', Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    records: Mapped[list['VaccinationRecord']] = orm_relationship(back_populates='vaccine_type')

class VaccinationRecord(VaccinationBase):
    __tablename__ = 'VaccinationRecords'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    profile_id: Mapped[str] = mapped_column('profileId', String(36), ForeignKey('VaccinationProfiles.id'), index=True, nullable=False)
    vaccine_type_id: Mapped[str | None] = mapped_column('vaccineTypeId', String(36), ForeignKey('VaccineTypes.id'), index=True, nullable=True)
    vaccine_name: Mapped[str] = mapped_column('vaccineName', String(180), nullable=False)
    disease_or_purpose: Mapped[str | None] = mapped_column('diseaseOrPurpose', String(180), nullable=True)
    dose_number: Mapped[int] = mapped_column('doseNumber', Integer, nullable=False, default=1)
    total_doses: Mapped[int | None] = mapped_column('totalDoses', Integer, nullable=True)
    vaccination_date: Mapped[date | None] = mapped_column('vaccinationDate', Date, nullable=True)
    next_due_date: Mapped[date | None] = mapped_column('nextDueDate', Date, index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default='scheduled')
    clinic_or_provider: Mapped[str | None] = mapped_column('clinicOrProvider', String(180), nullable=True)
    professional_name: Mapped[str | None] = mapped_column('professionalName', String(180), nullable=True)
    country_or_location: Mapped[str | None] = mapped_column('countryOrLocation', String(180), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(180), nullable=True)
    batch_number: Mapped[str | None] = mapped_column('batchNumber', String(120), nullable=True)
    certificate_reference: Mapped[str | None] = mapped_column('certificateReference', String(180), nullable=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    profile: Mapped[VaccinationProfile] = orm_relationship(back_populates='records')
    vaccine_type: Mapped[VaccineType | None] = orm_relationship(back_populates='records')
