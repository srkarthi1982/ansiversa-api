from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.health_report_organizer.db import HealthReportOrganizerBase


def _uuid() -> str:
    return str(uuid4())


class HealthReportCategory(HealthReportOrganizerBase):
    __tablename__ = "HealthReportCategories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reports: Mapped[list["HealthReport"]] = relationship(back_populates="category")


class HealthReportFacility(HealthReportOrganizerBase):
    __tablename__ = "HealthReportFacilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    facility_type: Mapped[str] = mapped_column("facilityType", String(60), default="clinic", server_default="clinic", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    website: Mapped[str | None] = mapped_column(String(240), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reports: Mapped[list["HealthReport"]] = relationship(back_populates="facility")


class HealthReport(HealthReportOrganizerBase):
    __tablename__ = "HealthReports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str | None] = mapped_column("categoryId", String(36), ForeignKey("HealthReportCategories.id"), index=True, nullable=True)
    facility_id: Mapped[str | None] = mapped_column("facilityId", String(36), ForeignKey("HealthReportFacilities.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    report_type: Mapped[str] = mapped_column("reportType", String(80), default="lab", server_default="lab", nullable=False)
    report_date: Mapped[str] = mapped_column("reportDate", String(40), nullable=False)
    patient_name: Mapped[str | None] = mapped_column("patientName", String(140), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column("doctorName", String(140), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="new", server_default="new", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="routine", server_default="routine", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[HealthReportCategory | None] = relationship(back_populates="reports")
    facility: Mapped[HealthReportFacility | None] = relationship(back_populates="reports")
    attachments: Mapped[list["HealthReportAttachment"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    notes: Mapped[list["HealthReportNote"]] = relationship(back_populates="report", cascade="all, delete-orphan")


class HealthReportAttachment(HealthReportOrganizerBase):
    __tablename__ = "HealthReportAttachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    report_id: Mapped[str] = mapped_column("reportId", String(36), ForeignKey("HealthReports.id"), index=True, nullable=False)
    file_name: Mapped[str] = mapped_column("fileName", String(220), nullable=False)
    file_type: Mapped[str | None] = mapped_column("fileType", String(80), nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reference_url: Mapped[str | None] = mapped_column("referenceUrl", String(500), nullable=True)
    storage_location: Mapped[str | None] = mapped_column("storageLocation", String(220), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="available", server_default="available", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    report: Mapped[HealthReport] = relationship(back_populates="attachments")


class HealthReportNote(HealthReportOrganizerBase):
    __tablename__ = "HealthReportNotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    report_id: Mapped[str] = mapped_column("reportId", String(36), ForeignKey("HealthReports.id"), index=True, nullable=False)
    note_date: Mapped[str] = mapped_column("noteDate", String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(40), default="general", server_default="general", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    report: Mapped[HealthReport] = relationship(back_populates="notes")
