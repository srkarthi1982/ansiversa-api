from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AiJobInterviewSessionStatus = Literal["draft", "inProgress", "completed"]
ExperienceLevel = Literal["entry", "mid", "senior", "lead", "executive"]
InterviewType = Literal["behavioral", "technical", "screening", "leadership", "custom"]
AiJobInterviewQuestionCategory = Literal["behavioral", "technical", "role", "company", "closing"]
AiJobInterviewAnswerStatus = Literal["draft", "answered"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class AiJobInterviewSessionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    role_title: str = Field(alias="roleTitle", min_length=1, max_length=140)
    company_name: str | None = Field(default=None, alias="companyName", max_length=140)
    experience_level: ExperienceLevel = Field(default="mid", alias="experienceLevel")
    interview_type: InterviewType = Field(default="behavioral", alias="interviewType")
    target_date: date | None = Field(default=None, alias="targetDate")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "role_title", "company_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewSessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    role_title: str | None = Field(default=None, alias="roleTitle", min_length=1, max_length=140)
    company_name: str | None = Field(default=None, alias="companyName", max_length=140)
    experience_level: ExperienceLevel | None = Field(default=None, alias="experienceLevel")
    interview_type: InterviewType | None = Field(default=None, alias="interviewType")
    target_date: date | None = Field(default=None, alias="targetDate")
    status: AiJobInterviewSessionStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "role_title", "company_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewQuestionCreateRequest(BaseModel):
    session_id: int = Field(alias="sessionId", gt=0)
    prompt: str = Field(min_length=1, max_length=2000)
    category: AiJobInterviewQuestionCategory = "behavioral"
    position: int = Field(default=1, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("prompt", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewQuestionUpdateRequest(BaseModel):
    prompt: str | None = Field(default=None, min_length=1, max_length=2000)
    category: AiJobInterviewQuestionCategory | None = None
    position: int | None = Field(default=None, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("prompt", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewAnswerCreateRequest(BaseModel):
    question_id: int = Field(alias="questionId", gt=0)
    answer_text: str = Field(alias="answerText", min_length=1, max_length=5000)
    confidence: int = Field(default=3, ge=1, le=5)
    status: AiJobInterviewAnswerStatus = "answered"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewAnswerUpdateRequest(BaseModel):
    answer_text: str | None = Field(default=None, alias="answerText", min_length=1, max_length=5000)
    confidence: int | None = Field(default=None, ge=1, le=5)
    status: AiJobInterviewAnswerStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewResultCreateRequest(BaseModel):
    session_id: int = Field(alias="sessionId", gt=0)
    progress_score: int = Field(alias="progressScore", ge=1, le=5)
    strengths: str | None = Field(default=None, max_length=3000)
    improvements: str | None = Field(default=None, max_length=3000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("strengths", "improvements", "next_steps", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AiJobInterviewSessionResponse(BaseModel):
    id: int
    title: str
    role_title: str = Field(serialization_alias="roleTitle")
    company_name: str | None = Field(serialization_alias="companyName")
    experience_level: ExperienceLevel = Field(serialization_alias="experienceLevel")
    interview_type: InterviewType = Field(serialization_alias="interviewType")
    target_date: date | None = Field(serialization_alias="targetDate")
    status: AiJobInterviewSessionStatus
    question_count: int = Field(serialization_alias="questionCount")
    answered_count: int = Field(serialization_alias="answeredCount")
    result_count: int = Field(serialization_alias="resultCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AiJobInterviewSessionListResponse(BaseModel):
    items: list[AiJobInterviewSessionResponse]


class AiJobInterviewQuestionResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    session_title: str = Field(serialization_alias="sessionTitle")
    prompt: str
    category: AiJobInterviewQuestionCategory
    position: int
    has_answer: bool = Field(serialization_alias="hasAnswer")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AiJobInterviewQuestionListResponse(BaseModel):
    items: list[AiJobInterviewQuestionResponse]


class AiJobInterviewAnswerResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    question_id: int = Field(serialization_alias="questionId")
    question_prompt: str = Field(serialization_alias="questionPrompt")
    answer_text: str = Field(serialization_alias="answerText")
    confidence: int
    status: AiJobInterviewAnswerStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AiJobInterviewAnswerListResponse(BaseModel):
    items: list[AiJobInterviewAnswerResponse]


class AiJobInterviewResultResponse(BaseModel):
    id: int
    session_id: int = Field(serialization_alias="sessionId")
    session_title: str = Field(serialization_alias="sessionTitle")
    progress_score: int = Field(serialization_alias="progressScore")
    strengths: str | None
    improvements: str | None
    next_steps: str | None = Field(serialization_alias="nextSteps")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AiJobInterviewResultListResponse(BaseModel):
    items: list[AiJobInterviewResultResponse]


class AiJobInterviewerDashboardResponse(BaseModel):
    sessions: list[AiJobInterviewSessionResponse]
    questions: list[AiJobInterviewQuestionResponse]
    answers: list[AiJobInterviewAnswerResponse]
    results: list[AiJobInterviewResultResponse]
    active_session_count: int = Field(serialization_alias="activeSessionCount")
    completed_session_count: int = Field(serialization_alias="completedSessionCount")
    answered_question_count: int = Field(serialization_alias="answeredQuestionCount")
    average_progress_score: int = Field(serialization_alias="averageProgressScore")
