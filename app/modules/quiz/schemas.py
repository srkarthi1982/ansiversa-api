from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuizTaxonomyItemResponse(BaseModel):
    id: int
    name: str
    is_active: bool = Field(serialization_alias="isActive")
    question_count: int = Field(serialization_alias="qCount")

    model_config = ConfigDict(from_attributes=True)


class QuizPlatformResponse(QuizTaxonomyItemResponse):
    description: str
    type: str | None


class QuizSubjectResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")


class QuizTopicResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")
    subject_id: int = Field(serialization_alias="subjectId")


class QuizRoadmapResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")
    subject_id: int = Field(serialization_alias="subjectId")
    topic_id: int = Field(serialization_alias="topicId")


class QuizPlatformListResponse(BaseModel):
    items: list[QuizPlatformResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizSubjectListResponse(BaseModel):
    items: list[QuizSubjectResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizTopicListResponse(BaseModel):
    items: list[QuizTopicResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizRoadmapListResponse(BaseModel):
    items: list[QuizRoadmapResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizAttemptRequest(BaseModel):
    platform_id: int = Field(validation_alias="platformId", ge=1)
    subject_id: int = Field(validation_alias="subjectId", ge=1)
    topic_id: int = Field(validation_alias="topicId", ge=1)
    roadmap_id: int = Field(validation_alias="roadmapId", ge=1)
    level: Literal["E", "M", "D"]
    limit: int = Field(default=10, ge=1, le=10)
    excluded_question_ids: list[int] = Field(
        default_factory=list,
        validation_alias="excludedQuestionIds",
        max_length=500,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("excluded_question_ids")
    @classmethod
    def validate_excluded_question_ids(cls, value: list[int]) -> list[int]:
        if any(question_id < 1 for question_id in value):
            raise ValueError("Excluded question IDs must be positive integers.")

        return list(dict.fromkeys(value))


class QuizAttemptQuestionResponse(BaseModel):
    id: int
    question_text: str = Field(serialization_alias="questionText")
    options: list[str]
    level: Literal["E", "M", "D"]


class QuizAttemptResponse(BaseModel):
    attempt_id: int = Field(serialization_alias="attemptId")
    questions: list[QuizAttemptQuestionResponse]
    total_questions: int = Field(serialization_alias="totalQuestions")


class QuizAttemptAnswerRequest(BaseModel):
    question_id: int = Field(validation_alias="questionId", ge=1)
    selected_answer: str = Field(validation_alias="selectedAnswer", min_length=1, max_length=500)

    model_config = ConfigDict(extra="forbid")

    @field_validator("selected_answer")
    @classmethod
    def normalize_selected_answer(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Selected answer is required.")

        return normalized


class QuizAttemptSubmitRequest(BaseModel):
    answers: list[QuizAttemptAnswerRequest] = Field(min_length=1, max_length=10)

    model_config = ConfigDict(extra="forbid")


class QuizAttemptReviewResponse(BaseModel):
    question_id: int = Field(serialization_alias="questionId")
    question_text: str = Field(serialization_alias="questionText")
    options: list[str]
    selected_answer: str = Field(serialization_alias="selectedAnswer")
    selected_answer_text: str | None = Field(serialization_alias="selectedAnswerText")
    correct_answer: str = Field(serialization_alias="correctAnswer")
    correct_answer_text: str | None = Field(serialization_alias="correctAnswerText")
    is_correct: bool = Field(serialization_alias="isCorrect")
    explanation: str


class QuizAttemptSubmitResponse(BaseModel):
    result_id: int = Field(serialization_alias="resultId")
    score: int
    total: int
    percentage: int
    review: list[QuizAttemptReviewResponse]


class QuizHistoryContextResponse(BaseModel):
    platform_id: int = Field(serialization_alias="platformId")
    platform_name: str = Field(serialization_alias="platformName")
    subject_id: int = Field(serialization_alias="subjectId")
    subject_name: str = Field(serialization_alias="subjectName")
    topic_id: int = Field(serialization_alias="topicId")
    topic_name: str = Field(serialization_alias="topicName")
    roadmap_id: int = Field(serialization_alias="roadmapId")
    roadmap_name: str = Field(serialization_alias="roadmapName")
    level: Literal["E", "M", "D"]


class QuizAttemptHistoryItemResponse(QuizHistoryContextResponse):
    id: int
    status: str
    result_id: int | None = Field(serialization_alias="resultId")
    score: int | None
    total_questions: int = Field(serialization_alias="totalQuestions")
    percentage: int | None
    created_at: datetime = Field(serialization_alias="createdAt")
    submitted_at: datetime | None = Field(serialization_alias="submittedAt")
    expires_at: datetime = Field(serialization_alias="expiresAt")


class QuizAttemptHistoryListResponse(BaseModel):
    items: list[QuizAttemptHistoryItemResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizResultHistoryItemResponse(QuizHistoryContextResponse):
    id: int
    attempt_id: int | None = Field(serialization_alias="attemptId")
    score: int
    total_questions: int = Field(serialization_alias="totalQuestions")
    percentage: int
    created_at: datetime = Field(serialization_alias="createdAt")
    submitted_at: datetime | None = Field(serialization_alias="submittedAt")


class QuizResultHistoryListResponse(BaseModel):
    items: list[QuizResultHistoryItemResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizResultDetailResponse(QuizResultHistoryItemResponse):
    review: list[QuizAttemptReviewResponse]
