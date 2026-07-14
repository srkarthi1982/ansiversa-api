from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SplitMethod = Literal["equal", "manual"]
ArchiveFilter = Literal["active", "archived", "all"]
ExpenseSort = Literal["newest", "oldest", "amount", "title"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class MemberCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    active: bool = True
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)


class MemberUpdateRequest(MemberCreateRequest):
    pass


class MemberResponse(BaseModel):
    id: str
    name: str
    active: bool
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ParticipantRequest(BaseModel):
    member_id: str = Field(alias="memberId", min_length=1, max_length=36)
    share_amount: Decimal | None = Field(default=None, alias="shareAmount", ge=0, max_digits=12, decimal_places=2)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ParticipantResponse(BaseModel):
    member_id: str = Field(serialization_alias="memberId")
    member_name: str = Field(serialization_alias="memberName")
    share_amount: Decimal = Field(serialization_alias="shareAmount")


class ExpenseCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=1, max_length=120)
    paid_by_member_id: str = Field(alias="paidByMemberId", min_length=1, max_length=36)
    split_method: SplitMethod = Field(alias="splitMethod")
    expense_date: str = Field(alias="expenseDate", min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=5000)
    participants: list[ParticipantRequest] = Field(min_length=1, max_length=30)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "category", "expense_date", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_payload(self) -> "ExpenseCreateRequest":
        _validate_iso_date(self.expense_date, "expenseDate")
        member_ids = [participant.member_id for participant in self.participants]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("Each participant can appear only once.")
        if self.split_method == "manual":
            total = sum((participant.share_amount or Decimal("0.00")) for participant in self.participants)
            if total.quantize(Decimal("0.01")) != self.amount.quantize(Decimal("0.01")):
                raise ValueError("Manual split shares must equal the expense amount.")
        return self


class ExpenseUpdateRequest(ExpenseCreateRequest):
    pass


class ExpenseSummaryResponse(BaseModel):
    id: str
    title: str
    amount: Decimal
    category: str
    paid_by_member_id: str = Field(serialization_alias="paidByMemberId")
    paid_by_member_name: str = Field(serialization_alias="paidByMemberName")
    split_method: SplitMethod = Field(serialization_alias="splitMethod")
    expense_date: str = Field(serialization_alias="expenseDate")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    archived: bool
    participants: list[ParticipantResponse]
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ExpenseDetailResponse(ExpenseSummaryResponse):
    notes: str | None


class SettlementCreateRequest(BaseModel):
    from_member_id: str = Field(alias="fromMemberId", min_length=1, max_length=36)
    to_member_id: str = Field(alias="toMemberId", min_length=1, max_length=36)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    settlement_date: str = Field(alias="settlementDate", min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("settlement_date", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_payload(self) -> "SettlementCreateRequest":
        _validate_iso_date(self.settlement_date, "settlementDate")
        if self.from_member_id == self.to_member_id:
            raise ValueError("Settlement members must be different.")
        return self


class SettlementUpdateRequest(SettlementCreateRequest):
    pass


class SettlementResponse(BaseModel):
    id: str
    from_member_id: str = Field(serialization_alias="fromMemberId")
    from_member_name: str = Field(serialization_alias="fromMemberName")
    to_member_id: str = Field(serialization_alias="toMemberId")
    to_member_name: str = Field(serialization_alias="toMemberName")
    amount: Decimal
    settlement_date: str = Field(serialization_alias="settlementDate")
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CountItem(BaseModel):
    label: str
    count: int


class AmountItem(BaseModel):
    label: str
    amount: Decimal


class BalanceItem(BaseModel):
    member_id: str = Field(serialization_alias="memberId")
    member_name: str = Field(serialization_alias="memberName")
    balance: Decimal


class DashboardResponse(BaseModel):
    total_expenses: Decimal = Field(serialization_alias="totalExpenses")
    total_settled: Decimal = Field(serialization_alias="totalSettled")
    outstanding_balance: Decimal = Field(serialization_alias="outstandingBalance")
    active_members: int = Field(serialization_alias="activeMembers")


class InsightsResponse(DashboardResponse):
    members: list[MemberResponse]
    expenses_by_member: list[AmountItem] = Field(serialization_alias="expensesByMember")
    expenses_by_category: list[AmountItem] = Field(serialization_alias="expensesByCategory")
    highest_spender: AmountItem | None = Field(serialization_alias="highestSpender")
    largest_expense: ExpenseSummaryResponse | None = Field(serialization_alias="largestExpense")
    outstanding_balances: list[BalanceItem] = Field(serialization_alias="outstandingBalances")
    recent_expenses: list[ExpenseSummaryResponse] = Field(serialization_alias="recentExpenses")
    recent_settlements: list[SettlementResponse] = Field(serialization_alias="recentSettlements")


def _validate_iso_date(value: str | None, field_name: str) -> None:
    if not value:
        return
    from datetime import date
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc
