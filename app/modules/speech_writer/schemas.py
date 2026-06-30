from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "paused", "archived"]
SpeechStatus = Literal["draft", "writing", "review", "ready", "delivered", "archived"]
SpeechTone = Literal["neutral", "warm", "professional", "inspirational", "formal", "humorous"]
HistoryEventType = Literal["created", "drafted", "edited", "reviewed", "delivered", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class SpeechProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    occasion: str | None = Field(default=None, max_length=120)
    event_date: str | None = Field(default=None, alias="eventDate", max_length=40)
    audience: str | None = Field(default=None, max_length=180)
    tone: SpeechTone | None = None
    status: ProjectStatus = "draft"
    purpose: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SpeechProjectUpdateRequest(SpeechProjectCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: ProjectStatus | None = None


class SpeechCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    speaker_name: str | None = Field(default=None, alias="speakerName", max_length=140)
    occasion: str | None = Field(default=None, max_length=120)
    duration_minutes: int | None = Field(default=None, alias="durationMinutes", ge=1, le=240)
    status: SpeechStatus = "draft"
    key_message: str | None = Field(default=None, alias="keyMessage", max_length=5000)
    speech_text: str | None = Field(default=None, alias="speechText", max_length=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SpeechUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    speaker_name: str | None = Field(default=None, alias="speakerName", max_length=140)
    occasion: str | None = Field(default=None, max_length=120)
    duration_minutes: int | None = Field(default=None, alias="durationMinutes", ge=1, le=240)
    status: SpeechStatus | None = None
    key_message: str | None = Field(default=None, alias="keyMessage", max_length=5000)
    speech_text: str | None = Field(default=None, alias="speechText", max_length=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SpeechTemplateCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    occasion: str | None = Field(default=None, max_length=120)
    tone: SpeechTone | None = None
    template_text: str | None = Field(default=None, alias="templateText", max_length=10000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SpeechTemplateUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    occasion: str | None = Field(default=None, max_length=120)
    tone: SpeechTone | None = None
    template_text: str | None = Field(default=None, alias="templateText", max_length=10000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SpeechHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    speech_id: int = Field(alias="speechId", gt=0)
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


class SpeechHistoryUpdateRequest(BaseModel):
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


class SpeechProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    occasion: str | None
    event_date: str | None = Field(serialization_alias="eventDate")
    audience: str | None
    tone: SpeechTone | None
    status: ProjectStatus
    purpose_preview: str | None = Field(serialization_alias="purposePreview")
    speech_count: int = Field(serialization_alias="speechCount")
    template_count: int = Field(serialization_alias="templateCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SpeechProjectDetailResponse(SpeechProjectSummaryResponse):
    purpose: str | None
    notes: str | None


class SpeechSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    speaker_name: str | None = Field(serialization_alias="speakerName")
    occasion: str | None
    duration_minutes: int | None = Field(serialization_alias="durationMinutes")
    status: SpeechStatus
    key_message_preview: str | None = Field(serialization_alias="keyMessagePreview")
    speech_preview: str | None = Field(serialization_alias="speechPreview")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SpeechDetailResponse(SpeechSummaryResponse):
    key_message: str | None = Field(serialization_alias="keyMessage")
    speech_text: str | None = Field(serialization_alias="speechText")


class SpeechTemplateSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    occasion: str | None
    tone: SpeechTone | None
    template_preview: str | None = Field(serialization_alias="templatePreview")
    usage_notes_preview: str | None = Field(serialization_alias="usageNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SpeechTemplateDetailResponse(SpeechTemplateSummaryResponse):
    template_text: str | None = Field(serialization_alias="templateText")
    usage_notes: str | None = Field(serialization_alias="usageNotes")


class SpeechHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    speech_id: int = Field(serialization_alias="speechId")
    speech_title: str = Field(serialization_alias="speechTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SpeechHistoryDetailResponse(SpeechHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class SpeechWriterDashboardResponse(BaseModel):
    projects: list[SpeechProjectSummaryResponse]
    speeches: list[SpeechSummaryResponse]
    templates: list[SpeechTemplateSummaryResponse]
    history: list[SpeechHistorySummaryResponse]
    project_count: int = Field(serialization_alias="projectCount")
    speech_count: int = Field(serialization_alias="speechCount")
    template_count: int = Field(serialization_alias="templateCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_speech_count: int = Field(serialization_alias="readySpeechCount")

    model_config = ConfigDict(from_attributes=True)
