from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProposalProjectStatus = Literal["draft", "active", "submitted", "won", "lost"]
ProposalSectionStatus = Literal["draft", "ready", "approved"]
ProposalDraftStatus = Literal["draft", "ready", "submitted", "archived"]
ProposalHistoryActionType = Literal["created", "updated", "reviewed", "submitted", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ProposalProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    client_name: str = Field(alias="clientName", min_length=1, max_length=180)
    opportunity: str | None = Field(default=None, max_length=3000)
    budget_range: str | None = Field(default=None, alias="budgetRange", max_length=120)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    status: ProposalProjectStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "client_name", "opportunity", "budget_range", "due_date", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    client_name: str | None = Field(default=None, alias="clientName", min_length=1, max_length=180)
    opportunity: str | None = Field(default=None, max_length=3000)
    budget_range: str | None = Field(default=None, alias="budgetRange", max_length=120)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    status: ProposalProjectStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "client_name", "opportunity", "budget_range", "due_date", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalSectionCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    content: str = Field(min_length=1, max_length=12000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)
    status: ProposalSectionStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalSectionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    content: str | None = Field(default=None, min_length=1, max_length=12000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)
    status: ProposalSectionStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalDraftCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    summary: str | None = Field(default=None, max_length=3000)
    body: str = Field(min_length=1, max_length=20000)
    status: ProposalDraftStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "summary", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalDraftUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    summary: str | None = Field(default=None, max_length=3000)
    body: str | None = Field(default=None, min_length=1, max_length=20000)
    status: ProposalDraftStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "summary", "body", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalHistoryCreateRequest(BaseModel):
    project_id: int | None = Field(default=None, alias="projectId", gt=0)
    draft_id: int | None = Field(default=None, alias="draftId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    action_type: ProposalHistoryActionType = Field(default="updated", alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProposalProjectSummaryResponse(BaseModel):
    id: int
    title: str
    client_name: str = Field(serialization_alias="clientName")
    budget_range: str | None = Field(serialization_alias="budgetRange")
    due_date: str | None = Field(serialization_alias="dueDate")
    status: ProposalProjectStatus
    section_count: int = Field(serialization_alias="sectionCount")
    draft_count: int = Field(serialization_alias="draftCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalProjectDetailResponse(ProposalProjectSummaryResponse):
    opportunity: str | None


class ProposalSectionSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    content_preview: str = Field(serialization_alias="contentPreview")
    sort_order: int = Field(serialization_alias="sortOrder")
    status: ProposalSectionStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalSectionDetailResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    content: str
    sort_order: int = Field(serialization_alias="sortOrder")
    status: ProposalSectionStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalDraftSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    body_preview: str = Field(serialization_alias="bodyPreview")
    status: ProposalDraftStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalDraftDetailResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    summary: str | None
    body: str
    status: ProposalDraftStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalHistorySummaryResponse(BaseModel):
    id: int
    project_id: int | None = Field(serialization_alias="projectId")
    project_title: str | None = Field(serialization_alias="projectTitle")
    draft_id: int | None = Field(serialization_alias="draftId")
    draft_title: str | None = Field(serialization_alias="draftTitle")
    title: str
    action_type: ProposalHistoryActionType = Field(serialization_alias="actionType")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProposalWriterDashboardResponse(BaseModel):
    projects: list[ProposalProjectSummaryResponse]
    sections: list[ProposalSectionSummaryResponse]
    drafts: list[ProposalDraftSummaryResponse]
    history: list[ProposalHistorySummaryResponse]
    active_project_count: int = Field(serialization_alias="activeProjectCount")
    ready_section_count: int = Field(serialization_alias="readySectionCount")
    ready_draft_count: int = Field(serialization_alias="readyDraftCount")
    submitted_draft_count: int = Field(serialization_alias="submittedDraftCount")

    model_config = ConfigDict(from_attributes=True)
