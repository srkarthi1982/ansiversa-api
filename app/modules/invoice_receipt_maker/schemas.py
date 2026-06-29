from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["active", "archived"]
DocumentType = Literal["invoice", "receipt"]
DocumentStatus = Literal["draft", "sent", "paid", "void"]
HistoryActionType = Literal["created", "updated", "sent", "paid", "exported", "voided"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class InvoiceReceiptProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    business_name: str = Field(alias="businessName", min_length=1, max_length=180)
    client_name: str | None = Field(default=None, alias="clientName", max_length=180)
    currency: str = Field(default="AED", min_length=3, max_length=12)
    status: ProjectStatus = "active"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "business_name", "client_name", "currency", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    business_name: str | None = Field(default=None, alias="businessName", min_length=1, max_length=180)
    client_name: str | None = Field(default=None, alias="clientName", max_length=180)
    currency: str | None = Field(default=None, min_length=3, max_length=12)
    status: ProjectStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "business_name", "client_name", "currency", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptDocumentCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    document_type: DocumentType = Field(alias="documentType")
    document_number: str = Field(alias="documentNumber", min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=180)
    client_name: str = Field(alias="clientName", min_length=1, max_length=180)
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    paid_date: str | None = Field(default=None, alias="paidDate", max_length=40)
    status: DocumentStatus = "draft"
    notes: str | None = Field(default=None, max_length=5000)
    terms: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "document_number",
        "title",
        "client_name",
        "issue_date",
        "due_date",
        "paid_date",
        "notes",
        "terms",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptDocumentUpdateRequest(BaseModel):
    document_type: DocumentType | None = Field(default=None, alias="documentType")
    document_number: str | None = Field(default=None, alias="documentNumber", min_length=1, max_length=80)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    client_name: str | None = Field(default=None, alias="clientName", min_length=1, max_length=180)
    issue_date: str | None = Field(default=None, alias="issueDate", max_length=40)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    paid_date: str | None = Field(default=None, alias="paidDate", max_length=40)
    status: DocumentStatus | None = None
    notes: str | None = Field(default=None, max_length=5000)
    terms: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "document_number",
        "title",
        "client_name",
        "issue_date",
        "due_date",
        "paid_date",
        "notes",
        "terms",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptItemCreateRequest(BaseModel):
    document_id: int = Field(alias="documentId", gt=0)
    description: str = Field(min_length=1, max_length=3000)
    quantity: Decimal = Field(default=Decimal("1"), ge=0)
    unit_price: Decimal = Field(default=Decimal("0"), alias="unitPrice", ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), alias="taxRate", ge=0, le=100)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptItemUpdateRequest(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=3000)
    quantity: Decimal | None = Field(default=None, ge=0)
    unit_price: Decimal | None = Field(default=None, alias="unitPrice", ge=0)
    tax_rate: Decimal | None = Field(default=None, alias="taxRate", ge=0, le=100)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InvoiceReceiptHistoryCreateRequest(BaseModel):
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


class InvoiceReceiptProjectSummaryResponse(BaseModel):
    id: int
    title: str
    business_name: str = Field(serialization_alias="businessName")
    client_name: str | None = Field(serialization_alias="clientName")
    currency: str
    status: ProjectStatus
    document_count: int = Field(serialization_alias="documentCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InvoiceReceiptProjectDetailResponse(InvoiceReceiptProjectSummaryResponse):
    notes: str | None


class InvoiceReceiptDocumentSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    document_type: DocumentType = Field(serialization_alias="documentType")
    document_number: str = Field(serialization_alias="documentNumber")
    title: str
    client_name: str = Field(serialization_alias="clientName")
    issue_date: str | None = Field(serialization_alias="issueDate")
    due_date: str | None = Field(serialization_alias="dueDate")
    paid_date: str | None = Field(serialization_alias="paidDate")
    status: DocumentStatus
    subtotal: Decimal
    tax_total: Decimal = Field(serialization_alias="taxTotal")
    total: Decimal
    item_count: int = Field(serialization_alias="itemCount")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InvoiceReceiptDocumentDetailResponse(InvoiceReceiptDocumentSummaryResponse):
    notes: str | None
    terms: str | None


class InvoiceReceiptItemSummaryResponse(BaseModel):
    id: int
    document_id: int = Field(serialization_alias="documentId")
    document_title: str = Field(serialization_alias="documentTitle")
    description_preview: str = Field(serialization_alias="descriptionPreview")
    quantity: Decimal
    unit_price: Decimal = Field(serialization_alias="unitPrice")
    tax_rate: Decimal = Field(serialization_alias="taxRate")
    line_total: Decimal = Field(serialization_alias="lineTotal")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InvoiceReceiptItemDetailResponse(BaseModel):
    id: int
    document_id: int = Field(serialization_alias="documentId")
    document_title: str = Field(serialization_alias="documentTitle")
    description: str
    quantity: Decimal
    unit_price: Decimal = Field(serialization_alias="unitPrice")
    tax_rate: Decimal = Field(serialization_alias="taxRate")
    line_total: Decimal = Field(serialization_alias="lineTotal")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InvoiceReceiptHistorySummaryResponse(BaseModel):
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


class InvoiceReceiptDashboardResponse(BaseModel):
    projects: list[InvoiceReceiptProjectSummaryResponse]
    documents: list[InvoiceReceiptDocumentSummaryResponse]
    items: list[InvoiceReceiptItemSummaryResponse]
    history: list[InvoiceReceiptHistorySummaryResponse]
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    draft_document_count: int = Field(serialization_alias="draftDocumentCount")
    sent_document_count: int = Field(serialization_alias="sentDocumentCount")
    paid_document_count: int = Field(serialization_alias="paidDocumentCount")

    model_config = ConfigDict(from_attributes=True)
