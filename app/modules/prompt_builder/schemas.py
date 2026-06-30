from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "paused", "archived"]
PromptStatus = Literal["draft", "testing", "ready", "archived"]
HistoryEventType = Literal["created", "edited", "tested", "used", "versioned", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class PromptProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    status: ProjectStatus = "draft"
    goal: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PromptProjectUpdateRequest(PromptProjectCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: ProjectStatus | None = None


class PromptCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    model_target: str | None = Field(default=None, alias="modelTarget", max_length=120)
    status: PromptStatus = "draft"
    prompt_text: str | None = Field(default=None, alias="promptText", max_length=12000)
    context_text: str | None = Field(default=None, alias="contextText", max_length=8000)
    output_format: str | None = Field(default=None, alias="outputFormat", max_length=4000)
    tags: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PromptUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    model_target: str | None = Field(default=None, alias="modelTarget", max_length=120)
    status: PromptStatus | None = None
    prompt_text: str | None = Field(default=None, alias="promptText", max_length=12000)
    context_text: str | None = Field(default=None, alias="contextText", max_length=8000)
    output_format: str | None = Field(default=None, alias="outputFormat", max_length=4000)
    tags: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PromptTemplateCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    template_text: str | None = Field(default=None, alias="templateText", max_length=12000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PromptTemplateUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    template_text: str | None = Field(default=None, alias="templateText", max_length=12000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PromptHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    prompt_id: int = Field(alias="promptId", gt=0)
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


class PromptHistoryUpdateRequest(BaseModel):
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


class PromptProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    category: str | None
    status: ProjectStatus
    goal_preview: str | None = Field(serialization_alias="goalPreview")
    prompt_count: int = Field(serialization_alias="promptCount")
    template_count: int = Field(serialization_alias="templateCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PromptProjectDetailResponse(PromptProjectSummaryResponse):
    goal: str | None
    notes: str | None


class PromptSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    category: str | None
    model_target: str | None = Field(serialization_alias="modelTarget")
    status: PromptStatus
    prompt_preview: str | None = Field(serialization_alias="promptPreview")
    context_preview: str | None = Field(serialization_alias="contextPreview")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PromptDetailResponse(PromptSummaryResponse):
    prompt_text: str | None = Field(serialization_alias="promptText")
    context_text: str | None = Field(serialization_alias="contextText")
    output_format: str | None = Field(serialization_alias="outputFormat")
    tags: str | None


class PromptTemplateSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    category: str | None
    template_preview: str | None = Field(serialization_alias="templatePreview")
    usage_notes_preview: str | None = Field(serialization_alias="usageNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PromptTemplateDetailResponse(PromptTemplateSummaryResponse):
    template_text: str | None = Field(serialization_alias="templateText")
    usage_notes: str | None = Field(serialization_alias="usageNotes")


class PromptHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    prompt_id: int = Field(serialization_alias="promptId")
    prompt_title: str = Field(serialization_alias="promptTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PromptHistoryDetailResponse(PromptHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class PromptBuilderDashboardResponse(BaseModel):
    projects: list[PromptProjectSummaryResponse]
    prompts: list[PromptSummaryResponse]
    templates: list[PromptTemplateSummaryResponse]
    history: list[PromptHistorySummaryResponse]
    project_count: int = Field(serialization_alias="projectCount")
    prompt_count: int = Field(serialization_alias="promptCount")
    template_count: int = Field(serialization_alias="templateCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_prompt_count: int = Field(serialization_alias="readyPromptCount")

    model_config = ConfigDict(from_attributes=True)
