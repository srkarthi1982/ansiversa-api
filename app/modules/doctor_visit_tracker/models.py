from datetime import date, datetime, time
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship
from app.modules.doctor_visit_tracker.db import DoctorVisitBase

def _uuid() -> str:
    return str(uuid4())

class DoctorSpecialty(DoctorVisitBase):
    __tablename__ = 'DoctorSpecialties'
    __table_args__ = (UniqueConstraint('userId', 'name', name='uq_doctor_specialties_owner_name'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column('sortOrder', Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column('isSystem', Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    visits: Mapped[list['DoctorVisit']] = orm_relationship(back_populates='specialty')

class DoctorVisit(DoctorVisitBase):
    __tablename__ = 'DoctorVisits'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    specialty_id: Mapped[str] = mapped_column('specialtyId', String(36), ForeignKey('DoctorSpecialties.id'), index=True, nullable=False)
    visit_title: Mapped[str] = mapped_column('visitTitle', String(180), nullable=False)
    doctor_name: Mapped[str] = mapped_column('doctorName', String(180), nullable=False)
    clinic_name: Mapped[str | None] = mapped_column('clinicName', String(180), nullable=True)
    visit_date: Mapped[date] = mapped_column('visitDate', Date, index=True, nullable=False)
    visit_time: Mapped[time | None] = mapped_column('visitTime', Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default='scheduled')
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis_notes: Mapped[str | None] = mapped_column('diagnosisNotes', Text, nullable=True)
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column('followUpDate', Date, index=True, nullable=True)
    visit_cost: Mapped[float | None] = mapped_column('visitCost', Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    insurance_notes: Mapped[str | None] = mapped_column('insuranceNotes', Text, nullable=True)
    personal_notes: Mapped[str | None] = mapped_column('personalNotes', Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    specialty: Mapped[DoctorSpecialty] = orm_relationship(back_populates='visits')
