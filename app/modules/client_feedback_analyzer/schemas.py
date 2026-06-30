from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FeedbackSentiment = Literal["positive", "neutral", "negative", "mixed"]
FeedbackStatus = Literal["new", "reviewed", "actioned", "archived"]
InsightPriority = Literal["low", "medium", "high", "urgent"]
InsightStatus = Literal["open", "planned", "resolved", "archived"]
ReportStatus = Literal["draft", "reviewed", "shared", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ClientProfileCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    name: str = Field(min_length=1, max_length=180)
    company_name: str | None = Field(default=None, alias="companyName", max_length=180)
    contact_name: str | None = Field(default=None, alias="contactName", max_length=180)
    email: str | None = Field(default=None, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    segment: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ClientProfileUpdateRequest(ClientProfileCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)


class ClientFeedbackCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    client_id: int = Field(alias="clientId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    source: str | None = Field(default=None, max_length=120)
    feedback_text: str = Field(alias="feedbackText", min_length=1, max_length=8000)
    sentiment: FeedbackSentiment = "neutral"
    rating: int | None = Field(default=None, ge=1, le=10)
    status: FeedbackStatus = "new"
    received_at: str | None = Field(default=None, alias="receivedAt", max_length=40)
    tags: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "source", "feedback_text", "received_at", "tags", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ClientFeedbackUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    source: str | None = Field(default=None, max_length=120)
    feedback_text: str | None = Field(default=None, alias="feedbackText", min_length=1, max_length=8000)
    sentiment: FeedbackSentiment | None = None
    rating: int | None = Field(default=None, ge=1, le=10)
    status: FeedbackStatus | None = None
    received_at: str | None = Field(default=None, alias="receivedAt", max_length=40)
    tags: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "source", "feedback_text", "received_at", "tags", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class FeedbackInsightCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    client_id: int = Field(alias="clientId", gt=0)
    feedback_id: int | None = Field(default=None, alias="feedbackId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    sentiment: FeedbackSentiment = "neutral"
    priority: InsightPriority = "medium"
    recommendation: str | None = Field(default=None, max_length=5000)
    status: InsightStatus = "open"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "category", "recommendation", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class FeedbackInsightUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    feedback_id: int | None = Field(default=None, alias="feedbackId", gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    sentiment: FeedbackSentiment | None = None
    priority: InsightPriority | None = None
    recommendation: str | None = Field(default=None, max_length=5000)
    status: InsightStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "category", "recommendation", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class FeedbackReportCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    scope: str | None = Field(default=None, max_length=120)
    summary: str = Field(min_length=1, max_length=8000)
    period_start: str | None = Field(default=None, alias="periodStart", max_length=40)
    period_end: str | None = Field(default=None, alias="periodEnd", max_length=40)
    status: ReportStatus = "draft"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "scope", "summary", "period_start", "period_end", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class FeedbackReportUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    scope: str | None = Field(default=None, max_length=120)
    summary: str | None = Field(default=None, min_length=1, max_length=8000)
    period_start: str | None = Field(default=None, alias="periodStart", max_length=40)
    period_end: str | None = Field(default=None, alias="periodEnd", max_length=40)
    status: ReportStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "scope", "summary", "period_start", "period_end", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ClientProfileSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    name: str
    company_name: str | None = Field(serialization_alias="companyName")
    contact_name: str | None = Field(serialization_alias="contactName")
    email: str | None
    industry: str | None
    segment: str | None
    feedback_count: int = Field(serialization_alias="feedbackCount")
    insight_count: int = Field(serialization_alias="insightCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ClientProfileDetailResponse(ClientProfileSummaryResponse):
    notes: str | None


class ClientFeedbackSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    client_id: int = Field(serialization_alias="clientId")
    client_name: str = Field(serialization_alias="clientName")
    title: str
    source: str | None
    feedback_preview: str | None = Field(serialization_alias="feedbackPreview")
    sentiment: FeedbackSentiment
    rating: int | None
    status: FeedbackStatus
    received_at: str | None = Field(serialization_alias="receivedAt")
    tags_preview: str | None = Field(serialization_alias="tagsPreview")
    insight_count: int = Field(serialization_alias="insightCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ClientFeedbackDetailResponse(ClientFeedbackSummaryResponse):
    feedback_text: str = Field(serialization_alias="feedbackText")
    tags: str | None


class FeedbackInsightSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    client_id: int = Field(serialization_alias="clientId")
    client_name: str = Field(serialization_alias="clientName")
    feedback_id: int | None = Field(serialization_alias="feedbackId")
    feedback_title: str | None = Field(serialization_alias="feedbackTitle")
    title: str
    category: str | None
    sentiment: FeedbackSentiment
    priority: InsightPriority
    recommendation_preview: str | None = Field(serialization_alias="recommendationPreview")
    status: InsightStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class FeedbackInsightDetailResponse(FeedbackInsightSummaryResponse):
    recommendation: str | None
    notes: str | None


class FeedbackReportSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    scope: str | None
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    period_start: str | None = Field(serialization_alias="periodStart")
    period_end: str | None = Field(serialization_alias="periodEnd")
    status: ReportStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class FeedbackReportDetailResponse(FeedbackReportSummaryResponse):
    summary: str


class ClientFeedbackAnalyzerDashboardResponse(BaseModel):
    clients: list[ClientProfileSummaryResponse]
    feedback: list[ClientFeedbackSummaryResponse]
    insights: list[FeedbackInsightSummaryResponse]
    reports: list[FeedbackReportSummaryResponse]
    client_count: int = Field(serialization_alias="clientCount")
    feedback_count: int = Field(serialization_alias="feedbackCount")
    insight_count: int = Field(serialization_alias="insightCount")
    report_count: int = Field(serialization_alias="reportCount")
    negative_feedback_count: int = Field(serialization_alias="negativeFeedbackCount")
    urgent_insight_count: int = Field(serialization_alias="urgentInsightCount")

    model_config = ConfigDict(from_attributes=True)
