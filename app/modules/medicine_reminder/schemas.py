from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MedicineStatus = Literal["active", "paused", "completed", "archived"]
MedicineForm = Literal["tablet", "capsule", "liquid", "injection", "drops", "inhaler", "other"]
ScheduleStatus = Literal["active", "paused", "archived"]
ScheduleFrequency = Literal["daily", "weekdays", "weekly", "asNeeded", "custom"]
DoseLogStatus = Literal["taken", "missed", "skipped", "late"]
NoteCategory = Literal["general", "sideEffect", "doctor", "refill", "question"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class MedicineCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    dosage: str | None = Field(default=None, max_length=120)
    form: MedicineForm = "tablet"
    purpose: str | None = Field(default=None, max_length=180)
    instructions: str | None = Field(default=None, max_length=4000)
    prescribing_doctor: str | None = Field(default=None, alias="prescribingDoctor", max_length=120)
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    end_date: str | None = Field(default=None, alias="endDate", max_length=40)
    status: MedicineStatus = "active"
    refill_quantity: int | None = Field(default=None, alias="refillQuantity", ge=0, le=100000)
    refill_reminder_date: str | None = Field(default=None, alias="refillReminderDate", max_length=40)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MedicineUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    dosage: str | None = Field(default=None, max_length=120)
    form: MedicineForm | None = None
    purpose: str | None = Field(default=None, max_length=180)
    instructions: str | None = Field(default=None, max_length=4000)
    prescribing_doctor: str | None = Field(default=None, alias="prescribingDoctor", max_length=120)
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    end_date: str | None = Field(default=None, alias="endDate", max_length=40)
    status: MedicineStatus | None = None
    refill_quantity: int | None = Field(default=None, alias="refillQuantity", ge=0, le=100000)
    refill_reminder_date: str | None = Field(default=None, alias="refillReminderDate", max_length=40)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ScheduleCreateRequest(BaseModel):
    medicine_id: str = Field(alias="medicineId", min_length=1, max_length=36)
    label: str = Field(min_length=1, max_length=120)
    time_of_day: str = Field(alias="timeOfDay", min_length=1, max_length=20)
    frequency: ScheduleFrequency = "daily"
    days_of_week: str | None = Field(default=None, alias="daysOfWeek", max_length=80)
    dose_amount: str | None = Field(default=None, alias="doseAmount", max_length=80)
    instructions: str | None = Field(default=None, max_length=4000)
    status: ScheduleStatus = "active"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ScheduleUpdateRequest(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=120)
    time_of_day: str | None = Field(default=None, alias="timeOfDay", min_length=1, max_length=20)
    frequency: ScheduleFrequency | None = None
    days_of_week: str | None = Field(default=None, alias="daysOfWeek", max_length=80)
    dose_amount: str | None = Field(default=None, alias="doseAmount", max_length=80)
    instructions: str | None = Field(default=None, max_length=4000)
    status: ScheduleStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class DoseLogCreateRequest(BaseModel):
    medicine_id: str = Field(alias="medicineId", min_length=1, max_length=36)
    schedule_id: str | None = Field(default=None, alias="scheduleId", max_length=36)
    scheduled_for: str = Field(alias="scheduledFor", min_length=1, max_length=40)
    taken_at: str | None = Field(default=None, alias="takenAt", max_length=40)
    status: DoseLogStatus = "taken"
    note: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class DoseLogUpdateRequest(BaseModel):
    scheduled_for: str | None = Field(default=None, alias="scheduledFor", min_length=1, max_length=40)
    taken_at: str | None = Field(default=None, alias="takenAt", max_length=40)
    status: DoseLogStatus | None = None
    note: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MedicineReminderNoteCreateRequest(BaseModel):
    medicine_id: str = Field(alias="medicineId", min_length=1, max_length=36)
    note_date: str = Field(alias="noteDate", min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=4000)
    category: NoteCategory = "general"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MedicineReminderNoteUpdateRequest(BaseModel):
    note_date: str | None = Field(default=None, alias="noteDate", min_length=1, max_length=40)
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=4000)
    category: NoteCategory | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MedicineSummaryResponse(BaseModel):
    id: str
    name: str
    dosage: str | None
    form: MedicineForm
    purpose: str | None
    instructions_preview: str | None = Field(serialization_alias="instructionsPreview")
    prescribing_doctor: str | None = Field(serialization_alias="prescribingDoctor")
    start_date: str | None = Field(serialization_alias="startDate")
    end_date: str | None = Field(serialization_alias="endDate")
    status: MedicineStatus
    refill_quantity: int | None = Field(serialization_alias="refillQuantity")
    refill_reminder_date: str | None = Field(serialization_alias="refillReminderDate")
    schedule_count: int = Field(serialization_alias="scheduleCount")
    active_schedule_count: int = Field(serialization_alias="activeScheduleCount")
    dose_log_count: int = Field(serialization_alias="doseLogCount")
    last_taken_at: str | None = Field(serialization_alias="lastTakenAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ScheduleSummaryResponse(BaseModel):
    id: str
    medicine_id: str = Field(serialization_alias="medicineId")
    medicine_name: str = Field(serialization_alias="medicineName")
    label: str
    time_of_day: str = Field(serialization_alias="timeOfDay")
    frequency: ScheduleFrequency
    days_of_week: str | None = Field(serialization_alias="daysOfWeek")
    dose_amount: str | None = Field(serialization_alias="doseAmount")
    instructions_preview: str | None = Field(serialization_alias="instructionsPreview")
    status: ScheduleStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class DoseLogSummaryResponse(BaseModel):
    id: str
    medicine_id: str = Field(serialization_alias="medicineId")
    medicine_name: str = Field(serialization_alias="medicineName")
    schedule_id: str | None = Field(serialization_alias="scheduleId")
    schedule_label: str | None = Field(serialization_alias="scheduleLabel")
    scheduled_for: str = Field(serialization_alias="scheduledFor")
    taken_at: str | None = Field(serialization_alias="takenAt")
    status: DoseLogStatus
    note_preview: str | None = Field(serialization_alias="notePreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MedicineReminderNoteSummaryResponse(BaseModel):
    id: str
    medicine_id: str = Field(serialization_alias="medicineId")
    medicine_name: str = Field(serialization_alias="medicineName")
    note_date: str = Field(serialization_alias="noteDate")
    title: str
    body_preview: str | None = Field(serialization_alias="bodyPreview")
    category: NoteCategory
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MedicineDetailResponse(MedicineSummaryResponse):
    instructions: str | None
    schedules: list[ScheduleSummaryResponse]
    dose_logs: list[DoseLogSummaryResponse] = Field(serialization_alias="doseLogs")
    notes: list[MedicineReminderNoteSummaryResponse]


class ScheduleDetailResponse(ScheduleSummaryResponse):
    instructions: str | None


class DoseLogDetailResponse(DoseLogSummaryResponse):
    note: str | None


class MedicineReminderNoteDetailResponse(MedicineReminderNoteSummaryResponse):
    body: str | None


class MedicineReminderDashboardResponse(BaseModel):
    medicines: list[MedicineSummaryResponse]
    schedules: list[ScheduleSummaryResponse]
    dose_logs: list[DoseLogSummaryResponse] = Field(serialization_alias="doseLogs")
    notes: list[MedicineReminderNoteSummaryResponse]
    active_medicine_count: int = Field(serialization_alias="activeMedicineCount")
    active_schedule_count: int = Field(serialization_alias="activeScheduleCount")
    doses_logged_this_week: int = Field(serialization_alias="dosesLoggedThisWeek")
    missed_dose_count: int = Field(serialization_alias="missedDoseCount")
    refill_watch_count: int = Field(serialization_alias="refillWatchCount")
    recent_dose_logs: list[DoseLogSummaryResponse] = Field(serialization_alias="recentDoseLogs")
