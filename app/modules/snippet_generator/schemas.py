from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "paused", "archived"]
SnippetStatus = Literal["draft", "ready", "archived"]
HistoryEventType = Literal["created", "edited", "used", "copied", "versioned", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class SnippetProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    language: str | None = Field(default=None, max_length=120)
    status: ProjectStatus = "draft"
    goal: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetProjectUpdateRequest(SnippetProjectCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: ProjectStatus | None = None


class SnippetCategoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    name: str = Field(min_length=1, max_length=140)
    color: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetCategoryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=140)
    color: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    category_id: int | None = Field(default=None, alias="categoryId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    language: str | None = Field(default=None, max_length=120)
    status: SnippetStatus = "draft"
    description: str | None = Field(default=None, max_length=4000)
    snippet_text: str | None = Field(default=None, alias="snippetText", max_length=16000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)
    tags: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    language: str | None = Field(default=None, max_length=120)
    status: SnippetStatus | None = None
    description: str | None = Field(default=None, max_length=4000)
    snippet_text: str | None = Field(default=None, alias="snippetText", max_length=16000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)
    tags: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    snippet_id: int = Field(alias="snippetId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    description: str | None = Field(default=None, max_length=5000)
    revision_notes: str | None = Field(default=None, alias="revisionNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetHistoryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    description: str | None = Field(default=None, max_length=5000)
    revision_notes: str | None = Field(default=None, alias="revisionNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SnippetProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    language: str | None
    status: ProjectStatus
    goal_preview: str | None = Field(serialization_alias="goalPreview")
    snippet_count: int = Field(serialization_alias="snippetCount")
    category_count: int = Field(serialization_alias="categoryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SnippetProjectDetailResponse(SnippetProjectSummaryResponse):
    goal: str | None
    notes: str | None


class SnippetCategorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    name: str
    color: str | None
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    snippet_count: int = Field(serialization_alias="snippetCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SnippetCategoryDetailResponse(SnippetCategorySummaryResponse):
    description: str | None


class SnippetSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    category_id: int | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    title: str
    language: str | None
    status: SnippetStatus
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    snippet_preview: str | None = Field(serialization_alias="snippetPreview")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SnippetDetailResponse(SnippetSummaryResponse):
    description: str | None
    snippet_text: str | None = Field(serialization_alias="snippetText")
    usage_notes: str | None = Field(serialization_alias="usageNotes")
    tags: str | None


class SnippetHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    snippet_id: int = Field(serialization_alias="snippetId")
    snippet_title: str = Field(serialization_alias="snippetTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SnippetHistoryDetailResponse(SnippetHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class SnippetGeneratorDashboardResponse(BaseModel):
    projects: list[SnippetProjectSummaryResponse]
    snippets: list[SnippetSummaryResponse]
    categories: list[SnippetCategorySummaryResponse]
    history: list[SnippetHistorySummaryResponse]
    project_count: int = Field(serialization_alias="projectCount")
    snippet_count: int = Field(serialization_alias="snippetCount")
    category_count: int = Field(serialization_alias="categoryCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_snippet_count: int = Field(serialization_alias="readySnippetCount")

    model_config = ConfigDict(from_attributes=True)
