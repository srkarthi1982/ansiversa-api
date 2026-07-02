from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "archived"]
JobStatus = Literal["queued", "running", "completed", "failed"]
GenerationType = Literal["blog", "video", "product", "social", "email"]
TitleStyle = Literal["clear", "playful", "professional", "bold", "seo"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class TitleProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    topic: str = Field(min_length=1, max_length=12000)
    audience: str | None = Field(default="General audience", max_length=160)
    language: str | None = Field(default="English", max_length=80)
    status: ProjectStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TitleProjectUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    topic: str | None = Field(default=None, min_length=1, max_length=12000)
    audience: str | None = Field(default=None, max_length=160)
    language: str | None = Field(default=None, max_length=80)
    status: ProjectStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TitleGenerateRequest(BaseModel):
    generation_type: GenerationType = Field(default="blog", alias="generationType")
    style: TitleStyle = "clear"
    keywords: str | None = Field(default=None, max_length=240)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, value: object) -> object:
        return _normalize_text(value)


class TitleProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    topic_preview: str = Field(serialization_alias="topicPreview")
    audience: str | None
    language: str | None
    status: ProjectStatus
    generated_count: int = Field(serialization_alias="generatedCount")
    latest_category: str | None = Field(serialization_alias="latestCategory")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TitleProjectDetailResponse(TitleProjectSummaryResponse):
    topic: str


class GeneratedTitleSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    generated_title: str = Field(serialization_alias="generatedTitle")
    category: str
    score: int
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class GeneratedTitleDetailResponse(GeneratedTitleSummaryResponse):
    topic: str
    audience: str | None
    language: str | None


class TitleJobResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    status: JobStatus
    provider: str
    generation_type: GenerationType = Field(serialization_alias="generationType")
    started_at: datetime = Field(serialization_alias="startedAt")
    completed_at: datetime | None = Field(serialization_alias="completedAt")

    model_config = ConfigDict(from_attributes=True)


class TitleGenerationResponse(BaseModel):
    project: TitleProjectDetailResponse
    generated_titles: list[GeneratedTitleSummaryResponse] = Field(serialization_alias="generatedTitles")
    job: TitleJobResponse


class CreativeTitleGeneratorDashboardResponse(BaseModel):
    projects: list[TitleProjectSummaryResponse]
    generated_titles: list[GeneratedTitleSummaryResponse] = Field(serialization_alias="generatedTitles")
    history: list[TitleJobResponse]
    project_count: int = Field(serialization_alias="projectCount")
    generated_count: int = Field(serialization_alias="generatedCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")

    model_config = ConfigDict(from_attributes=True)
