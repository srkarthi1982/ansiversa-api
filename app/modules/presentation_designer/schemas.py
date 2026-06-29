from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "review", "ready", "archived"]
AssetType = Literal["text", "image", "chart", "icon", "reference"]
ReviewActionType = Literal["created", "updated", "reviewed", "exported", "presented", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class PresentationProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    audience: str | None = Field(default=None, max_length=180)
    theme: str = Field(default="modern", min_length=1, max_length=80)
    status: ProjectStatus = "draft"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "audience", "theme", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    audience: str | None = Field(default=None, max_length=180)
    theme: str | None = Field(default=None, min_length=1, max_length=80)
    status: ProjectStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "audience", "theme", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationSlideCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    layout: str = Field(default="title-body", min_length=1, max_length=80)
    headline: str | None = Field(default=None, max_length=240)
    body: str | None = Field(default=None, max_length=8000)
    speaker_notes: str | None = Field(default=None, alias="speakerNotes", max_length=5000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "layout", "headline", "body", "speaker_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationSlideUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    layout: str | None = Field(default=None, min_length=1, max_length=80)
    headline: str | None = Field(default=None, max_length=240)
    body: str | None = Field(default=None, max_length=8000)
    speaker_notes: str | None = Field(default=None, alias="speakerNotes", max_length=5000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "layout", "headline", "body", "speaker_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationAssetCreateRequest(BaseModel):
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    asset_type: AssetType = Field(default="text", alias="assetType")
    description: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=3000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "source", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationAssetUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    asset_type: AssetType | None = Field(default=None, alias="assetType")
    description: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=3000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "source", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationReviewHistoryCreateRequest(BaseModel):
    project_id: int | None = Field(default=None, alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    action_type: ReviewActionType = Field(default="reviewed", alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationReviewHistoryUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    action_type: ReviewActionType | None = Field(default=None, alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PresentationProjectSummaryResponse(BaseModel):
    id: int
    title: str
    audience: str | None
    theme: str
    status: ProjectStatus
    slide_count: int = Field(serialization_alias="slideCount")
    asset_count: int = Field(serialization_alias="assetCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PresentationProjectDetailResponse(PresentationProjectSummaryResponse):
    notes: str | None


class PresentationSlideSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    layout: str
    headline: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PresentationSlideDetailResponse(PresentationSlideSummaryResponse):
    body: str | None
    speaker_notes: str | None = Field(serialization_alias="speakerNotes")


class PresentationAssetSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    asset_type: AssetType = Field(serialization_alias="assetType")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PresentationAssetDetailResponse(PresentationAssetSummaryResponse):
    description: str | None
    source: str | None


class PresentationReviewHistorySummaryResponse(BaseModel):
    id: int
    project_id: int | None = Field(serialization_alias="projectId")
    project_title: str | None = Field(serialization_alias="projectTitle")
    title: str
    action_type: ReviewActionType = Field(serialization_alias="actionType")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PresentationReviewHistoryDetailResponse(PresentationReviewHistorySummaryResponse):
    notes: str | None


class PresentationDashboardResponse(BaseModel):
    projects: list[PresentationProjectSummaryResponse]
    slides: list[PresentationSlideSummaryResponse]
    assets: list[PresentationAssetSummaryResponse]
    review_history: list[PresentationReviewHistorySummaryResponse] = Field(serialization_alias="reviewHistory")
    draft_project_count: int = Field(serialization_alias="draftProjectCount")
    review_project_count: int = Field(serialization_alias="reviewProjectCount")
    ready_project_count: int = Field(serialization_alias="readyProjectCount")

    model_config = ConfigDict(from_attributes=True)
