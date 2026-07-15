from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

ArchiveFilter = Literal["active", "archived", "all"]
TaskSort = Literal["due", "priority", "title", "created", "updated", "cost"]
TaskTimeFilter = Literal["all", "today", "week", "month", "overdue", "completed"]
Priority = Literal["low", "medium", "high", "urgent"]
RecurrenceType = Literal["one_time", "weekly", "monthly", "quarterly", "six_monthly", "yearly", "custom"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


def _normalize_currency(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized or "USD"
    return value


def _validate_phone(value: str | None) -> str | None:
    if value is None:
        return None
    allowed = set("0123456789+()-. xX")
    if sum(1 for character in value if character.isdigit()) < 3 or any(character not in allowed for character in value):
        raise ValueError("phone must be a valid phone value.")
    return value


class MaintenanceLookupCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MaintenanceLookupUpdateRequest(MaintenanceLookupCreateRequest):
    pass


class MaintenanceLookupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    task_count: int = Field(serialization_alias="taskCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MaintenanceTaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    area_id: str = Field(alias="areaId", min_length=1, max_length=36)
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    description: str | None = Field(default=None, max_length=5000)
    due_date: date = Field(alias="dueDate")
    recurrence_type: RecurrenceType = Field(default="one_time", alias="recurrenceType")
    recurrence_interval: int | None = Field(default=None, alias="recurrenceInterval", ge=1, le=3650)
    priority: Priority = "medium"
    estimated_cost: Decimal | None = Field(default=None, alias="estimatedCost", ge=0, max_digits=12, decimal_places=2)
    actual_cost: Decimal | None = Field(default=None, alias="actualCost", ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    provider_name: str | None = Field(default=None, alias="providerName", max_length=180)
    provider_phone: str | None = Field(default=None, alias="providerPhone", max_length=60)
    provider_email: EmailStr | None = Field(default=None, alias="providerEmail", max_length=180)
    reference_number: str | None = Field(default=None, alias="referenceNumber", max_length=120)
    notes: str | None = Field(default=None, max_length=5000)
    completion_notes: str | None = Field(default=None, alias="completionNotes", max_length=5000)
    reminder_lead_days: int = Field(default=3, alias="reminderLeadDays", ge=0, le=365)
    archived: bool = False

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "provider_name", "provider_phone", "reference_number", "notes", "completion_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        return _normalize_currency(value)

    @field_validator("provider_phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return _validate_phone(value)

    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.recurrence_type != "custom" and self.recurrence_interval is not None:
            raise ValueError("recurrenceInterval is only allowed for custom recurrence.")
        if self.recurrence_type == "custom" and self.recurrence_interval is None:
            raise ValueError("custom recurrence requires recurrenceInterval.")
        return self


class MaintenanceTaskUpdateRequest(MaintenanceTaskCreateRequest):
    pass


class CompletionRequest(BaseModel):
    actual_cost: Decimal | None = Field(default=None, alias="actualCost", ge=0, max_digits=12, decimal_places=2)
    completion_notes: str | None = Field(default=None, alias="completionNotes", max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("completion_notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MaintenanceTaskSummaryResponse(BaseModel):
    id: str
    title: str
    area_id: str = Field(serialization_alias="areaId")
    area_name: str = Field(serialization_alias="areaName")
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    due_date: date = Field(serialization_alias="dueDate")
    recurrence_type: str = Field(serialization_alias="recurrenceType")
    recurrence_interval: int | None = Field(serialization_alias="recurrenceInterval")
    priority: str
    status: str
    days_remaining: int = Field(serialization_alias="daysRemaining")
    due_soon: bool = Field(serialization_alias="dueSoon")
    overdue: bool
    estimated_cost: Decimal | None = Field(serialization_alias="estimatedCost")
    actual_cost: Decimal | None = Field(serialization_alias="actualCost")
    currency: str
    provider_name: str | None = Field(serialization_alias="providerName")
    completed_at: datetime | None = Field(serialization_alias="completedAt")
    archived: bool
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MaintenanceTaskDetailResponse(MaintenanceTaskSummaryResponse):
    description: str | None
    provider_phone: str | None = Field(serialization_alias="providerPhone")
    provider_email: str | None = Field(serialization_alias="providerEmail")
    reference_number: str | None = Field(serialization_alias="referenceNumber")
    notes: str | None
    completion_notes: str | None = Field(serialization_alias="completionNotes")
    reminder_lead_days: int = Field(serialization_alias="reminderLeadDays")
    completion_count: int = Field(serialization_alias="completionCount")


class CountItem(BaseModel):
    label: str
    count: int


class CostSummary(BaseModel):
    estimated_total: Decimal = Field(serialization_alias="estimatedTotal")
    actual_total: Decimal = Field(serialization_alias="actualTotal")
    currency: str


class DashboardResponse(BaseModel):
    total_active_tasks: int = Field(serialization_alias="totalActiveTasks")
    due_today: int = Field(serialization_alias="dueToday")
    due_this_week: int = Field(serialization_alias="dueThisWeek")
    overdue_tasks: int = Field(serialization_alias="overdueTasks")
    completed_this_month: int = Field(serialization_alias="completedThisMonth")
    upcoming_tasks: int = Field(serialization_alias="upcomingTasks")
    archived_tasks: int = Field(serialization_alias="archivedTasks")
    estimated_total: Decimal = Field(serialization_alias="estimatedTotal")
    actual_total: Decimal = Field(serialization_alias="actualTotal")


class InsightsResponse(DashboardResponse):
    areas: list[MaintenanceLookupResponse]
    categories: list[MaintenanceLookupResponse]
    tasks_by_area: list[CountItem] = Field(serialization_alias="tasksByArea")
    tasks_by_category: list[CountItem] = Field(serialization_alias="tasksByCategory")
    tasks_by_priority: list[CountItem] = Field(serialization_alias="tasksByPriority")
    cost_summary: CostSummary = Field(serialization_alias="costSummary")
    recently_completed: list[MaintenanceTaskSummaryResponse] = Field(serialization_alias="recentlyCompleted")
    upcoming: list[MaintenanceTaskSummaryResponse]
    overdue: list[MaintenanceTaskSummaryResponse]

