from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ScanStatus = Literal["scanning", "organized", "extracting", "reviewed"]
PageStatus = Literal["captured", "organized", "extracted"]
NoteType = Literal["keyPoints", "definition", "question", "summary"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class TextbookScanCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    subject: str = Field(min_length=1, max_length=120)
    source: str | None = Field(default=None, max_length=180)
    goal: str = Field(min_length=1, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "source", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TextbookScanUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    subject: str | None = Field(default=None, min_length=1, max_length=120)
    source: str | None = Field(default=None, max_length=180)
    goal: str | None = Field(default=None, min_length=1, max_length=2000)
    status: ScanStatus | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "source", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TextbookPageCreateRequest(BaseModel):
    scan_id: int = Field(alias="scanId", gt=0)
    page_number: int = Field(alias="pageNumber", gt=0, le=10000)
    title: str | None = Field(default=None, max_length=180)
    page_text: str = Field(alias="pageText", min_length=1, max_length=12000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "page_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TextbookPageUpdateRequest(BaseModel):
    page_number: int | None = Field(default=None, alias="pageNumber", gt=0, le=10000)
    title: str | None = Field(default=None, max_length=180)
    page_text: str | None = Field(default=None, alias="pageText", min_length=1, max_length=12000)
    status: PageStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "page_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExtractedNoteCreateRequest(BaseModel):
    scan_id: int = Field(alias="scanId", gt=0)
    page_id: int = Field(alias="pageId", gt=0)
    heading: str = Field(min_length=1, max_length=180)
    key_points: str = Field(alias="keyPoints", min_length=1, max_length=4000)
    summary: str | None = Field(default=None, max_length=2000)
    note_type: NoteType = Field(default="keyPoints", alias="noteType")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("heading", "key_points", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TextbookScanResponse(BaseModel):
    id: int
    title: str
    subject: str
    source: str | None
    goal: str
    status: ScanStatus
    page_count: int = Field(serialization_alias="pageCount")
    extracted_note_count: int = Field(serialization_alias="extractedNoteCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TextbookScanListResponse(BaseModel):
    items: list[TextbookScanResponse]


class TextbookPageResponse(BaseModel):
    id: int
    scan_id: int = Field(serialization_alias="scanId")
    scan_title: str = Field(serialization_alias="scanTitle")
    page_number: int = Field(serialization_alias="pageNumber")
    title: str | None
    page_text: str = Field(serialization_alias="pageText")
    status: PageStatus
    extracted_note_count: int = Field(serialization_alias="extractedNoteCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TextbookPageListItemResponse(BaseModel):
    id: int
    scan_id: int = Field(serialization_alias="scanId")
    scan_title: str = Field(serialization_alias="scanTitle")
    page_number: int = Field(serialization_alias="pageNumber")
    title: str | None
    status: PageStatus
    extracted_note_count: int = Field(serialization_alias="extractedNoteCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TextbookPageListResponse(BaseModel):
    items: list[TextbookPageListItemResponse]


class ExtractedNoteResponse(BaseModel):
    id: int
    scan_id: int = Field(serialization_alias="scanId")
    scan_title: str = Field(serialization_alias="scanTitle")
    page_id: int = Field(serialization_alias="pageId")
    page_number: int = Field(serialization_alias="pageNumber")
    heading: str
    key_points: str = Field(serialization_alias="keyPoints")
    summary: str | None
    note_type: NoteType = Field(serialization_alias="noteType")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class ExtractedNoteListResponse(BaseModel):
    items: list[ExtractedNoteResponse]


class SmartTextbookScannerReviewResponse(BaseModel):
    active_scan_count: int = Field(serialization_alias="activeScanCount")
    reviewed_scan_count: int = Field(serialization_alias="reviewedScanCount")
    total_page_count: int = Field(serialization_alias="totalPageCount")
    extracted_page_count: int = Field(serialization_alias="extractedPageCount")
    total_note_count: int = Field(serialization_alias="totalNoteCount")
    extraction_rate: int = Field(serialization_alias="extractionRate")
    recent_notes: list[ExtractedNoteResponse] = Field(serialization_alias="recentNotes")


class SmartTextbookScannerDashboardResponse(BaseModel):
    scans: list[TextbookScanResponse]
    pages: list[TextbookPageListItemResponse]
    notes: list[ExtractedNoteResponse]
    review: SmartTextbookScannerReviewResponse
