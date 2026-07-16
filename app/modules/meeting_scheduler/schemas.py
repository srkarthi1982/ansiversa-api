from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

MeetingType = Literal["in_person", "online", "hybrid", "phone"]
MeetingStatus = Literal["draft", "scheduled", "completed", "cancelled"]
ResponseStatus = Literal["pending", "accepted", "declined", "tentative"]
AgendaStatus = Literal["pending", "discussed", "deferred", "completed"]
MeetingPeriod = Literal["all", "upcoming", "past"]


def _clean(value: object) -> object:
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class MeetingWrite(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    meeting_date: date = Field(alias="meetingDate")
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    timezone: str = Field(min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=300)
    meeting_type: MeetingType = Field(alias="meetingType")
    status: MeetingStatus = "scheduled"
    notes: str | None = Field(default=None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "timezone", "location", "notes", mode="before")
    @classmethod
    def clean_text(cls, value: object) -> object:
        return _clean(value)

    @model_validator(mode="after")
    def valid_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be later than start time.")
        return self


class MeetingSchedulerMeetingCreateRequest(MeetingWrite):
    pass


class MeetingSchedulerMeetingUpdateRequest(MeetingWrite):
    pass


class ParticipantWrite(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: EmailStr | None = None
    role: str | None = Field(default=None, max_length=120)
    response_status: ResponseStatus = Field(default="pending", alias="responseStatus")
    notes: str | None = Field(default=None, max_length=3000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "role", "notes", mode="before")
    @classmethod
    def clean_text(cls, value: object) -> object:
        return _clean(value)


class MeetingSchedulerParticipantCreateRequest(ParticipantWrite):
    pass


class MeetingSchedulerParticipantUpdateRequest(ParticipantWrite):
    pass


class AgendaItemWrite(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    duration_minutes: int = Field(default=15, alias="durationMinutes", ge=1, le=1440)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=9999)
    status: AgendaStatus = "pending"
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", mode="before")
    @classmethod
    def clean_text(cls, value: object) -> object:
        return _clean(value)


class MeetingSchedulerAgendaItemCreateRequest(AgendaItemWrite):
    pass


class MeetingSchedulerAgendaItemUpdateRequest(AgendaItemWrite):
    pass


class MeetingSchedulerParticipantResponse(ParticipantWrite):
    id: str
    meeting_id: str = Field(serialization_alias="meetingId")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MeetingSchedulerAgendaItemResponse(AgendaItemWrite):
    id: str
    meeting_id: str = Field(serialization_alias="meetingId")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MeetingSchedulerMeetingResponse(MeetingWrite):
    id: str
    participant_count: int = Field(default=0, serialization_alias="participantCount")
    agenda_item_count: int = Field(default=0, serialization_alias="agendaItemCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MeetingSchedulerMeetingDetailResponse(MeetingSchedulerMeetingResponse):
    participants: list[MeetingSchedulerParticipantResponse]
    agenda_items: list[MeetingSchedulerAgendaItemResponse] = Field(serialization_alias="agendaItems")


class MeetingSchedulerMeetingListResponse(BaseModel):
    items: list[MeetingSchedulerMeetingResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    pages: int


class MeetingSchedulerDashboardResponse(BaseModel):
    total_meetings: int = Field(serialization_alias="totalMeetings")
    upcoming_meetings: int = Field(serialization_alias="upcomingMeetings")
    completed_meetings: int = Field(serialization_alias="completedMeetings")
    pending_responses: int = Field(serialization_alias="pendingResponses")
