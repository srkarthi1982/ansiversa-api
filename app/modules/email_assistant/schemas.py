from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EmailTone = Literal["professional", "friendly", "direct", "formal", "empathetic"]
EmailProjectStatus = Literal["draft", "active", "completed"]
EmailDraftStatus = Literal["draft", "ready", "sent", "archived"]
EmailTemplateCategory = Literal["general", "followUp", "proposal", "support", "announcement"]
EmailHistoryActionType = Literal["drafted", "edited", "sent", "archived", "reviewed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class EmailProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    audience: str | None = Field(default=None, max_length=180)
    goal: str | None = Field(default=None, max_length=3000)
    tone: EmailTone = "professional"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "audience", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    audience: str | None = Field(default=None, max_length=180)
    goal: str | None = Field(default=None, max_length=3000)
    tone: EmailTone | None = None
    status: EmailProjectStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "audience", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailDraftCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    template_id: int | None = Field(default=None, alias="templateId", gt=0)
    subject: str = Field(min_length=1, max_length=220)
    body: str = Field(min_length=1, max_length=12000)
    tone: EmailTone = "professional"
    status: EmailDraftStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("subject", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailDraftUpdateRequest(BaseModel):
    template_id: int | None = Field(default=None, alias="templateId", gt=0)
    subject: str | None = Field(default=None, min_length=1, max_length=220)
    body: str | None = Field(default=None, min_length=1, max_length=12000)
    tone: EmailTone | None = None
    status: EmailDraftStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("subject", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailTemplateCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category: EmailTemplateCategory = "general"
    subject_pattern: str | None = Field(default=None, alias="subjectPattern", max_length=220)
    body_pattern: str = Field(alias="bodyPattern", min_length=1, max_length=12000)
    tone: EmailTone = "professional"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "subject_pattern", "body_pattern", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailTemplateUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: EmailTemplateCategory | None = None
    subject_pattern: str | None = Field(default=None, alias="subjectPattern", max_length=220)
    body_pattern: str | None = Field(default=None, alias="bodyPattern", min_length=1, max_length=12000)
    tone: EmailTone | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "subject_pattern", "body_pattern", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailHistoryCreateRequest(BaseModel):
    project_id: int | None = Field(default=None, alias="projectId", gt=0)
    draft_id: int | None = Field(default=None, alias="draftId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    action_type: EmailHistoryActionType = Field(default="drafted", alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailHistoryUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    action_type: EmailHistoryActionType | None = Field(default=None, alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmailProjectResponse(BaseModel):
    id: int
    title: str
    audience: str | None
    goal: str | None
    tone: EmailTone
    status: EmailProjectStatus
    draft_count: int = Field(serialization_alias="draftCount")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailDraftResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    template_id: int | None = Field(serialization_alias="templateId")
    template_title: str | None = Field(serialization_alias="templateTitle")
    subject: str
    body: str
    tone: EmailTone
    status: EmailDraftStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailDraftListItemResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    template_id: int | None = Field(serialization_alias="templateId")
    template_title: str | None = Field(serialization_alias="templateTitle")
    subject: str
    body_preview: str = Field(serialization_alias="bodyPreview")
    tone: EmailTone
    status: EmailDraftStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailTemplateResponse(BaseModel):
    id: int
    title: str
    category: EmailTemplateCategory
    subject_pattern: str | None = Field(serialization_alias="subjectPattern")
    body_pattern: str = Field(serialization_alias="bodyPattern")
    tone: EmailTone
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailTemplateListItemResponse(BaseModel):
    id: int
    title: str
    category: EmailTemplateCategory
    subject_pattern: str | None = Field(serialization_alias="subjectPattern")
    body_pattern_preview: str = Field(serialization_alias="bodyPatternPreview")
    tone: EmailTone
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailHistoryResponse(BaseModel):
    id: int
    project_id: int | None = Field(serialization_alias="projectId")
    project_title: str | None = Field(serialization_alias="projectTitle")
    draft_id: int | None = Field(serialization_alias="draftId")
    draft_subject: str | None = Field(serialization_alias="draftSubject")
    title: str
    action_type: EmailHistoryActionType = Field(serialization_alias="actionType")
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailHistoryListItemResponse(BaseModel):
    id: int
    project_id: int | None = Field(serialization_alias="projectId")
    project_title: str | None = Field(serialization_alias="projectTitle")
    draft_id: int | None = Field(serialization_alias="draftId")
    draft_subject: str | None = Field(serialization_alias="draftSubject")
    title: str
    action_type: EmailHistoryActionType = Field(serialization_alias="actionType")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class EmailAssistantDashboardResponse(BaseModel):
    projects: list[EmailProjectResponse]
    drafts: list[EmailDraftListItemResponse]
    templates: list[EmailTemplateListItemResponse]
    history: list[EmailHistoryListItemResponse]
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_draft_count: int = Field(serialization_alias="readyDraftCount")
    template_count: int = Field(serialization_alias="templateCount")
