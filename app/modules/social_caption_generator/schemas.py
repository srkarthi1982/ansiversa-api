from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "paused", "archived"]
CaptionStatus = Literal["draft", "review", "approved", "published", "archived"]
CaptionTone = Literal["neutral", "friendly", "professional", "playful", "urgent", "inspirational"]
HistoryEventType = Literal["created", "generated", "edited", "approved", "published", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class CaptionProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    platform: str | None = Field(default=None, max_length=80)
    audience: str | None = Field(default=None, max_length=180)
    tone: CaptionTone | None = None
    status: ProjectStatus = "draft"
    campaign_brief: str | None = Field(default=None, alias="campaignBrief", max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CaptionProjectUpdateRequest(CaptionProjectCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: ProjectStatus | None = None


class SocialCaptionCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    platform: str | None = Field(default=None, max_length=80)
    status: CaptionStatus = "draft"
    caption_text: str | None = Field(default=None, alias="captionText", max_length=10000)
    hashtags: str | None = Field(default=None, max_length=4000)
    call_to_action: str | None = Field(default=None, alias="callToAction", max_length=240)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SocialCaptionUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    platform: str | None = Field(default=None, max_length=80)
    status: CaptionStatus | None = None
    caption_text: str | None = Field(default=None, alias="captionText", max_length=10000)
    hashtags: str | None = Field(default=None, max_length=4000)
    call_to_action: str | None = Field(default=None, alias="callToAction", max_length=240)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CaptionTemplateCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    platform: str | None = Field(default=None, max_length=80)
    tone: CaptionTone | None = None
    template_text: str | None = Field(default=None, alias="templateText", max_length=10000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CaptionTemplateUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    platform: str | None = Field(default=None, max_length=80)
    tone: CaptionTone | None = None
    template_text: str | None = Field(default=None, alias="templateText", max_length=10000)
    usage_notes: str | None = Field(default=None, alias="usageNotes", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CaptionHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    caption_id: int = Field(alias="captionId", gt=0)
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


class CaptionHistoryUpdateRequest(BaseModel):
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


class CaptionProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    platform: str | None
    audience: str | None
    tone: CaptionTone | None
    status: ProjectStatus
    campaign_brief_preview: str | None = Field(serialization_alias="campaignBriefPreview")
    caption_count: int = Field(serialization_alias="captionCount")
    template_count: int = Field(serialization_alias="templateCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CaptionProjectDetailResponse(CaptionProjectSummaryResponse):
    campaign_brief: str | None = Field(serialization_alias="campaignBrief")
    notes: str | None


class SocialCaptionSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    platform: str | None
    status: CaptionStatus
    caption_preview: str | None = Field(serialization_alias="captionPreview")
    hashtag_preview: str | None = Field(serialization_alias="hashtagPreview")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SocialCaptionDetailResponse(SocialCaptionSummaryResponse):
    caption_text: str | None = Field(serialization_alias="captionText")
    hashtags: str | None
    call_to_action: str | None = Field(serialization_alias="callToAction")


class CaptionTemplateSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    platform: str | None
    tone: CaptionTone | None
    template_preview: str | None = Field(serialization_alias="templatePreview")
    usage_notes_preview: str | None = Field(serialization_alias="usageNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CaptionTemplateDetailResponse(CaptionTemplateSummaryResponse):
    template_text: str | None = Field(serialization_alias="templateText")
    usage_notes: str | None = Field(serialization_alias="usageNotes")


class CaptionHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    caption_id: int = Field(serialization_alias="captionId")
    caption_title: str = Field(serialization_alias="captionTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CaptionHistoryDetailResponse(CaptionHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class SocialCaptionGeneratorDashboardResponse(BaseModel):
    projects: list[CaptionProjectSummaryResponse]
    captions: list[SocialCaptionSummaryResponse]
    templates: list[CaptionTemplateSummaryResponse]
    history: list[CaptionHistorySummaryResponse]
    project_count: int = Field(serialization_alias="projectCount")
    caption_count: int = Field(serialization_alias="captionCount")
    template_count: int = Field(serialization_alias="templateCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    approved_caption_count: int = Field(serialization_alias="approvedCaptionCount")

    model_config = ConfigDict(from_attributes=True)
