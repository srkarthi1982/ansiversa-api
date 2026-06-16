from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

LessonStatus = Literal["draft", "published"]
LessonSectionType = Literal["objective", "instruction", "activity", "assessment", "resource"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class LessonCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    subject: str = Field(min_length=1, max_length=140)
    audience: str = Field(min_length=1, max_length=140)
    duration_minutes: int = Field(validation_alias="durationMinutes", ge=1, le=480)
    objective: str = Field(min_length=1, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "audience", "objective", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LessonUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    subject: str | None = Field(default=None, min_length=1, max_length=140)
    audience: str | None = Field(default=None, min_length=1, max_length=140)
    duration_minutes: int | None = Field(
        default=None,
        validation_alias="durationMinutes",
        ge=1,
        le=480,
    )
    objective: str | None = Field(default=None, min_length=1, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "audience", "objective", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LessonResponse(BaseModel):
    id: str
    title: str
    subject: str
    audience: str
    duration_minutes: int = Field(serialization_alias="durationMinutes")
    objective: str
    status: LessonStatus
    section_count: int = Field(serialization_alias="sectionCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    published_at: datetime | None = Field(serialization_alias="publishedAt")

    model_config = ConfigDict(from_attributes=True)


class LessonListResponse(BaseModel):
    items: list[LessonResponse]


class LessonSectionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    section_type: LessonSectionType = Field(validation_alias="sectionType")
    content: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LessonSectionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    section_type: LessonSectionType | None = Field(
        default=None,
        validation_alias="sectionType",
    )
    content: str | None = Field(default=None, min_length=1, max_length=5000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LessonSectionResponse(BaseModel):
    id: str
    lesson_id: str = Field(serialization_alias="lessonId")
    title: str
    section_type: LessonSectionType = Field(serialization_alias="sectionType")
    content: str
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class LessonSectionListResponse(BaseModel):
    items: list[LessonSectionResponse]


class LessonDetailResponse(BaseModel):
    lesson: LessonResponse
    sections: list[LessonSectionResponse]


class LessonSectionReorderRequest(BaseModel):
    section_ids: list[str] = Field(validation_alias="sectionIds", min_length=1)

    model_config = ConfigDict(extra="forbid")
