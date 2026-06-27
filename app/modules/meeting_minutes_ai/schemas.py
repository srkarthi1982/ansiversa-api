from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MeetingStatus = Literal["draft", "capturing", "reviewed"]
MeetingNoteType = Literal["notes", "transcript"]
MeetingActionStatus = Literal["open", "inProgress", "done"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class MeetingCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    meeting_date: date | None = Field(default=None, alias="meetingDate")
    participants: str | None = Field(default=None, max_length=3000)
    context: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "participants", "context", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    meeting_date: date | None = Field(default=None, alias="meetingDate")
    participants: str | None = Field(default=None, max_length=3000)
    context: str | None = Field(default=None, max_length=3000)
    status: MeetingStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "participants", "context", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingNoteCreateRequest(BaseModel):
    meeting_id: int = Field(alias="meetingId", gt=0)
    note_type: MeetingNoteType = Field(default="notes", alias="noteType")
    content: str = Field(min_length=1, max_length=20000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingNoteUpdateRequest(BaseModel):
    note_type: MeetingNoteType | None = Field(default=None, alias="noteType")
    content: str | None = Field(default=None, min_length=1, max_length=20000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingActionItemCreateRequest(BaseModel):
    meeting_id: int = Field(alias="meetingId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    owner_name: str | None = Field(default=None, alias="ownerName", max_length=140)
    due_date: date | None = Field(default=None, alias="dueDate")
    status: MeetingActionStatus = "open"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "owner_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingActionItemUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    owner_name: str | None = Field(default=None, alias="ownerName", max_length=140)
    due_date: date | None = Field(default=None, alias="dueDate")
    status: MeetingActionStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "owner_name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingSummaryCreateRequest(BaseModel):
    meeting_id: int = Field(alias="meetingId", gt=0)
    summary_text: str = Field(alias="summaryText", min_length=1, max_length=8000)
    decisions: str | None = Field(default=None, max_length=5000)
    risks: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("summary_text", "decisions", "risks", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingSummaryUpdateRequest(BaseModel):
    summary_text: str | None = Field(default=None, alias="summaryText", min_length=1, max_length=8000)
    decisions: str | None = Field(default=None, max_length=5000)
    risks: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("summary_text", "decisions", "risks", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MeetingResponse(BaseModel):
    id: int
    title: str
    meeting_date: date | None = Field(serialization_alias="meetingDate")
    participants: str | None
    context: str | None
    status: MeetingStatus
    note_count: int = Field(serialization_alias="noteCount")
    action_item_count: int = Field(serialization_alias="actionItemCount")
    summary_count: int = Field(serialization_alias="summaryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class MeetingNoteResponse(BaseModel):
    id: int
    meeting_id: int = Field(serialization_alias="meetingId")
    meeting_title: str = Field(serialization_alias="meetingTitle")
    note_type: MeetingNoteType = Field(serialization_alias="noteType")
    content: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class MeetingActionItemResponse(BaseModel):
    id: int
    meeting_id: int = Field(serialization_alias="meetingId")
    meeting_title: str = Field(serialization_alias="meetingTitle")
    title: str
    owner_name: str | None = Field(serialization_alias="ownerName")
    due_date: date | None = Field(serialization_alias="dueDate")
    status: MeetingActionStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class MeetingSummaryResponse(BaseModel):
    id: int
    meeting_id: int = Field(serialization_alias="meetingId")
    meeting_title: str = Field(serialization_alias="meetingTitle")
    summary_text: str = Field(serialization_alias="summaryText")
    decisions: str | None
    risks: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class MeetingMinutesDashboardResponse(BaseModel):
    meetings: list[MeetingResponse]
    notes: list[MeetingNoteResponse]
    action_items: list[MeetingActionItemResponse] = Field(serialization_alias="actionItems")
    summaries: list[MeetingSummaryResponse]
    open_action_count: int = Field(serialization_alias="openActionCount")
    reviewed_meeting_count: int = Field(serialization_alias="reviewedMeetingCount")
    transcript_count: int = Field(serialization_alias="transcriptCount")
