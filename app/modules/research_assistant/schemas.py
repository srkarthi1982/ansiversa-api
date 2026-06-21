from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ResearchStatus = Literal["collecting", "reviewing", "complete"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ResearchTopicCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    question: str | None = Field(default=None, max_length=2000)
    summary: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "question", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchTopicUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    question: str | None = Field(default=None, max_length=2000)
    summary: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "question", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchTopicStatusRequest(BaseModel):
    status: ResearchStatus

    model_config = ConfigDict(extra="forbid")


class ResearchTopicResponse(BaseModel):
    id: str
    title: str
    question: str | None
    summary: str | None
    status: ResearchStatus
    note_count: int = Field(serialization_alias="noteCount")
    reference_count: int = Field(serialization_alias="referenceCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResearchTopicListResponse(BaseModel):
    items: list[ResearchTopicResponse]


class ResearchNoteCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchNoteUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    body: str | None = Field(default=None, min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchNoteResponse(BaseModel):
    id: str
    topic_id: str = Field(serialization_alias="topicId")
    title: str
    body: str
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResearchReferenceCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    url: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "url", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchReferenceUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    url: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "url", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResearchReferenceResponse(BaseModel):
    id: str
    topic_id: str = Field(serialization_alias="topicId")
    title: str
    url: str | None
    notes: str | None
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResearchTopicDetailResponse(BaseModel):
    topic: ResearchTopicResponse
    notes: list[ResearchNoteResponse]
    references: list[ResearchReferenceResponse]
