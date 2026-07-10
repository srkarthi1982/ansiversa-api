from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VocabularyDifficulty = Literal["new", "learning", "review", "mastered"]
PracticeResult = Literal["correct", "partial", "missed", "skipped"]
SortDirection = Literal["asc", "desc"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class VocabularyCreateRequest(BaseModel):
    word: str = Field(min_length=1, max_length=180)
    translation: str = Field(min_length=1, max_length=180)
    language: str = Field(min_length=1, max_length=80)
    category: str | None = Field(default=None, max_length=80)
    difficulty: VocabularyDifficulty = "new"
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VocabularyUpdateRequest(BaseModel):
    word: str | None = Field(default=None, min_length=1, max_length=180)
    translation: str | None = Field(default=None, min_length=1, max_length=180)
    language: str | None = Field(default=None, min_length=1, max_length=80)
    category: str | None = Field(default=None, max_length=80)
    difficulty: VocabularyDifficulty | None = None
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PracticeSessionCreateRequest(BaseModel):
    vocabulary_id: str = Field(alias="vocabularyId", min_length=1, max_length=36)
    practiced_at: str = Field(alias="practicedAt", min_length=1, max_length=40)
    result: PracticeResult
    confidence: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PracticeSessionUpdateRequest(BaseModel):
    practiced_at: str | None = Field(default=None, alias="practicedAt", min_length=1, max_length=40)
    result: PracticeResult | None = None
    confidence: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VocabularySummaryResponse(BaseModel):
    id: str
    word: str
    translation: str
    language: str
    category: str | None
    difficulty: VocabularyDifficulty
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    session_count: int = Field(serialization_alias="sessionCount")
    last_practiced_at: str | None = Field(serialization_alias="lastPracticedAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VocabularyDetailResponse(VocabularySummaryResponse):
    notes: str | None
    sessions: list["PracticeSessionSummaryResponse"]


class PracticeSessionSummaryResponse(BaseModel):
    id: str
    vocabulary_id: str = Field(serialization_alias="vocabularyId")
    word: str
    translation: str
    language: str
    category: str | None
    practiced_at: str = Field(serialization_alias="practicedAt")
    result: PracticeResult
    confidence: int | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class PracticeSessionDetailResponse(PracticeSessionSummaryResponse):
    notes: str | None


class LanguageLearningBuddyDashboardResponse(BaseModel):
    vocabulary: list[VocabularySummaryResponse]
    sessions: list[PracticeSessionSummaryResponse]
    vocabulary_count: int = Field(serialization_alias="vocabularyCount")
    language_count: int = Field(serialization_alias="languageCount")
    practice_count: int = Field(serialization_alias="practiceCount")
    mastered_count: int = Field(serialization_alias="masteredCount")
    recent_sessions: list[PracticeSessionSummaryResponse] = Field(serialization_alias="recentSessions")
    weekly_practice_count: int = Field(serialization_alias="weeklyPracticeCount")


class PaginatedVocabularyResponse(BaseModel):
    items: list[VocabularySummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int


class PaginatedPracticeSessionResponse(BaseModel):
    items: list[PracticeSessionSummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int
