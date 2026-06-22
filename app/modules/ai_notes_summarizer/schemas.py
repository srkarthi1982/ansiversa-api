from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

JobStatus = Literal["complete", "failed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class NotesDocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    source_text: str = Field(
        alias="sourceText",
        min_length=20,
        max_length=20000,
    )

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "source_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class NotesDocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    source_text: str | None = Field(
        default=None,
        alias="sourceText",
        min_length=20,
        max_length=20000,
    )

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "source_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class NotesDocumentResponse(BaseModel):
    id: int
    title: str
    source_text: str = Field(serialization_alias="sourceText")
    summary_count: int = Field(serialization_alias="summaryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class NotesDocumentListResponse(BaseModel):
    items: list[NotesDocumentResponse]


class NoteSummaryResponse(BaseModel):
    id: int
    document_id: int = Field(serialization_alias="documentId")
    document_title: str = Field(serialization_alias="documentTitle")
    summary: str
    key_points: list[str] = Field(serialization_alias="keyPoints")
    action_items: list[str] = Field(serialization_alias="actionItems")
    word_count: int = Field(serialization_alias="wordCount")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class NoteSummaryListResponse(BaseModel):
    items: list[NoteSummaryResponse]


class SummaryJobResponse(BaseModel):
    id: int
    document_id: int | None = Field(serialization_alias="documentId")
    status: JobStatus
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class NotesDocumentDetailResponse(BaseModel):
    document: NotesDocumentResponse
    summaries: list[NoteSummaryResponse]
    jobs: list[SummaryJobResponse]
