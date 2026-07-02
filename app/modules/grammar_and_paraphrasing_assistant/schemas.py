from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["draft", "active", "archived"]
JobStatus = Literal["queued", "running", "completed", "failed"]
GrammarAction = Literal["correct", "paraphrase", "improve"]
ToneOption = Literal["clear", "professional", "friendly", "concise", "confident"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class GrammarProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    original_text: str = Field(alias="originalText", min_length=1, max_length=12000)
    language: str | None = Field(default="English", max_length=80)
    status: ProjectStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GrammarProjectUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    original_text: str | None = Field(default=None, alias="originalText", min_length=1, max_length=12000)
    language: str | None = Field(default=None, max_length=80)
    status: ProjectStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GrammarRunRequest(BaseModel):
    action: GrammarAction = "improve"
    tone: ToneOption = "clear"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class GrammarProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    language: str | None
    status: ProjectStatus
    original_preview: str = Field(serialization_alias="originalPreview")
    result_count: int = Field(serialization_alias="resultCount")
    latest_tone: str | None = Field(serialization_alias="latestTone")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class GrammarProjectDetailResponse(GrammarProjectSummaryResponse):
    original_text: str = Field(serialization_alias="originalText")


class GrammarResultSummaryResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    corrected_preview: str = Field(serialization_alias="correctedPreview")
    paraphrased_preview: str = Field(serialization_alias="paraphrasedPreview")
    tone: str | None
    grammar_score: int = Field(serialization_alias="grammarScore")
    readability_score: int = Field(serialization_alias="readabilityScore")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class GrammarResultDetailResponse(GrammarResultSummaryResponse):
    original_text: str = Field(serialization_alias="originalText")
    corrected_text: str = Field(serialization_alias="correctedText")
    paraphrased_text: str = Field(serialization_alias="paraphrasedText")


class GrammarJobResponse(BaseModel):
    id: int
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    status: JobStatus
    provider: str
    action: GrammarAction
    started_at: datetime = Field(serialization_alias="startedAt")
    completed_at: datetime | None = Field(serialization_alias="completedAt")

    model_config = ConfigDict(from_attributes=True)


class GrammarRunResponse(BaseModel):
    project: GrammarProjectDetailResponse
    result: GrammarResultDetailResponse
    job: GrammarJobResponse


class GrammarAndParaphrasingDashboardResponse(BaseModel):
    projects: list[GrammarProjectSummaryResponse]
    results: list[GrammarResultSummaryResponse]
    history: list[GrammarJobResponse]
    project_count: int = Field(serialization_alias="projectCount")
    result_count: int = Field(serialization_alias="resultCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_project_count: int = Field(serialization_alias="activeProjectCount")

    model_config = ConfigDict(from_attributes=True)
