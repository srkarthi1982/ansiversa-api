from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ConceptStatus = Literal["learning", "reviewed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ConceptCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    topic: str = Field(min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "topic", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    topic: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "topic", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptResponse(BaseModel):
    id: str
    title: str
    topic: str
    description: str | None
    status: ConceptStatus
    step_count: int = Field(serialization_alias="stepCount")
    check_count: int = Field(serialization_alias="checkCount")
    reviewed_at: datetime | None = Field(serialization_alias="reviewedAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ConceptListResponse(BaseModel):
    items: list[ConceptResponse]


class ConceptStepCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    explanation: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "explanation", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptStepUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    explanation: str | None = Field(default=None, min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "explanation", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptStepResponse(BaseModel):
    id: str
    concept_id: str = Field(serialization_alias="conceptId")
    title: str
    explanation: str
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ConceptCheckCreateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    expected_answer: str = Field(
        validation_alias="expectedAnswer",
        min_length=1,
        max_length=3000,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("question", "expected_answer", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptCheckUpdateRequest(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=2000)
    expected_answer: str | None = Field(
        default=None,
        validation_alias="expectedAnswer",
        min_length=1,
        max_length=3000,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("question", "expected_answer", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ConceptCheckResponse(BaseModel):
    id: str
    concept_id: str = Field(serialization_alias="conceptId")
    question: str
    expected_answer: str = Field(serialization_alias="expectedAnswer")
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ConceptDetailResponse(BaseModel):
    concept: ConceptResponse
    steps: list[ConceptStepResponse]
    checks: list[ConceptCheckResponse]
