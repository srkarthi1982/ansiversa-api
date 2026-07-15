from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

WaterUnit = Literal['ml', 'L']
EntrySort = Literal['date', 'amount', 'drink_type', 'created']
SummaryRange = Literal['week', 'month']

class CountItem(BaseModel):
    label: str
    count: int

class AmountItem(BaseModel):
    label: str
    amount: Decimal
    count: int = 0

class DaySummary(BaseModel):
    date: date
    total_amount: Decimal = Field(serialization_alias='totalAmount')
    entry_count: int = Field(serialization_alias='entryCount')
    goal_achieved: bool = Field(serialization_alias='goalAchieved')

class GoalRequest(BaseModel):
    daily_goal: Decimal = Field(alias='dailyGoal', gt=0, max_digits=12, decimal_places=2)
    preferred_unit: WaterUnit = Field(default='ml', alias='preferredUnit')
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

class GoalResponse(BaseModel):
    id: str
    daily_goal: Decimal = Field(serialization_alias='dailyGoal')
    preferred_unit: WaterUnit = Field(serialization_alias='preferredUnit')
    daily_goal_ml: Decimal = Field(serialization_alias='dailyGoalMl')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class EntryCreateRequest(BaseModel):
    entry_date: date = Field(alias='entryDate')
    entry_time: time = Field(alias='entryTime')
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    unit: WaterUnit = 'ml'
    drink_type: str = Field(default='Water', alias='drinkType', min_length=1, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    @field_validator('drink_type', 'notes', mode='before')
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = ' '.join(value.strip().split())
            return normalized or None
        return value

class EntryUpdateRequest(EntryCreateRequest):
    pass

class EntrySummaryResponse(BaseModel):
    id: str
    entry_date: date = Field(serialization_alias='entryDate')
    entry_time: time = Field(serialization_alias='entryTime')
    amount: Decimal
    unit: WaterUnit
    amount_ml: Decimal = Field(serialization_alias='amountMl')
    drink_type: str = Field(serialization_alias='drinkType')
    notes_preview: str | None = Field(serialization_alias='notesPreview')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class EntryDetailResponse(EntrySummaryResponse):
    notes: str | None

class EntryListResponse(BaseModel):
    items: list[EntrySummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias='pageSize')

class DashboardResponse(BaseModel):
    goal: GoalResponse
    todays_intake: Decimal = Field(serialization_alias='todaysIntake')
    remaining_amount: Decimal = Field(serialization_alias='remainingAmount')
    completion_percent: float = Field(serialization_alias='completionPercent')
    goal_achieved: bool = Field(serialization_alias='goalAchieved')
    entries_today: int = Field(serialization_alias='entriesToday')
    weekly_average: Decimal = Field(serialization_alias='weeklyAverage')
    monthly_average: Decimal = Field(serialization_alias='monthlyAverage')
    current_streak: int = Field(serialization_alias='currentStreak')

class InsightsResponse(DashboardResponse):
    best_hydration_day: DaySummary | None = Field(serialization_alias='bestHydrationDay')
    intake_trend_by_week: list[AmountItem] = Field(serialization_alias='intakeTrendByWeek')
    intake_by_drink_type: list[AmountItem] = Field(serialization_alias='intakeByDrinkType')
    recent_entries: list[EntrySummaryResponse] = Field(serialization_alias='recentEntries')
    weekly_summaries: list[DaySummary] = Field(serialization_alias='weeklySummaries')
    monthly_summaries: list[DaySummary] = Field(serialization_alias='monthlySummaries')
    drink_types: list[str] = Field(serialization_alias='drinkTypes')
