from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ExamOption = Literal["A", "B", "C", "D"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ExamPaperCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    subject: str = Field(min_length=1, max_length=140)
    duration_minutes: int = Field(validation_alias="durationMinutes", ge=1, le=360)
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExamPaperUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    subject: str | None = Field(default=None, min_length=1, max_length=140)
    duration_minutes: int | None = Field(
        default=None,
        validation_alias="durationMinutes",
        ge=1,
        le=360,
    )
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "subject", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExamPaperResponse(BaseModel):
    id: str
    title: str
    subject: str
    duration_minutes: int = Field(serialization_alias="durationMinutes")
    description: str | None
    question_count: int = Field(serialization_alias="questionCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ExamPaperListResponse(BaseModel):
    items: list[ExamPaperResponse]


class ExamQuestionCreateRequest(BaseModel):
    question_text: str = Field(validation_alias="questionText", min_length=1, max_length=2000)
    option_a: str = Field(validation_alias="optionA", min_length=1, max_length=500)
    option_b: str = Field(validation_alias="optionB", min_length=1, max_length=500)
    option_c: str = Field(validation_alias="optionC", min_length=1, max_length=500)
    option_d: str = Field(validation_alias="optionD", min_length=1, max_length=500)
    correct_option: ExamOption = Field(validation_alias="correctOption")
    explanation: str | None = Field(default=None, max_length=1000)
    marks: int = Field(default=1, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "explanation",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExamQuestionUpdateRequest(BaseModel):
    question_text: str | None = Field(default=None, validation_alias="questionText", min_length=1, max_length=2000)
    option_a: str | None = Field(default=None, validation_alias="optionA", min_length=1, max_length=500)
    option_b: str | None = Field(default=None, validation_alias="optionB", min_length=1, max_length=500)
    option_c: str | None = Field(default=None, validation_alias="optionC", min_length=1, max_length=500)
    option_d: str | None = Field(default=None, validation_alias="optionD", min_length=1, max_length=500)
    correct_option: ExamOption | None = Field(default=None, validation_alias="correctOption")
    explanation: str | None = Field(default=None, max_length=1000)
    marks: int | None = Field(default=None, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "explanation",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExamQuestionResponse(BaseModel):
    id: str
    paper_id: str = Field(serialization_alias="paperId")
    question_text: str = Field(serialization_alias="questionText")
    option_a: str = Field(serialization_alias="optionA")
    option_b: str = Field(serialization_alias="optionB")
    option_c: str = Field(serialization_alias="optionC")
    option_d: str = Field(serialization_alias="optionD")
    correct_option: ExamOption = Field(serialization_alias="correctOption")
    explanation: str | None
    marks: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionListResponse(BaseModel):
    items: list[ExamQuestionResponse]


class ExamPaperDetailResponse(BaseModel):
    paper: ExamPaperResponse
    questions: list[ExamQuestionResponse]


class ExamAttemptAnswerRequest(BaseModel):
    question_id: str = Field(validation_alias="questionId", min_length=1)
    selected_option: ExamOption = Field(validation_alias="selectedOption")

    model_config = ConfigDict(extra="forbid")


class ExamAttemptAnswersRequest(BaseModel):
    answers: list[ExamAttemptAnswerRequest]

    model_config = ConfigDict(extra="forbid")


class ExamAttemptResponse(BaseModel):
    id: str
    paper: ExamPaperResponse
    questions: list[ExamQuestionResponse]
    answers: dict[str, ExamOption]
    total_questions: int = Field(serialization_alias="totalQuestions")
    total_marks: int = Field(serialization_alias="totalMarks")
    started_at: datetime = Field(serialization_alias="startedAt")
    submitted_at: datetime | None = Field(serialization_alias="submittedAt")
    status: str


class ExamReviewQuestionResponse(BaseModel):
    question_id: str = Field(serialization_alias="questionId")
    question_text: str = Field(serialization_alias="questionText")
    selected_option: ExamOption | None = Field(serialization_alias="selectedOption")
    correct_option: ExamOption = Field(serialization_alias="correctOption")
    selected_answer: str | None = Field(serialization_alias="selectedAnswer")
    correct_answer: str = Field(serialization_alias="correctAnswer")
    explanation: str | None
    is_correct: bool = Field(serialization_alias="isCorrect")
    marks: int


class ExamReviewResponse(BaseModel):
    attempt_id: str = Field(serialization_alias="attemptId")
    total_questions: int = Field(serialization_alias="totalQuestions")
    correct_answers: int = Field(serialization_alias="correctAnswers")
    wrong_answers: int = Field(serialization_alias="wrongAnswers")
    unanswered: int
    score: int
    total_marks: int = Field(serialization_alias="totalMarks")
    percentage: int
    completed_at: datetime = Field(serialization_alias="completedAt")
    questions: list[ExamReviewQuestionResponse]
