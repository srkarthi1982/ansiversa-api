from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

JobDescriptionStatus = Literal["draft", "ready", "analyzing", "reviewed", "archived"]
AnalysisStatus = Literal["draft", "review", "complete", "archived"]
SkillMatchLevel = Literal["missing", "partial", "matched", "strong"]
HistoryEventType = Literal["note", "imported", "analyzed", "skills-reviewed", "recommendation", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class JobDescriptionCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    company_name: str = Field(alias="companyName", min_length=1, max_length=180)
    location: str | None = Field(default=None, max_length=180)
    employment_type: str | None = Field(default=None, alias="employmentType", max_length=80)
    source_url: str | None = Field(default=None, alias="sourceUrl", max_length=500)
    status: JobDescriptionStatus = "draft"
    seniority: str | None = Field(default=None, max_length=80)
    description_text: str | None = Field(default=None, alias="descriptionText", max_length=12000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class JobDescriptionUpdateRequest(JobDescriptionCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    company_name: str | None = Field(default=None, alias="companyName", min_length=1, max_length=180)
    status: JobDescriptionStatus | None = None


class JobAnalysisCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    job_description_id: int = Field(alias="jobDescriptionId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    status: AnalysisStatus = "draft"
    match_score: int = Field(default=0, alias="matchScore", ge=0, le=100)
    summary: str | None = Field(default=None, max_length=5000)
    keywords: str | None = Field(default=None, max_length=3000)
    responsibilities: str | None = Field(default=None, max_length=5000)
    recommendations: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class JobAnalysisUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: AnalysisStatus | None = None
    match_score: int | None = Field(default=None, alias="matchScore", ge=0, le=100)
    summary: str | None = Field(default=None, max_length=5000)
    keywords: str | None = Field(default=None, max_length=3000)
    responsibilities: str | None = Field(default=None, max_length=5000)
    recommendations: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SkillMatchCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    analysis_id: int = Field(alias="analysisId", gt=0)
    skill_name: str = Field(alias="skillName", min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    match_level: SkillMatchLevel = Field(default="partial", alias="matchLevel")
    evidence: str | None = Field(default=None, max_length=4000)
    recommendation: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SkillMatchUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    skill_name: str | None = Field(default=None, alias="skillName", min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    match_level: SkillMatchLevel | None = Field(default=None, alias="matchLevel")
    evidence: str | None = Field(default=None, max_length=4000)
    recommendation: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AnalysisHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    analysis_id: int = Field(alias="analysisId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    summary: str | None = Field(default=None, max_length=5000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AnalysisHistoryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    summary: str | None = Field(default=None, max_length=5000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class JobDescriptionSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    company_name: str = Field(serialization_alias="companyName")
    location: str | None
    employment_type: str | None = Field(serialization_alias="employmentType")
    status: JobDescriptionStatus
    seniority: str | None
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    analysis_count: int = Field(serialization_alias="analysisCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class JobDescriptionDetailResponse(JobDescriptionSummaryResponse):
    source_url: str | None = Field(serialization_alias="sourceUrl")
    description_text: str | None = Field(serialization_alias="descriptionText")
    notes: str | None


class JobAnalysisSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    job_description_id: int = Field(serialization_alias="jobDescriptionId")
    job_title: str = Field(serialization_alias="jobTitle")
    title: str
    status: AnalysisStatus
    match_score: int = Field(serialization_alias="matchScore")
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    skill_count: int = Field(serialization_alias="skillCount")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class JobAnalysisDetailResponse(JobAnalysisSummaryResponse):
    summary: str | None
    keywords: str | None
    responsibilities: str | None
    recommendations: str | None


class SkillMatchSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    analysis_id: int = Field(serialization_alias="analysisId")
    analysis_title: str = Field(serialization_alias="analysisTitle")
    skill_name: str = Field(serialization_alias="skillName")
    category: str | None
    match_level: SkillMatchLevel = Field(serialization_alias="matchLevel")
    evidence_preview: str | None = Field(serialization_alias="evidencePreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SkillMatchDetailResponse(SkillMatchSummaryResponse):
    evidence: str | None
    recommendation: str | None


class AnalysisHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    analysis_id: int = Field(serialization_alias="analysisId")
    analysis_title: str = Field(serialization_alias="analysisTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    next_steps_preview: str | None = Field(serialization_alias="nextStepsPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryDetailResponse(AnalysisHistorySummaryResponse):
    summary: str | None
    next_steps: str | None = Field(serialization_alias="nextSteps")


class JobDescriptionAnalyzerDashboardResponse(BaseModel):
    jobs: list[JobDescriptionSummaryResponse]
    analysis: list[JobAnalysisSummaryResponse]
    skills: list[SkillMatchSummaryResponse]
    history: list[AnalysisHistorySummaryResponse]
    job_count: int = Field(serialization_alias="jobCount")
    analysis_count: int = Field(serialization_alias="analysisCount")
    skill_count: int = Field(serialization_alias="skillCount")
    history_count: int = Field(serialization_alias="historyCount")
    reviewed_job_count: int = Field(serialization_alias="reviewedJobCount")
    strong_skill_count: int = Field(serialization_alias="strongSkillCount")

    model_config = ConfigDict(from_attributes=True)
