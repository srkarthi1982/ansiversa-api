from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.household_expense_splitter import repository
from app.modules.household_expense_splitter.models import ExpenseParticipant, HouseholdExpense, HouseholdMember, HouseholdSettlement
from app.modules.household_expense_splitter.schemas import (
    AmountItem,
    ArchiveFilter,
    BalanceItem,
    DashboardResponse,
    ExpenseCreateRequest,
    ExpenseDetailResponse,
    ExpenseSort,
    ExpenseSummaryResponse,
    ExpenseUpdateRequest,
    InsightsResponse,
    MemberCreateRequest,
    MemberResponse,
    MemberUpdateRequest,
    ParticipantResponse,
    SettlementCreateRequest,
    SettlementResponse,
    SettlementUpdateRequest,
)


def _money(value: object) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    if len(normalized) <= 140:
        return normalized
    return f"{normalized[:137]}..."


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _member_response(member: HouseholdMember) -> MemberResponse:
    return MemberResponse(id=member.id, name=member.name, active=member.active, created_at=member.created_at, updated_at=member.updated_at)


def _get_owned_member(db: Session, user: User, member_id: str) -> HouseholdMember:
    member = repository.get_member(db, member_id)
    if not member or member.owner_id != user.id:
        _not_found("Member")
    return member


def _get_owned_expense(db: Session, user: User, expense_id: str) -> HouseholdExpense:
    expense = repository.get_expense(db, expense_id)
    if not expense or expense.owner_id != user.id:
        _not_found("Expense")
    return expense


def _get_owned_settlement(db: Session, user: User, settlement_id: str) -> HouseholdSettlement:
    settlement = repository.get_settlement(db, settlement_id)
    if not settlement or settlement.owner_id != user.id:
        _not_found("Settlement")
    return settlement


def list_members(db: Session, user: User) -> list[MemberResponse]:
    return [_member_response(member) for member in repository.list_members(db, user.id)]


def create_member(db: Session, user: User, payload: MemberCreateRequest) -> MemberResponse:
    member = HouseholdMember(owner_id=user.id, name=payload.name, active=payload.active)
    repository.add(db, member)
    _commit_or_conflict(db, "A member with this name already exists.")
    db.refresh(member)
    return _member_response(member)


def update_member(db: Session, user: User, member_id: str, payload: MemberUpdateRequest) -> MemberResponse:
    member = _get_owned_member(db, user, member_id)
    member.name = payload.name
    member.active = payload.active
    _commit_or_conflict(db, "A member with this name already exists.")
    db.refresh(member)
    return _member_response(member)


def delete_member(db: Session, user: User, member_id: str) -> None:
    member = _get_owned_member(db, user, member_id)
    if repository.member_link_count(db, user.id, member.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member is linked to expenses or settlements.")
    repository.delete_record(db, member)
    db.commit()


def _participant_response(participant: ExpenseParticipant) -> ParticipantResponse:
    return ParticipantResponse(member_id=participant.member_id, member_name=participant.member.name, share_amount=_money(participant.share_amount))


def _expense_summary(expense: HouseholdExpense) -> ExpenseSummaryResponse:
    return ExpenseSummaryResponse(
        id=expense.id,
        title=expense.title,
        amount=_money(expense.amount),
        category=expense.category,
        paid_by_member_id=expense.paid_by_member_id,
        paid_by_member_name=expense.paid_by_member.name,
        split_method=expense.split_method,  # type: ignore[arg-type]
        expense_date=expense.expense_date,
        notes_preview=_preview(expense.notes),
        archived=expense.archived,
        participants=[_participant_response(participant) for participant in sorted(expense.participants, key=lambda item: item.member.name.lower())],
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


def _expense_detail(expense: HouseholdExpense) -> ExpenseDetailResponse:
    return ExpenseDetailResponse(**_expense_summary(expense).model_dump(), notes=expense.notes)


def _validate_expense_members(db: Session, user: User, payload: ExpenseCreateRequest | ExpenseUpdateRequest) -> None:
    _get_owned_member(db, user, payload.paid_by_member_id)
    for participant in payload.participants:
        _get_owned_member(db, user, participant.member_id)


def _split_shares(payload: ExpenseCreateRequest | ExpenseUpdateRequest) -> list[tuple[str, Decimal]]:
    amount = _money(payload.amount)
    if payload.split_method == "manual":
        return [(participant.member_id, _money(participant.share_amount)) for participant in payload.participants]
    base = (amount / Decimal(len(payload.participants))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    shares = [base for _ in payload.participants]
    difference = amount - sum(shares, Decimal("0.00"))
    shares[-1] = _money(shares[-1] + difference)
    return [(participant.member_id, shares[index]) for index, participant in enumerate(payload.participants)]


def _apply_expense_payload(db: Session, expense: HouseholdExpense, payload: ExpenseCreateRequest | ExpenseUpdateRequest) -> None:
    expense.title = payload.title
    expense.amount = payload.amount
    expense.category = payload.category
    expense.paid_by_member_id = payload.paid_by_member_id
    expense.split_method = payload.split_method
    expense.expense_date = payload.expense_date
    expense.notes = payload.notes
    expense.participants.clear()
    db.flush()
    for member_id, share_amount in _split_shares(payload):
        expense.participants.append(ExpenseParticipant(member_id=member_id, share_amount=share_amount))


def create_expense(db: Session, user: User, payload: ExpenseCreateRequest) -> ExpenseDetailResponse:
    _validate_expense_members(db, user, payload)
    expense = HouseholdExpense(owner_id=user.id, title=payload.title, amount=payload.amount, category=payload.category, paid_by_member_id=payload.paid_by_member_id, split_method=payload.split_method, expense_date=payload.expense_date, notes=payload.notes)
    repository.add(db, expense)
    _apply_expense_payload(db, expense, payload)
    _commit_or_conflict(db, "Unable to create expense.")
    return _expense_detail(_get_owned_expense(db, user, expense.id))


def update_expense(db: Session, user: User, expense_id: str, payload: ExpenseUpdateRequest) -> ExpenseDetailResponse:
    expense = _get_owned_expense(db, user, expense_id)
    _validate_expense_members(db, user, payload)
    _apply_expense_payload(db, expense, payload)
    _commit_or_conflict(db, "Unable to update expense.")
    return _expense_detail(_get_owned_expense(db, user, expense.id))


def get_expense(db: Session, user: User, expense_id: str) -> ExpenseDetailResponse:
    return _expense_detail(_get_owned_expense(db, user, expense_id))


def _matches_expense(expense: HouseholdExpense, query: str | None, member_id: str | None, category: str | None, archive_filter: ArchiveFilter, split_method: str | None, expense_date: str | None) -> bool:
    if query and query.strip().lower() not in expense.title.lower():
        return False
    if member_id and member_id not in [expense.paid_by_member_id, *[participant.member_id for participant in expense.participants]]:
        return False
    if category and expense.category.lower() != category.strip().lower():
        return False
    if archive_filter == "active" and expense.archived:
        return False
    if archive_filter == "archived" and not expense.archived:
        return False
    if split_method and expense.split_method != split_method:
        return False
    if expense_date and expense.expense_date != expense_date:
        return False
    return True


def _sort_expenses(expenses: list[HouseholdExpense], sort_by: ExpenseSort) -> list[HouseholdExpense]:
    if sort_by == "oldest":
        return sorted(expenses, key=lambda expense: (expense.expense_date, expense.title.lower()))
    if sort_by == "amount":
        return sorted(expenses, key=lambda expense: (_money(expense.amount), expense.title.lower()), reverse=True)
    if sort_by == "title":
        return sorted(expenses, key=lambda expense: expense.title.lower())
    return sorted(expenses, key=lambda expense: (expense.expense_date, expense.created_at), reverse=True)


def list_expenses(db: Session, user: User, query: str | None = None, member_id: str | None = None, category: str | None = None, archive_filter: ArchiveFilter = "active", split_method: str | None = None, expense_date: str | None = None, sort_by: ExpenseSort = "newest") -> list[ExpenseSummaryResponse]:
    expenses = repository.list_expenses(db, user.id)
    filtered = [expense for expense in expenses if _matches_expense(expense, query, member_id, category, archive_filter, split_method, expense_date)]
    return [_expense_summary(expense) for expense in _sort_expenses(filtered, sort_by)]


def set_expense_archived(db: Session, user: User, expense_id: str, archived: bool) -> ExpenseDetailResponse:
    expense = _get_owned_expense(db, user, expense_id)
    expense.archived = archived
    db.commit()
    return _expense_detail(_get_owned_expense(db, user, expense.id))


def delete_expense(db: Session, user: User, expense_id: str) -> None:
    expense = _get_owned_expense(db, user, expense_id)
    repository.delete_record(db, expense)
    db.commit()


def _settlement_response(settlement: HouseholdSettlement) -> SettlementResponse:
    return SettlementResponse(
        id=settlement.id,
        from_member_id=settlement.from_member_id,
        from_member_name=settlement.from_member.name,
        to_member_id=settlement.to_member_id,
        to_member_name=settlement.to_member.name,
        amount=_money(settlement.amount),
        settlement_date=settlement.settlement_date,
        notes=settlement.notes,
        created_at=settlement.created_at,
        updated_at=settlement.updated_at,
    )


def list_settlements(db: Session, user: User) -> list[SettlementResponse]:
    return [_settlement_response(settlement) for settlement in repository.list_settlements(db, user.id)]


def create_settlement(db: Session, user: User, payload: SettlementCreateRequest) -> SettlementResponse:
    _get_owned_member(db, user, payload.from_member_id)
    _get_owned_member(db, user, payload.to_member_id)
    settlement = HouseholdSettlement(owner_id=user.id, from_member_id=payload.from_member_id, to_member_id=payload.to_member_id, amount=payload.amount, settlement_date=payload.settlement_date, notes=payload.notes)
    repository.add(db, settlement)
    _commit_or_conflict(db, "Unable to create settlement.")
    return _settlement_response(_get_owned_settlement(db, user, settlement.id))


def update_settlement(db: Session, user: User, settlement_id: str, payload: SettlementUpdateRequest) -> SettlementResponse:
    settlement = _get_owned_settlement(db, user, settlement_id)
    _get_owned_member(db, user, payload.from_member_id)
    _get_owned_member(db, user, payload.to_member_id)
    settlement.from_member_id = payload.from_member_id
    settlement.to_member_id = payload.to_member_id
    settlement.amount = payload.amount
    settlement.settlement_date = payload.settlement_date
    settlement.notes = payload.notes
    _commit_or_conflict(db, "Unable to update settlement.")
    return _settlement_response(_get_owned_settlement(db, user, settlement.id))


def delete_settlement(db: Session, user: User, settlement_id: str) -> None:
    settlement = _get_owned_settlement(db, user, settlement_id)
    repository.delete_record(db, settlement)
    db.commit()


def _balances(expenses: list[HouseholdExpense], settlements: list[HouseholdSettlement]) -> dict[str, Decimal]:
    balances: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for expense in expenses:
        if expense.archived:
            continue
        balances[expense.paid_by_member_id] += _money(expense.amount)
        for participant in expense.participants:
            balances[participant.member_id] -= _money(participant.share_amount)
    for settlement in settlements:
        balances[settlement.from_member_id] += _money(settlement.amount)
        balances[settlement.to_member_id] -= _money(settlement.amount)
    return {member_id: _money(balance) for member_id, balance in balances.items()}


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    expenses = repository.list_expenses(db, user.id)
    settlements = repository.list_settlements(db, user.id)
    balances = _balances(expenses, settlements)
    outstanding = sum((balance for balance in balances.values() if balance > 0), Decimal("0.00"))
    return DashboardResponse(
        total_expenses=sum((_money(expense.amount) for expense in expenses if not expense.archived), Decimal("0.00")),
        total_settled=sum((_money(settlement.amount) for settlement in settlements), Decimal("0.00")),
        outstanding_balance=_money(outstanding),
        active_members=len([member for member in repository.list_members(db, user.id) if member.active]),
    )


def get_insights(db: Session, user: User) -> InsightsResponse:
    members = repository.list_members(db, user.id)
    expenses = repository.list_expenses(db, user.id)
    active_expenses = [expense for expense in expenses if not expense.archived]
    settlements = repository.list_settlements(db, user.id)
    dashboard = get_dashboard(db, user)
    member_names = {member.id: member.name for member in members}
    by_member: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for expense in active_expenses:
        by_member[expense.paid_by_member_id] += _money(expense.amount)
        by_category[expense.category] += _money(expense.amount)
    balances = _balances(expenses, settlements)
    highest_spender = max((AmountItem(label=member_names.get(member_id, "Unknown"), amount=_money(amount)) for member_id, amount in by_member.items()), key=lambda item: item.amount, default=None)
    largest_expense = max(active_expenses, key=lambda expense: _money(expense.amount), default=None)
    return InsightsResponse(
        **dashboard.model_dump(),
        members=[_member_response(member) for member in members],
        expenses_by_member=[AmountItem(label=member_names.get(member_id, "Unknown"), amount=_money(amount)) for member_id, amount in sorted(by_member.items(), key=lambda item: item[1], reverse=True)],
        expenses_by_category=[AmountItem(label=label, amount=_money(amount)) for label, amount in sorted(by_category.items(), key=lambda item: item[1], reverse=True)],
        highest_spender=highest_spender,
        largest_expense=_expense_summary(largest_expense) if largest_expense else None,
        outstanding_balances=[BalanceItem(member_id=member_id, member_name=member_names.get(member_id, "Unknown"), balance=balance) for member_id, balance in sorted(balances.items(), key=lambda item: item[1], reverse=True) if balance != 0],
        recent_expenses=[_expense_summary(expense) for expense in _sort_expenses(active_expenses, "newest")[:8]],
        recent_settlements=[_settlement_response(settlement) for settlement in settlements[:8]],
    )
