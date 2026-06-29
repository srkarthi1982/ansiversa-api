from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["active", "archived"]
DocumentStatus = Literal["draft", "review", "approved", "signed", "archived"]
HistoryActionType = Literal["created", "updated", "generated", "reviewed", "approved", "signed", "exported"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ContractProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    counterparty_name: str | None = Field(default=None, alias="counterpartyName", max_length=180)
    contract_type: str = Field(default="service", alias="contractType", min_length=1, max_length=80)
    status: ProjectStatus = "active"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "counterparty_name", "contract_type", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    counterparty_name: str | None = Field(default=None, alias="counterpartyName", max_length=180)
    contract_type: str | None = Field(default=None, alias="contractType", min_length=1, max_length=80)
    status: ProjectStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "counterparty_name", "contract_type", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractDocumentCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    status: DocumentStatus = "draft"
    contract_type: str = Field(default="service", alias="contractType", min_length=1, max_length=80)
    effective_date: str | None = Field(default=None, alias="effectiveDate", max_length=40)
    expiry_date: str | None = Field(default=None, alias="expiryDate", max_length=40)
    jurisdiction: str | None = Field(default=None, max_length=120)
    parties: str | None = Field(default=None, max_length=5000)
    body: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "title",
        "contract_type",
        "effective_date",
        "expiry_date",
        "jurisdiction",
        "parties",
        "body",
        "notes",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractDocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: DocumentStatus | None = None
    contract_type: str | None = Field(default=None, alias="contractType", min_length=1, max_length=80)
    effective_date: str | None = Field(default=None, alias="effectiveDate", max_length=40)
    expiry_date: str | None = Field(default=None, alias="expiryDate", max_length=40)
    jurisdiction: str | None = Field(default=None, max_length=120)
    parties: str | None = Field(default=None, max_length=5000)
    body: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "title",
        "contract_type",
        "effective_date",
        "expiry_date",
        "jurisdiction",
        "parties",
        "body",
        "notes",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractClauseCreateRequest(BaseModel):
    document_id: int = Field(alias="documentId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    category: str = Field(default="general", min_length=1, max_length=80)
    body: str = Field(min_length=1, max_length=8000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "category", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractClauseUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    body: str | None = Field(default=None, min_length=1, max_length=8000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "category", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractHistoryCreateRequest(BaseModel):
    project_id: int | None = Field(default=None, alias="projectId", gt=0)
    document_id: int | None = Field(default=None, alias="documentId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    action_type: HistoryActionType = Field(default="updated", alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ContractProjectSummaryResponse(BaseModel):
    id: int
    title: str
    counterparty_name: str | None = Field(serialization_alias="counterpartyName")
    contract_type: str = Field(serialization_alias="contractType")
    status: ProjectStatus
    document_count: int = Field(serialization_alias="documentCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ContractProjectDetailResponse(ContractProjectSummaryResponse):
    notes: str | None


class ContractDocumentSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    status: DocumentStatus
    contract_type: str = Field(serialization_alias="contractType")
    effective_date: str | None = Field(serialization_alias="effectiveDate")
    expiry_date: str | None = Field(serialization_alias="expiryDate")
    jurisdiction: str | None
    clause_count: int = Field(serialization_alias="clauseCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ContractDocumentDetailResponse(ContractDocumentSummaryResponse):
    parties: str | None
    body: str | None
    notes: str | None


class ContractClauseSummaryResponse(BaseModel):
    id: int
    document_id: int = Field(serialization_alias="documentId")
    document_title: str = Field(serialization_alias="documentTitle")
    title: str
    category: str
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ContractClauseDetailResponse(ContractClauseSummaryResponse):
    body: str


class ContractHistorySummaryResponse(BaseModel):
    id: int
    project_id: int | None = Field(serialization_alias="projectId")
    project_title: str | None = Field(serialization_alias="projectTitle")
    document_id: int | None = Field(serialization_alias="documentId")
    document_title: str | None = Field(serialization_alias="documentTitle")
    title: str
    action_type: HistoryActionType = Field(serialization_alias="actionType")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ContractDashboardResponse(BaseModel):
    projects: list[ContractProjectSummaryResponse]
    documents: list[ContractDocumentSummaryResponse]
    clauses: list[ContractClauseSummaryResponse]
    history: list[ContractHistorySummaryResponse]
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    draft_document_count: int = Field(serialization_alias="draftDocumentCount")
    review_document_count: int = Field(serialization_alias="reviewDocumentCount")
    signed_document_count: int = Field(serialization_alias="signedDocumentCount")

    model_config = ConfigDict(from_attributes=True)
