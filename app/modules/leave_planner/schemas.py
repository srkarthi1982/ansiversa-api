from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LeaveDayType = Literal["full_day", "first_half", "second_half"]
LeaveStatus = Literal["planned", "pending", "approved", "taken", "cancelled", "rejected"]
LeavePeriod = Literal["all", "upcoming", "current", "past"]
ColorKey = Literal["blue", "green", "amber", "violet", "rose", "slate"]

def _clean(value):
    if isinstance(value, str):
        value = " ".join(value.strip().split()); return value or None
    return value

class LeavePlannerTypeWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    code: str | None = Field(default=None, max_length=30)
    description: str | None = Field(default=None, max_length=3000)
    annual_allowance_days: float = Field(default=0, alias="annualAllowanceDays", ge=0, le=1000)
    carry_forward_days: float = Field(default=0, alias="carryForwardDays", ge=0, le=1000)
    color_key: ColorKey = Field(default="blue", alias="colorKey")
    is_active: bool = Field(default=True, alias="isActive")
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    @field_validator("name", "code", "description", mode="before")
    @classmethod
    def clean(cls, value): return _clean(value)

class LeavePlannerTypeCreateRequest(LeavePlannerTypeWrite): pass
class LeavePlannerTypeUpdateRequest(LeavePlannerTypeWrite): pass

class LeavePlannerEntryWrite(BaseModel):
    leave_type_id: str = Field(alias="leaveTypeId", min_length=1, max_length=36)
    title: str = Field(min_length=1, max_length=180)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    day_type: LeaveDayType = Field(default="full_day", alias="dayType")
    status: LeaveStatus = "planned"
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    @field_validator("title", "reason", "notes", mode="before")
    @classmethod
    def clean(cls, value): return _clean(value)
    @model_validator(mode="after")
    def dates(self):
        if self.end_date < self.start_date: raise ValueError("End date must be on or after start date.")
        if self.day_type != "full_day" and self.end_date != self.start_date: raise ValueError("Half-day leave must start and end on the same date.")
        return self

class LeavePlannerEntryCreateRequest(LeavePlannerEntryWrite): pass
class LeavePlannerEntryUpdateRequest(LeavePlannerEntryWrite): pass

class LeavePlannerTypeResponse(LeavePlannerTypeWrite):
    id: str; used_days: float = Field(serialization_alias="usedDays"); planned_days: float = Field(serialization_alias="plannedDays"); remaining_days: float = Field(serialization_alias="remainingDays"); entry_count: int = Field(serialization_alias="entryCount"); created_at: datetime = Field(serialization_alias="createdAt"); updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LeavePlannerEntryResponse(LeavePlannerEntryWrite):
    id: str; leave_type_name: str = Field(serialization_alias="leaveTypeName"); duration_days: float = Field(serialization_alias="durationDays"); created_at: datetime = Field(serialization_alias="createdAt"); updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LeavePlannerEntryListResponse(BaseModel):
    items: list[LeavePlannerEntryResponse]; total: int; page: int; page_size: int = Field(serialization_alias="pageSize"); pages: int

class LeavePlannerDashboardResponse(BaseModel):
    total_allowance: float = Field(serialization_alias="totalAllowance"); used_leave: float = Field(serialization_alias="usedLeave"); planned_leave: float = Field(serialization_alias="plannedLeave"); remaining_leave: float = Field(serialization_alias="remainingLeave"); upcoming_count: int = Field(serialization_alias="upcomingCount")
