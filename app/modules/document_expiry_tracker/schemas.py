from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DocumentStatus = Literal["active", "expiringSoon", "expired", "archived"]
ExpiryPeriod = Literal["all", "upcoming7", "upcoming30", "upcoming90", "expired", "noExpiry"]
DocumentSort = Literal["expiryDate", "createdAt", "title"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _normalize_tag(value: str) -> str:
    return value.strip().lower()


class DocumentExpiryDocumentBase(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    document_type: str = Field(alias="documentType", min_length=1, max_length=80)
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=120)
    issuing_authority: str | None = Field(default=None, alias="issuingAuthority", max_length=180)
    country: str = Field(min_length=1, max_length=120)
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    expiry_date: str | None = Field(default=None, alias="expiryDate", max_length=40)
    renewal_reminder_days: int = Field(default=30, alias="renewalReminderDays", ge=0, le=3650)
    notes: str | None = Field(default=None, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=20)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: object) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            candidates = value.split(",")
        elif isinstance(value, list):
            candidates = [str(item) for item in value]
        else:
            return []
        tags: list[str] = []
        for candidate in candidates:
            tag = _normalize_tag(candidate)
            if tag and tag not in tags:
                tags.append(tag[:40])
        return tags[:20]

    @model_validator(mode="after")
    def validate_dates(self) -> "DocumentExpiryDocumentBase":
        _validate_iso_date(self.issue_date, "issueDate")
        _validate_iso_date(self.expiry_date, "expiryDate")
        if self.issue_date and self.expiry_date and self.issue_date > self.expiry_date:
            raise ValueError("issueDate must be before or equal to expiryDate.")
        return self


class DocumentExpiryDocumentCreateRequest(DocumentExpiryDocumentBase):
    pass


class DocumentExpiryDocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    document_type: str | None = Field(default=None, alias="documentType", min_length=1, max_length=80)
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=120)
    issuing_authority: str | None = Field(default=None, alias="issuingAuthority", max_length=180)
    country: str | None = Field(default=None, min_length=1, max_length=120)
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    expiry_date: str | None = Field(default=None, alias="expiryDate", max_length=40)
    renewal_reminder_days: int | None = Field(default=None, alias="renewalReminderDays", ge=0, le=3650)
    notes: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = Field(default=None, max_length=20)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: object) -> list[str] | None:
        if value is None:
            return None
        return DocumentExpiryDocumentBase.normalize_tags(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "DocumentExpiryDocumentUpdateRequest":
        _validate_iso_date(self.issue_date, "issueDate")
        _validate_iso_date(self.expiry_date, "expiryDate")
        if self.issue_date and self.expiry_date and self.issue_date > self.expiry_date:
            raise ValueError("issueDate must be before or equal to expiryDate.")
        return self


class DocumentExpiryRenewRequest(BaseModel):
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    expiry_date: str = Field(alias="expiryDate", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "DocumentExpiryRenewRequest":
        _validate_iso_date(self.issue_date, "issueDate")
        _validate_iso_date(self.expiry_date, "expiryDate")
        if self.issue_date and self.issue_date > self.expiry_date:
            raise ValueError("issueDate must be before or equal to expiryDate.")
        return self


class DocumentExpiryDocumentSummaryResponse(BaseModel):
    id: str
    title: str
    document_type: str = Field(serialization_alias="documentType")
    document_number: str | None = Field(serialization_alias="documentNumber")
    issuing_authority: str | None = Field(serialization_alias="issuingAuthority")
    country: str
    issue_date: str | None = Field(serialization_alias="issueDate")
    expiry_date: str | None = Field(serialization_alias="expiryDate")
    renewal_reminder_days: int = Field(serialization_alias="renewalReminderDays")
    status: DocumentStatus
    days_until_expiry: int | None = Field(serialization_alias="daysUntilExpiry")
    reminder_date: str | None = Field(serialization_alias="reminderDate")
    tags: list[str]
    archived: bool
    renewal_count: int = Field(serialization_alias="renewalCount")
    last_renewed_at: str | None = Field(serialization_alias="lastRenewedAt")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class DocumentExpiryDocumentDetailResponse(DocumentExpiryDocumentSummaryResponse):
    notes: str | None


class DocumentExpiryTypeCount(BaseModel):
    label: str
    count: int


class DocumentExpiryDashboardResponse(BaseModel):
    documents: list[DocumentExpiryDocumentSummaryResponse]
    total_documents: int = Field(serialization_alias="totalDocuments")
    active_count: int = Field(serialization_alias="activeCount")
    expiring_soon_count: int = Field(serialization_alias="expiringSoonCount")
    expired_count: int = Field(serialization_alias="expiredCount")
    archived_count: int = Field(serialization_alias="archivedCount")
    upcoming_7_count: int = Field(serialization_alias="upcoming7Count")
    upcoming_30_count: int = Field(serialization_alias="upcoming30Count")
    upcoming_90_count: int = Field(serialization_alias="upcoming90Count")
    no_expiry_count: int = Field(serialization_alias="noExpiryCount")
    type_distribution: list[DocumentExpiryTypeCount] = Field(serialization_alias="typeDistribution")
    country_distribution: list[DocumentExpiryTypeCount] = Field(serialization_alias="countryDistribution")
    upcoming_renewals: list[DocumentExpiryDocumentSummaryResponse] = Field(serialization_alias="upcomingRenewals")


def _validate_iso_date(value: str | None, field_name: str) -> None:
    if not value:
        return
    from datetime import date

    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc
