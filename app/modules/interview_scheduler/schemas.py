from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SchedulePriority = Literal["low", "medium", "high", "urgent"]
ScheduleStatus = Literal["planned", "scheduled", "completed", "cancelled", "archived"]
RoundStatus = Literal["planned", "scheduled", "completed", "cancelled"]
EventType = Literal["interview", "reminder", "follow-up", "preparation"]
HistoryOutcome = Literal["advanced", "rejected", "offer", "hold", "withdrawn", "completed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class InterviewScheduleCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    candidate_name: str = Field(alias="candidateName", min_length=1, max_length=180)
    role_title: str = Field(alias="roleTitle", min_length=1, max_length=180)
    company_name: str | None = Field(default=None, alias="companyName", max_length=180)
    interview_stage: str | None = Field(default=None, alias="interviewStage", max_length=120)
    status: ScheduleStatus = "planned"
    priority: SchedulePriority = "medium"
    target_date: str | None = Field(default=None, alias="targetDate", max_length=40)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewScheduleUpdateRequest(InterviewScheduleCreateRequest):
    candidate_name: str | None = Field(default=None, alias="candidateName", min_length=1, max_length=180)
    role_title: str | None = Field(default=None, alias="roleTitle", min_length=1, max_length=180)
    status: ScheduleStatus | None = None
    priority: SchedulePriority | None = None


class InterviewRoundCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int = Field(alias="scheduleId", gt=0)
    round_name: str = Field(alias="roundName", min_length=1, max_length=180)
    interviewer_name: str | None = Field(default=None, alias="interviewerName", max_length=180)
    interview_type: str | None = Field(default=None, alias="interviewType", max_length=120)
    sequence: int = Field(default=1, ge=1, le=20)
    status: RoundStatus = "planned"
    scheduled_at: str | None = Field(default=None, alias="scheduledAt", max_length=40)
    location: str | None = Field(default=None, max_length=240)
    preparation_notes: str | None = Field(default=None, alias="preparationNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "round_name", "interviewer_name", "interview_type", "scheduled_at", "location", "preparation_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewRoundUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int | None = Field(default=None, alias="scheduleId", gt=0)
    round_name: str | None = Field(default=None, alias="roundName", min_length=1, max_length=180)
    interviewer_name: str | None = Field(default=None, alias="interviewerName", max_length=180)
    interview_type: str | None = Field(default=None, alias="interviewType", max_length=120)
    sequence: int | None = Field(default=None, ge=1, le=20)
    status: RoundStatus | None = None
    scheduled_at: str | None = Field(default=None, alias="scheduledAt", max_length=40)
    location: str | None = Field(default=None, max_length=240)
    preparation_notes: str | None = Field(default=None, alias="preparationNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "round_name", "interviewer_name", "interview_type", "scheduled_at", "location", "preparation_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewCalendarEventCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int = Field(alias="scheduleId", gt=0)
    round_id: int | None = Field(default=None, alias="roundId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    event_type: EventType = Field(default="interview", alias="eventType")
    starts_at: str = Field(alias="startsAt", min_length=1, max_length=40)
    ends_at: str | None = Field(default=None, alias="endsAt", max_length=40)
    reminder_minutes: int | None = Field(default=None, alias="reminderMinutes", ge=0, le=10080)
    location: str | None = Field(default=None, max_length=240)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "starts_at", "ends_at", "location", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewCalendarEventUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int | None = Field(default=None, alias="scheduleId", gt=0)
    round_id: int | None = Field(default=None, alias="roundId", gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    event_type: EventType | None = Field(default=None, alias="eventType")
    starts_at: str | None = Field(default=None, alias="startsAt", min_length=1, max_length=40)
    ends_at: str | None = Field(default=None, alias="endsAt", max_length=40)
    reminder_minutes: int | None = Field(default=None, alias="reminderMinutes", ge=0, le=10080)
    location: str | None = Field(default=None, max_length=240)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "starts_at", "ends_at", "location", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewHistoryCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int = Field(alias="scheduleId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    outcome: HistoryOutcome | None = None
    completed_at: str | None = Field(default=None, alias="completedAt", max_length=40)
    summary: str | None = Field(default=None, max_length=5000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "completed_at", "summary", "next_steps", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewHistoryUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    schedule_id: int | None = Field(default=None, alias="scheduleId", gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    outcome: HistoryOutcome | None = None
    completed_at: str | None = Field(default=None, alias="completedAt", max_length=40)
    summary: str | None = Field(default=None, max_length=5000)
    next_steps: str | None = Field(default=None, alias="nextSteps", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "title", "completed_at", "summary", "next_steps", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class InterviewScheduleSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    candidate_name: str = Field(serialization_alias="candidateName")
    role_title: str = Field(serialization_alias="roleTitle")
    company_name: str | None = Field(serialization_alias="companyName")
    interview_stage: str | None = Field(serialization_alias="interviewStage")
    status: ScheduleStatus
    priority: SchedulePriority
    target_date: str | None = Field(serialization_alias="targetDate")
    round_count: int = Field(serialization_alias="roundCount")
    event_count: int = Field(serialization_alias="eventCount")
    history_count: int = Field(serialization_alias="historyCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewScheduleDetailResponse(InterviewScheduleSummaryResponse):
    notes: str | None


class InterviewRoundSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    schedule_id: int = Field(serialization_alias="scheduleId")
    schedule_title: str = Field(serialization_alias="scheduleTitle")
    round_name: str = Field(serialization_alias="roundName")
    interviewer_name: str | None = Field(serialization_alias="interviewerName")
    interview_type: str | None = Field(serialization_alias="interviewType")
    sequence: int
    status: RoundStatus
    scheduled_at: str | None = Field(serialization_alias="scheduledAt")
    location: str | None
    preparation_preview: str | None = Field(serialization_alias="preparationPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewRoundDetailResponse(InterviewRoundSummaryResponse):
    preparation_notes: str | None = Field(serialization_alias="preparationNotes")


class InterviewCalendarEventSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    schedule_id: int = Field(serialization_alias="scheduleId")
    schedule_title: str = Field(serialization_alias="scheduleTitle")
    round_id: int | None = Field(serialization_alias="roundId")
    round_name: str | None = Field(serialization_alias="roundName")
    title: str
    event_type: EventType = Field(serialization_alias="eventType")
    starts_at: str = Field(serialization_alias="startsAt")
    ends_at: str | None = Field(serialization_alias="endsAt")
    reminder_minutes: int | None = Field(serialization_alias="reminderMinutes")
    location: str | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewCalendarEventDetailResponse(InterviewCalendarEventSummaryResponse):
    notes: str | None


class InterviewHistorySummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    schedule_id: int = Field(serialization_alias="scheduleId")
    schedule_title: str = Field(serialization_alias="scheduleTitle")
    title: str
    outcome: HistoryOutcome | None
    completed_at: str | None = Field(serialization_alias="completedAt")
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    next_steps_preview: str | None = Field(serialization_alias="nextStepsPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class InterviewHistoryDetailResponse(InterviewHistorySummaryResponse):
    summary: str | None
    next_steps: str | None = Field(serialization_alias="nextSteps")


class InterviewSchedulerDashboardResponse(BaseModel):
    schedules: list[InterviewScheduleSummaryResponse]
    rounds: list[InterviewRoundSummaryResponse]
    calendar_events: list[InterviewCalendarEventSummaryResponse] = Field(serialization_alias="calendarEvents")
    history: list[InterviewHistorySummaryResponse]
    schedule_count: int = Field(serialization_alias="scheduleCount")
    round_count: int = Field(serialization_alias="roundCount")
    calendar_event_count: int = Field(serialization_alias="calendarEventCount")
    history_count: int = Field(serialization_alias="historyCount")
    scheduled_count: int = Field(serialization_alias="scheduledCount")
    completed_count: int = Field(serialization_alias="completedCount")

    model_config = ConfigDict(from_attributes=True)
