from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BookStatus = Literal["draft", "ready", "summarizing", "reviewed", "archived"]
SourceType = Literal["manual", "chapter", "notes", "excerpt"]
SummaryStatus = Literal["draft", "review", "complete", "archived"]
SummaryType = Literal["chapter", "full-book", "topic", "study"]
NoteType = Literal["note", "highlight", "observation", "question"]
HistoryEventType = Literal["created", "generated", "edited", "reviewed", "note-added", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class BookCollectionCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    author: str | None = Field(default=None, max_length=180)
    category: str | None = Field(default=None, max_length=120)
    source_type: SourceType = Field(default="manual", alias="sourceType")
    status: BookStatus = "draft"
    source_text: str | None = Field(default=None, alias="sourceText", max_length=20000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BookCollectionUpdateRequest(BookCollectionCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    source_type: SourceType | None = Field(default=None, alias="sourceType")
    status: BookStatus | None = None


class BookSummaryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    book_id: int = Field(alias="bookId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    summary_type: SummaryType = Field(default="chapter", alias="summaryType")
    status: SummaryStatus = "draft"
    summary_text: str | None = Field(default=None, alias="summaryText", max_length=10000)
    key_points: str | None = Field(default=None, alias="keyPoints", max_length=6000)
    action_items: str | None = Field(default=None, alias="actionItems", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BookSummaryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    summary_type: SummaryType | None = Field(default=None, alias="summaryType")
    status: SummaryStatus | None = None
    summary_text: str | None = Field(default=None, alias="summaryText", max_length=10000)
    key_points: str | None = Field(default=None, alias="keyPoints", max_length=6000)
    action_items: str | None = Field(default=None, alias="actionItems", max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SummaryNoteCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    summary_id: int = Field(alias="summaryId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    note_type: NoteType = Field(default="note", alias="noteType")
    content: str | None = Field(default=None, max_length=6000)
    highlight: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SummaryNoteUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    note_type: NoteType | None = Field(default=None, alias="noteType")
    content: str | None = Field(default=None, max_length=6000)
    highlight: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SummaryHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    summary_id: int = Field(alias="summaryId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    description: str | None = Field(default=None, max_length=5000)
    revision_notes: str | None = Field(default=None, alias="revisionNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SummaryHistoryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    event_type: HistoryEventType | None = Field(default=None, alias="eventType")
    occurred_at: str | None = Field(default=None, alias="occurredAt", max_length=40)
    description: str | None = Field(default=None, max_length=5000)
    revision_notes: str | None = Field(default=None, alias="revisionNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BookCollectionSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    author: str | None
    category: str | None
    source_type: SourceType = Field(serialization_alias="sourceType")
    status: BookStatus
    source_preview: str | None = Field(serialization_alias="sourcePreview")
    summary_count: int = Field(serialization_alias="summaryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class BookCollectionDetailResponse(BookCollectionSummaryResponse):
    source_text: str | None = Field(serialization_alias="sourceText")
    notes: str | None


class BookSummarySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    book_id: int = Field(serialization_alias="bookId")
    book_title: str = Field(serialization_alias="bookTitle")
    title: str
    summary_type: SummaryType = Field(serialization_alias="summaryType")
    status: SummaryStatus
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    note_count: int = Field(serialization_alias="noteCount")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class BookSummaryDetailResponse(BookSummarySummaryResponse):
    summary_text: str | None = Field(serialization_alias="summaryText")
    key_points: str | None = Field(serialization_alias="keyPoints")
    action_items: str | None = Field(serialization_alias="actionItems")


class SummaryNoteSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    summary_id: int = Field(serialization_alias="summaryId")
    summary_title: str = Field(serialization_alias="summaryTitle")
    title: str
    note_type: NoteType = Field(serialization_alias="noteType")
    content_preview: str | None = Field(serialization_alias="contentPreview")
    highlight_preview: str | None = Field(serialization_alias="highlightPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SummaryNoteDetailResponse(SummaryNoteSummaryResponse):
    content: str | None
    highlight: str | None


class SummaryHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    summary_id: int = Field(serialization_alias="summaryId")
    summary_title: str = Field(serialization_alias="summaryTitle")
    title: str
    event_type: HistoryEventType | None = Field(serialization_alias="eventType")
    occurred_at: str | None = Field(serialization_alias="occurredAt")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    revision_notes_preview: str | None = Field(serialization_alias="revisionNotesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SummaryHistoryDetailResponse(SummaryHistorySummaryResponse):
    description: str | None
    revision_notes: str | None = Field(serialization_alias="revisionNotes")


class BookSummaryGeneratorDashboardResponse(BaseModel):
    books: list[BookCollectionSummaryResponse]
    summaries: list[BookSummarySummaryResponse]
    notes: list[SummaryNoteSummaryResponse]
    history: list[SummaryHistorySummaryResponse]
    book_count: int = Field(serialization_alias="bookCount")
    summary_count: int = Field(serialization_alias="summaryCount")
    note_count: int = Field(serialization_alias="noteCount")
    history_count: int = Field(serialization_alias="historyCount")
    reviewed_book_count: int = Field(serialization_alias="reviewedBookCount")
    completed_summary_count: int = Field(serialization_alias="completedSummaryCount")

    model_config = ConfigDict(from_attributes=True)
