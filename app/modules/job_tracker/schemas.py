from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

JobPriority = Literal["low", "medium", "high", "urgent"]
JobStatus = Literal["tracking", "applied", "interviewing", "offer", "closed", "archived"]
ApplicationStatus = Literal["draft", "applied", "screening", "interviewing", "offer", "rejected", "withdrawn", "archived"]
InsightPriority = Literal["low", "medium", "high", "urgent"]
InsightStatus = Literal["open", "planned", "done", "archived"]
HistoryEventType = Literal["note", "applied", "follow-up", "interview", "offer", "rejection", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class JobListingCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    company_name: str = Field(alias="companyName", min_length=1, max_length=180)
    location: str | None = Field(default=None, max_length=180)
    employment_type: str | None = Field(default=None, alias="employmentType", max_length=80)
    source_url: str | None = Field(default=None, alias="sourceUrl", max_length=500)
    status: JobStatus = "tracking"
    priority: JobPriority = "medium"
    salary_range: str | None = Field(default=None, alias="salaryRange", max_length=120)
    description: str | None = Field(default=None, max_length=8000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class JobListingUpdateRequest(JobListingCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    company_name: str | None = Field(default=None, alias="companyName", min_length=1, max_length=180)
    status: JobStatus | None = None
    priority: JobPriority | None = None


class JobApplicationCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    job_id: int = Field(alias="jobId", gt=0)
    role_title: str = Field(alias="roleTitle", min_length=1, max_length=180)
    company_name: str = Field(alias="companyName", min_length=1, max_length=180)
    status: ApplicationStatus = "draft"
    applied_at: str | None = Field(default=None, alias="appliedAt", max_length=40)
    follow_up_date: str | None = Field(default=None, alias="followUpDate", max_length=40)
    contact_name: str | None = Field(default=None, alias="contactName", max_length=180)
    contact_email: str | None = Field(default=None, alias="contactEmail", max_length=180)
    resume_version: str | None = Field(default=None, alias="resumeVersion", max_length=120)
    cover_letter_version: str | None = Field(default=None, alias="coverLetterVersion", max_length=120)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class JobApplicationUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    role_title: str | None = Field(default=None, alias="roleTitle", min_length=1, max_length=180)
    company_name: str | None = Field(default=None, alias="companyName", min_length=1, max_length=180)
    status: ApplicationStatus | None = None
    applied_at: str | None = Field(default=None, alias="appliedAt", max_length=40)
    follow_up_date: str | None = Field(default=None, alias="followUpDate", max_length=40)
    contact_name: str | None = Field(default=None, alias="contactName", max_length=180)
    contact_email: str | None = Field(default=None, alias="contactEmail", max_length=180)
    resume_version: str | None = Field(default=None, alias="resumeVersion", max_length=120)
    cover_letter_version: str | None = Field(default=None, alias="coverLetterVersion", max_length=120)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ApplicationInsightCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    application_id: int = Field(alias="applicationId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    priority: InsightPriority = "medium"
    status: InsightStatus = "open"
    recommendation: str | None = Field(default=None, max_length=5000)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ApplicationInsightUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    priority: InsightPriority | None = None
    status: InsightStatus | None = None
    recommendation: str | None = Field(default=None, max_length=5000)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ApplicationHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    application_id: int = Field(alias="applicationId", gt=0)
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


class JobListingSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    company_name: str = Field(serialization_alias="companyName")
    location: str | None
    employment_type: str | None = Field(serialization_alias="employmentType")
    status: JobStatus
    priority: JobPriority
    salary_range: str | None = Field(serialization_alias="salaryRange")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    application_count: int = Field(serialization_alias="applicationCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class JobListingDetailResponse(JobListingSummaryResponse):
    source_url: str | None = Field(serialization_alias="sourceUrl")
    description: str | None
    notes: str | None


class JobApplicationSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    job_id: int = Field(serialization_alias="jobId")
    job_title: str = Field(serialization_alias="jobTitle")
    role_title: str = Field(serialization_alias="roleTitle")
    company_name: str = Field(serialization_alias="companyName")
    status: ApplicationStatus
    applied_at: str | None = Field(serialization_alias="appliedAt")
    follow_up_date: str | None = Field(serialization_alias="followUpDate")
    contact_name: str | None = Field(serialization_alias="contactName")
    insight_count: int = Field(serialization_alias="insightCount")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class JobApplicationDetailResponse(JobApplicationSummaryResponse):
    contact_email: str | None = Field(serialization_alias="contactEmail")
    resume_version: str | None = Field(serialization_alias="resumeVersion")
    cover_letter_version: str | None = Field(serialization_alias="coverLetterVersion")
    notes: str | None


class ApplicationInsightSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    application_id: int = Field(serialization_alias="applicationId")
    application_title: str = Field(serialization_alias="applicationTitle")
    title: str
    category: str | None
    priority: InsightPriority
    status: InsightStatus
    recommendation_preview: str | None = Field(serialization_alias="recommendationPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ApplicationInsightDetailResponse(ApplicationInsightSummaryResponse):
    recommendation: str | None
    notes: str | None


class ApplicationHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    application_id: int = Field(serialization_alias="applicationId")
    application_title: str = Field(serialization_alias="applicationTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    next_steps_preview: str | None = Field(serialization_alias="nextStepsPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ApplicationHistoryDetailResponse(ApplicationHistorySummaryResponse):
    summary: str | None
    next_steps: str | None = Field(serialization_alias="nextSteps")


class JobTrackerDashboardResponse(BaseModel):
    jobs: list[JobListingSummaryResponse]
    applications: list[JobApplicationSummaryResponse]
    insights: list[ApplicationInsightSummaryResponse]
    history: list[ApplicationHistorySummaryResponse]
    job_count: int = Field(serialization_alias="jobCount")
    application_count: int = Field(serialization_alias="applicationCount")
    insight_count: int = Field(serialization_alias="insightCount")
    history_count: int = Field(serialization_alias="historyCount")
    active_application_count: int = Field(serialization_alias="activeApplicationCount")
    urgent_insight_count: int = Field(serialization_alias="urgentInsightCount")

    model_config = ConfigDict(from_attributes=True)
