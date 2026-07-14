from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ExpiryFilter = Literal["all", "expiring", "expired", "noExpiry"]
DocumentSort = Literal["uploadedAt", "expiryDate", "title", "fileSize"]
ExpiryStatus = Literal["active", "expiringSoon", "expired", "noExpiry"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _normalize_tag(value: str) -> str:
    return value.strip().lower()


class VaultCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)


class VaultCategoryUpdateRequest(VaultCategoryCreateRequest):
    pass


class VaultCategoryResponse(BaseModel):
    id: str
    name: str
    document_count: int = Field(serialization_alias="documentCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VaultDocumentMetadataRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    document_type: str = Field(alias="documentType", min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    expiry_date: str | None = Field(default=None, alias="expiryDate", max_length=40)

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
    def validate_dates(self) -> "VaultDocumentMetadataRequest":
        _validate_iso_date(self.issue_date, "issueDate")
        _validate_iso_date(self.expiry_date, "expiryDate")
        if self.issue_date and self.expiry_date and self.issue_date > self.expiry_date:
            raise ValueError("issueDate must be before or equal to expiryDate.")
        return self


class VaultDocumentSummaryResponse(BaseModel):
    id: str
    title: str
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    document_type: str = Field(serialization_alias="documentType")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    tags: list[str]
    file_name: str = Field(serialization_alias="fileName")
    stored_file_name: str = Field(serialization_alias="storedFileName")
    mime_type: str = Field(serialization_alias="mimeType")
    file_size: int = Field(serialization_alias="fileSize")
    issue_date: str | None = Field(serialization_alias="issueDate")
    expiry_date: str | None = Field(serialization_alias="expiryDate")
    expiry_status: ExpiryStatus = Field(serialization_alias="expiryStatus")
    days_until_expiry: int | None = Field(serialization_alias="daysUntilExpiry")
    uploaded_at: datetime = Field(serialization_alias="uploadedAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VaultDocumentDetailResponse(VaultDocumentSummaryResponse):
    description: str | None


class VaultCountItem(BaseModel):
    label: str
    count: int


class VaultStorageItem(BaseModel):
    label: str
    bytes: int


class VaultDashboardResponse(BaseModel):
    documents: list[VaultDocumentSummaryResponse]
    categories: list[VaultCategoryResponse]
    total_documents: int = Field(serialization_alias="totalDocuments")
    total_storage_bytes: int = Field(serialization_alias="totalStorageBytes")
    expiring_documents_count: int = Field(serialization_alias="expiringDocumentsCount")
    expired_documents_count: int = Field(serialization_alias="expiredDocumentsCount")
    no_expiry_count: int = Field(serialization_alias="noExpiryCount")
    category_distribution: list[VaultCountItem] = Field(serialization_alias="categoryDistribution")
    type_distribution: list[VaultCountItem] = Field(serialization_alias="typeDistribution")
    storage_by_type: list[VaultStorageItem] = Field(serialization_alias="storageByType")
    recent_documents: list[VaultDocumentSummaryResponse] = Field(serialization_alias="recentDocuments")


def _validate_iso_date(value: str | None, field_name: str) -> None:
    if not value:
        return
    from datetime import date

    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc
