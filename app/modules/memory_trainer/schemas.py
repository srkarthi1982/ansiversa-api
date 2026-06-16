from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MemoryMode = Literal["number_sequence", "word_sequence", "color_sequence"]
MemoryDifficulty = Literal["easy", "medium", "hard"]
MemorySessionStatus = Literal["active", "completed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


def _normalize_sequence(value: object) -> object:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    return value


class MemoryGameCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    mode: MemoryMode
    difficulty: MemoryDifficulty
    sequence_length: int = Field(validation_alias="sequenceLength", ge=3, le=12)
    round_count: int = Field(validation_alias="roundCount", ge=1, le=12)
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MemoryGameUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    mode: MemoryMode | None = None
    difficulty: MemoryDifficulty | None = None
    sequence_length: int | None = Field(
        default=None,
        validation_alias="sequenceLength",
        ge=3,
        le=12,
    )
    round_count: int | None = Field(
        default=None,
        validation_alias="roundCount",
        ge=1,
        le=12,
    )
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MemoryGameResponse(BaseModel):
    id: str
    title: str
    mode: MemoryMode
    difficulty: MemoryDifficulty
    sequence_length: int = Field(serialization_alias="sequenceLength")
    round_count: int = Field(serialization_alias="roundCount")
    description: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class MemoryGameListResponse(BaseModel):
    items: list[MemoryGameResponse]


class MemoryRoundSubmitRequest(BaseModel):
    round_number: int = Field(validation_alias="roundNumber", ge=1)
    user_answer: list[str] = Field(validation_alias="userAnswer", min_length=1)
    response_time_ms: int = Field(validation_alias="responseTimeMs", ge=0, le=3600000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("user_answer", mode="before")
    @classmethod
    def normalize_user_answer(cls, value: object) -> object:
        return _normalize_sequence(value)


class MemoryRoundResponse(BaseModel):
    id: str
    session_id: str = Field(serialization_alias="sessionId")
    round_number: int = Field(serialization_alias="roundNumber")
    sequence: list[str]
    user_answer: list[str] | None = Field(serialization_alias="userAnswer")
    is_correct: bool | None = Field(serialization_alias="isCorrect")
    response_time_ms: int | None = Field(serialization_alias="responseTimeMs")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MemorySessionResponse(BaseModel):
    id: str
    game_id: str = Field(serialization_alias="gameId")
    status: MemorySessionStatus
    started_at: datetime = Field(serialization_alias="startedAt")
    completed_at: datetime | None = Field(serialization_alias="completedAt")

    model_config = ConfigDict(from_attributes=True)


class MemorySessionDetailResponse(BaseModel):
    session: MemorySessionResponse
    game: MemoryGameResponse
    rounds: list[MemoryRoundResponse]
    current_round: MemoryRoundResponse | None = Field(serialization_alias="currentRound")


class MemoryPerformanceResponse(BaseModel):
    id: str
    session_id: str = Field(serialization_alias="sessionId")
    game_id: str = Field(serialization_alias="gameId")
    total_rounds: int = Field(serialization_alias="totalRounds")
    correct_rounds: int = Field(serialization_alias="correctRounds")
    wrong_rounds: int = Field(serialization_alias="wrongRounds")
    accuracy: int
    average_response_time_ms: int = Field(serialization_alias="averageResponseTimeMs")
    completed_at: datetime = Field(serialization_alias="completedAt")

    model_config = ConfigDict(from_attributes=True)


class MemoryReviewResponse(BaseModel):
    session: MemorySessionResponse
    game: MemoryGameResponse
    rounds: list[MemoryRoundResponse]
    performance: MemoryPerformanceResponse | None


class MemoryProgressResponse(BaseModel):
    total_sessions: int = Field(serialization_alias="totalSessions")
    best_accuracy: int = Field(serialization_alias="bestAccuracy")
    average_accuracy: int = Field(serialization_alias="averageAccuracy")
    total_rounds: int = Field(serialization_alias="totalRounds")
    last_completed_at: datetime | None = Field(serialization_alias="lastCompletedAt")
