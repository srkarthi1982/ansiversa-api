from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "paused", "archived"]
TranslationStatus = Literal["draft", "reviewing", "ready", "archived"]
HistoryEventType = Literal["created", "translated", "tone-fixed", "reviewed", "exported", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class TranslationProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    source_language: str | None = Field(default=None, alias="sourceLanguage", max_length=80)
    target_language: str | None = Field(default=None, alias="targetLanguage", max_length=80)
    tone: str | None = Field(default=None, max_length=80)
    status: ProjectStatus = "draft"
    goal: str | None = Field(default=None, max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TranslationProjectUpdateRequest(TranslationProjectCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: ProjectStatus | None = None


class TranslationCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    source_language: str | None = Field(default=None, alias="sourceLanguage", max_length=80)
    target_language: str | None = Field(default=None, alias="targetLanguage", max_length=80)
    tone: str | None = Field(default=None, max_length=80)
    status: TranslationStatus = "draft"
    source_text: str | None = Field(default=None, alias="sourceText", max_length=12000)
    translated_text: str | None = Field(default=None, alias="translatedText", max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TranslationUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    source_language: str | None = Field(default=None, alias="sourceLanguage", max_length=80)
    target_language: str | None = Field(default=None, alias="targetLanguage", max_length=80)
    tone: str | None = Field(default=None, max_length=80)
    status: TranslationStatus | None = None
    source_text: str | None = Field(default=None, alias="sourceText", max_length=12000)
    translated_text: str | None = Field(default=None, alias="translatedText", max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TranslationTemplateCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    source_language: str | None = Field(default=None, alias="sourceLanguage", max_length=80)
    target_language: str | None = Field(default=None, alias="targetLanguage", max_length=80)
    tone: str | None = Field(default=None, max_length=80)
    template_text: str | None = Field(default=None, alias="templateText", max_length=12000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TranslationTemplateUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    source_language: str | None = Field(default=None, alias="sourceLanguage", max_length=80)
    target_language: str | None = Field(default=None, alias="targetLanguage", max_length=80)
    tone: str | None = Field(default=None, max_length=80)
    template_text: str | None = Field(default=None, alias="templateText", max_length=12000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TranslationHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    translation_id: int = Field(alias="translationId", gt=0)
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


class TranslationHistoryUpdateRequest(BaseModel):
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


class TranslationProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    source_language: str | None = Field(serialization_alias="sourceLanguage")
    target_language: str | None = Field(serialization_alias="targetLanguage")
    tone: str | None
    status: ProjectStatus
    goal_preview: str | None = Field(serialization_alias="goalPreview")
    translation_count: int = Field(serialization_alias="translationCount")
    template_count: int = Field(serialization_alias="templateCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TranslationProjectDetailResponse(TranslationProjectSummaryResponse):
    goal: str | None
    notes: str | None


class TranslationSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    source_language: str | None = Field(serialization_alias="sourceLanguage")
    target_language: str | None = Field(serialization_alias="targetLanguage")
    tone: str | None
    status: TranslationStatus
    source_preview: str | None = Field(serialization_alias="sourcePreview")
    translated_preview: str | None = Field(serialization_alias="translatedPreview")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TranslationDetailResponse(TranslationSummaryResponse):
    source_text: str | None = Field(serialization_alias="sourceText")
    translated_text: str | None = Field(serialization_alias="translatedText")
    notes: str | None


class TranslationTemplateSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    source_language: str | None = Field(serialization_alias="sourceLanguage")
    target_language: str | None = Field(serialization_alias="targetLanguage")
    tone: str | None
    template_preview: str | None = Field(serialization_alias="templatePreview")
    usage_notes_preview: str | None = Field(serialization_alias="usageNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TranslationTemplateDetailResponse(TranslationTemplateSummaryResponse):
    template_text: str | None = Field(serialization_alias="templateText")
    usage_notes: str | None = Field(serialization_alias="usageNotes")


class TranslationHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    translation_id: int = Field(serialization_alias="translationId")
    translation_title: str = Field(serialization_alias="translationTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TranslationHistoryDetailResponse(TranslationHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class AiTranslatorAndToneFixerDashboardResponse(BaseModel):
    projects: list[TranslationProjectSummaryResponse]
    translations: list[TranslationSummaryResponse]
    templates: list[TranslationTemplateSummaryResponse]
    history: list[TranslationHistorySummaryResponse]
    project_count: int = Field(serialization_alias="projectCount")
    translation_count: int = Field(serialization_alias="translationCount")
    template_count: int = Field(serialization_alias="templateCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_translation_count: int = Field(serialization_alias="readyTranslationCount")

    model_config = ConfigDict(from_attributes=True)
