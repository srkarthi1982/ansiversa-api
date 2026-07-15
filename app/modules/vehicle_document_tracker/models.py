from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.vehicle_document_tracker.db import VehicleDocumentTrackerBase


def _uuid() -> str:
    return str(uuid4())


class VehicleDocumentVehicle(VehicleDocumentTrackerBase):
    __tablename__ = "VehicleDocumentsVehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_name: Mapped[str] = mapped_column("vehicleName", String(160), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_nickname: Mapped[str | None] = mapped_column("registrationNickname", String(120), nullable=True)
    registration_number: Mapped[str | None] = mapped_column("registrationNumber", String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    documents: Mapped[list["VehicleDocument"]] = relationship(back_populates="vehicle")


class VehicleDocumentType(VehicleDocumentTrackerBase):
    __tablename__ = "VehicleDocumentTypes"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_vehicle_document_types_user_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False, default="system")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    documents: Mapped[list["VehicleDocument"]] = relationship(back_populates="document_type")


class VehicleDocument(VehicleDocumentTrackerBase):
    __tablename__ = "VehicleDocuments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    vehicle_id: Mapped[str] = mapped_column("vehicleId", String(36), ForeignKey("VehicleDocumentsVehicles.id"), index=True, nullable=False)
    document_type_id: Mapped[str] = mapped_column("documentTypeId", String(36), ForeignKey("VehicleDocumentTypes.id"), index=True, nullable=False)
    document_number: Mapped[str | None] = mapped_column("documentNumber", String(160), nullable=True)
    issue_date: Mapped[date | None] = mapped_column("issueDate", Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column("expiryDate", Date, index=True, nullable=True)
    reminder_date: Mapped[date | None] = mapped_column("reminderDate", Date, index=True, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column("issuingAuthority", String(180), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    vehicle: Mapped[VehicleDocumentVehicle] = relationship(back_populates="documents")
    document_type: Mapped[VehicleDocumentType] = relationship(back_populates="documents")
