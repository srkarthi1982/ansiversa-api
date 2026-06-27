from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

InterviewSessionStatus = Literal["draft", "inProgress", "completed"]
InterviewType = Literal["behavioral", "technical", "screening", "leadership", "custom"]
InterviewQuestionCategory = Literal["behavioral", "technical", "role", "company", "closing"]
InterviewAnswerStatus = Literal["draft", "answered"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class InterviewSessionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    role_title: str = Field(alias="roleTitle", min_length=1, max_length=140)
    company_name: str | None = Field(default=None, alias="companyName", max_length=140)
    interview_type: InterviewType = Field(default="behavioral", alias="interviewType")
    target_date: date | None = Field(default=None, alias="targetDate")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "role_title", "company_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewSessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    role_title: str | None = Field(default=None, alias="roleTitle", min_length=1, max_length=140)
    company_name: str | None = Field(default=None, alias="companyName", max_length=140)
    interview_type: InterviewType | None = Field(default=None, alias="interviewType")
    target_date: date | None = Field(default=None, alias="targetDate")
    status: InterviewSessionStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "role_title", "company_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewQuestionCreateRequest(BaseModel):
    session_id: int = Field(alias="sessionId", gt=0)
    prompt: str = Field(min_length=1, max_length=2000)
    category: InterviewQuestionCategory = "behavioral"
    position: int = Field(default=1, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("prompt", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewQuestionUpdateRequest(BaseModel):
    prompt: str | None = Field(default=None, min_length=1, max_length=2000)
    category: InterviewQuestionCategory | None = None
    position: int | None = Field(default=None, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("prompt", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewAnswerCreateRequest(BaseModel):
    question_id: int = Field(alias="questionId", gt=0)
    answer_text: str = Field(alias="answerText", min_length=1, max_length=5000)
    confidence: int = Field(default=3, ge=1, le=5)
    status: InterviewAnswerStatus = "answered"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewAnswerUpdateRequest(BaseModel):
    answer_text: str | None = Field(default=None, alias="answerText", min_length=1, max_length=5000)
    confidence: int | None = Field(default=None, ge=1, le=5)
    status: InterviewAnswerStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewReviewCreateRequest(BaseModel):
    session_id: int = Field(alias="sessionId", gt=0)
    readiness_score: int = Field(alias="readinessScore", ge=1, le=5)
    strengths: str | None = Field(default=None, max_length=3000)
    improvements: str | None = Field(default=None, max_length=3000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("strengths", "improvements", "next_steps", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewSessionResponse(BaseModel):
    id: int
    title: str
    role_title: str = Field(serialization_alias="roleTitle")
    company_name: str | None = Field(serialization_alias="companyName")
    interview_type: InterviewType = Field(serialization_alias="interviewType")
    target_date: date | None = Field(serialization_alias="targetDate")
    status: InterviewSessionStatus
    question_count: int = Field(serialization_alias="questionCount")
    answered_count: int = Field(serialization_alias="answeredCount")
    review_count: int = Field(serialization_alias="reviewCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionListResponse(BaseModel):
    items: list[InterviewSessionResponse]


class InterviewQuestionResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    session_title: str = Field(serialization_alias="sessionTitle")
    prompt: str
    category: InterviewQuestionCategory
    position: int
    has_answer: bool = Field(serialization_alias="hasAnswer")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewQuestionListResponse(BaseModel):
    items: list[InterviewQuestionResponse]


class InterviewAnswerResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    question_id: int = Field(serialization_alias="questionId")
    question_prompt: str = Field(serialization_alias="questionPrompt")
    answer_text: str = Field(serialization_alias="answerText")
    confidence: int
    status: InterviewAnswerStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewAnswerListResponse(BaseModel):
    items: list[InterviewAnswerResponse]


class InterviewReviewResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    session_title: str = Field(serialization_alias="sessionTitle")
    readiness_score: int = Field(serialization_alias="readinessScore")
    strengths: str | None
    improvements: str | None
    next_steps: str | None = Field(serialization_alias="nextSteps")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewReviewListResponse(BaseModel):
    items: list[InterviewReviewResponse]


class InterviewCoachDashboardResponse(BaseModel):
    sessions: list[InterviewSessionResponse]
    questions: list[InterviewQuestionResponse]
    answers: list[InterviewAnswerResponse]
    reviews: list[InterviewReviewResponse]
    active_session_count: int = Field(serialization_alias="activeSessionCount")
    completed_session_count: int = Field(serialization_alias="completedSessionCount")
    answered_question_count: int = Field(serialization_alias="answeredQuestionCount")
    average_readiness_score: int = Field(serialization_alias="averageReadinessScore")
