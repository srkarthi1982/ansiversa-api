from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ArchiveFilter = Literal["active", "archived", "all"]
DocumentSort = Literal["expiry", "reminder", "updated", "vehicle", "type", "status"]
DocumentStatus = Literal["active", "renewal_due", "expired", "renewed", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


class VehicleCreateRequest(BaseModel):
    vehicle_name: str = Field(alias="vehicleName", min_length=1, max_length=160)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    registration_nickname: str | None = Field(default=None, alias="registrationNickname", max_length=120)
    registration_number: str | None = Field(default=None, alias="registrationNumber", max_length=120)
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("vehicle_name", "manufacturer", "model", "registration_nickname", "registration_number", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleUpdateRequest(VehicleCreateRequest):
    pass


class DocumentTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class DocumentTypeUpdateRequest(DocumentTypeCreateRequest):
    pass


class DocumentCreateRequest(BaseModel):
    vehicle_id: str = Field(alias="vehicleId", min_length=1, max_length=36)
    document_type_id: str = Field(alias="documentTypeId", min_length=1, max_length=36)
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=160)
    issue_date: date | None = Field(default=None, alias="issueDate")
    expiry_date: date | None = Field(default=None, alias="expiryDate")
    reminder_date: date | None = Field(default=None, alias="reminderDate")
    issuing_authority: str | None = Field(default=None, alias="issuingAuthority", max_length=180)
    status: DocumentStatus = "active"
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("document_number", "issuing_authority", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.issue_date and self.expiry_date and self.expiry_date < self.issue_date:
            raise ValueError("Expiry date cannot be before issue date.")
        if self.issue_date and self.reminder_date and self.reminder_date < self.issue_date:
            raise ValueError("Reminder date cannot be before issue date.")
        if self.expiry_date and self.reminder_date and self.reminder_date > self.expiry_date:
            raise ValueError("Reminder date cannot be after expiry date.")
        if self.archived and self.status == "active":
            self.status = "archived"
        return self


class DocumentUpdateRequest(DocumentCreateRequest):
    pass


class VehicleResponse(BaseModel):
    id: str
    vehicle_name: str = Field(serialization_alias="vehicleName")
    manufacturer: str | None
    model: str | None
    year: int | None
    registration_nickname: str | None = Field(serialization_alias="registrationNickname")
    registration_number: str | None = Field(serialization_alias="registrationNumber")
    notes: str | None
    archived: bool
    document_count: int = Field(serialization_alias="documentCount")
    expired_count: int = Field(serialization_alias="expiredCount")
    upcoming_count: int = Field(serialization_alias="upcomingCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class DocumentTypeResponse(BaseModel):
    id: str
    name: str
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    document_count: int = Field(serialization_alias="documentCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class DocumentResponse(BaseModel):
    id: str
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    document_type_id: str = Field(serialization_alias="documentTypeId")
    document_type_name: str = Field(serialization_alias="documentTypeName")
    document_number: str | None = Field(serialization_alias="documentNumber")
    issue_date: date | None = Field(serialization_alias="issueDate")
    expiry_date: date | None = Field(serialization_alias="expiryDate")
    reminder_date: date | None = Field(serialization_alias="reminderDate")
    issuing_authority: str | None = Field(serialization_alias="issuingAuthority")
    status: str
    computed_status: str = Field(serialization_alias="computedStatus")
    days_until_expiry: int | None = Field(serialization_alias="daysUntilExpiry")
    archived: bool
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class CountItem(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    total_vehicles: int = Field(serialization_alias="totalVehicles")
    total_documents: int = Field(serialization_alias="totalDocuments")
    expiring_today: int = Field(serialization_alias="expiringToday")
    expiring_this_week: int = Field(serialization_alias="expiringThisWeek")
    expired_documents: int = Field(serialization_alias="expiredDocuments")
    upcoming_renewals: int = Field(serialization_alias="upcomingRenewals")


class InsightsResponse(DashboardResponse):
    vehicles: list[VehicleResponse]
    document_types: list[DocumentTypeResponse] = Field(serialization_alias="documentTypes")
    recent_documents: list[DocumentResponse] = Field(serialization_alias="recentDocuments")
    upcoming_documents: list[DocumentResponse] = Field(serialization_alias="upcomingDocuments")
    expired_document_items: list[DocumentResponse] = Field(serialization_alias="expiredDocumentItems")
    documents_by_type: list[CountItem] = Field(serialization_alias="documentsByType")
    documents_by_vehicle: list[CountItem] = Field(serialization_alias="documentsByVehicle")
    documents_by_status: list[CountItem] = Field(serialization_alias="documentsByStatus")
