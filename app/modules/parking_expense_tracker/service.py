from collections import defaultdict
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.parking_expense_tracker import repository
from app.modules.parking_expense_tracker.models import ParkingExpenseEntry, ParkingExpenseLocation
from app.modules.parking_expense_tracker.schemas import (
    ParkingExpenseBreakdownResponse,
    ParkingExpenseDashboardResponse,
    ParkingExpenseEntryCreateRequest,
    ParkingExpenseEntryDetailResponse,
    ParkingExpenseEntrySummaryResponse,
    ParkingExpenseEntryUpdateRequest,
    ParkingExpenseLocationCreateRequest,
    ParkingExpenseLocationDetailResponse,
    ParkingExpenseLocationSummaryResponse,
    ParkingExpenseLocationUpdateRequest,
    ParkingExpenseMonthlySpendingResponse,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _month_key(value: str) -> str:
    return value[:7] if len(value) >= 7 else value


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_location(db: Session, user: User, location_id: str) -> ParkingExpenseLocation:
    location = repository.get_location(db, location_id)
    if not location or location.owner_id != user.id:
        _not_found("Parking location was not found.")
    return location


def _get_owned_expense(db: Session, user: User, expense_id: str) -> ParkingExpenseEntry:
    expense = repository.get_expense(db, expense_id)
    if not expense or expense.owner_id != user.id:
        _not_found("Parking expense was not found.")
    return expense


def _location_summary(location: ParkingExpenseLocation) -> ParkingExpenseLocationSummaryResponse:
    expenses = list(location.expenses)
    return ParkingExpenseLocationSummaryResponse(
        id=location.id,
        name=location.name,
        city=location.city,
        area=location.area,
        parking_type=location.parking_type,
        default_hourly_rate=location.default_hourly_rate,
        notes_preview=_preview(location.notes),
        expense_count=len(expenses),
        total_amount=round(sum(expense.amount for expense in expenses), 2),
        created_at=location.created_at,
        updated_at=location.updated_at,
    )


def _location_detail(location: ParkingExpenseLocation) -> ParkingExpenseLocationDetailResponse:
    return ParkingExpenseLocationDetailResponse(**_location_summary(location).model_dump(), notes=location.notes)


def _expense_summary(expense: ParkingExpenseEntry) -> ParkingExpenseEntrySummaryResponse:
    return ParkingExpenseEntrySummaryResponse(
        id=expense.id,
        location_id=expense.location_id,
        location_name=expense.location.name if expense.location else "Parking location",
        parked_at=expense.parked_at,
        start_time=expense.start_time,
        end_time=expense.end_time,
        duration_minutes=expense.duration_minutes,
        amount=expense.amount,
        currency_code=expense.currency_code,
        payment_method=expense.payment_method,
        vehicle=expense.vehicle,
        purpose=expense.purpose,
        notes_preview=_preview(expense.notes),
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


def _expense_detail(expense: ParkingExpenseEntry) -> ParkingExpenseEntryDetailResponse:
    return ParkingExpenseEntryDetailResponse(**_expense_summary(expense).model_dump(), notes=expense.notes)


def list_locations(db: Session, user: User) -> list[ParkingExpenseLocationSummaryResponse]:
    return [_location_summary(location) for location in repository.list_locations(db, user.id)]


def create_location(db: Session, user: User, payload: ParkingExpenseLocationCreateRequest) -> ParkingExpenseLocationDetailResponse:
    location = ParkingExpenseLocation(owner_id=user.id, **payload.model_dump())
    repository.add(db, location)
    db.commit()
    db.refresh(location)
    return _location_detail(location)


def get_location(db: Session, user: User, location_id: str) -> ParkingExpenseLocationDetailResponse:
    return _location_detail(_get_owned_location(db, user, location_id))


def update_location(db: Session, user: User, location_id: str, payload: ParkingExpenseLocationUpdateRequest) -> ParkingExpenseLocationDetailResponse:
    location = _get_owned_location(db, user, location_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return _location_detail(location)


def delete_location(db: Session, user: User, location_id: str) -> None:
    location = _get_owned_location(db, user, location_id)
    repository.delete_record(db, location)
    db.commit()


def list_expenses(db: Session, user: User) -> list[ParkingExpenseEntrySummaryResponse]:
    return [_expense_summary(expense) for expense in repository.list_expenses(db, user.id)]


def create_expense(db: Session, user: User, payload: ParkingExpenseEntryCreateRequest) -> ParkingExpenseEntryDetailResponse:
    data = payload.model_dump()
    _get_owned_location(db, user, data["location_id"])
    expense = ParkingExpenseEntry(owner_id=user.id, **data)
    repository.add(db, expense)
    db.commit()
    db.refresh(expense)
    return _expense_detail(expense)


def get_expense(db: Session, user: User, expense_id: str) -> ParkingExpenseEntryDetailResponse:
    return _expense_detail(_get_owned_expense(db, user, expense_id))


def update_expense(db: Session, user: User, expense_id: str, payload: ParkingExpenseEntryUpdateRequest) -> ParkingExpenseEntryDetailResponse:
    expense = _get_owned_expense(db, user, expense_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return _expense_detail(expense)


def delete_expense(db: Session, user: User, expense_id: str) -> None:
    expense = _get_owned_expense(db, user, expense_id)
    repository.delete_record(db, expense)
    db.commit()


def get_dashboard(db: Session, user: User) -> ParkingExpenseDashboardResponse:
    locations = [_location_summary(location) for location in repository.list_locations(db, user.id)]
    expenses = [_expense_summary(expense) for expense in repository.list_expenses(db, user.id)]
    total = round(sum(expense.amount for expense in expenses), 2)
    current_month = date.today().isoformat()[:7]
    this_month = round(sum(expense.amount for expense in expenses if _month_key(expense.parked_at) == current_month), 2)
    sessions = len(expenses)
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "sessions": 0})
    by_payment: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "sessions": 0})
    by_location: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "sessions": 0})

    for expense in expenses:
        month_item = monthly[_month_key(expense.parked_at)]
        month_item["amount"] += expense.amount
        month_item["sessions"] += 1
        payment_item = by_payment[expense.payment_method]
        payment_item["amount"] += expense.amount
        payment_item["sessions"] += 1
        location_item = by_location[expense.location_name]
        location_item["amount"] += expense.amount
        location_item["sessions"] += 1

    return ParkingExpenseDashboardResponse(
        locations=locations,
        expenses=expenses,
        total_expenses=total,
        this_month=this_month,
        average_per_visit=round(total / sessions, 2) if sessions else 0,
        total_sessions=sessions,
        monthly_spending=[
            ParkingExpenseMonthlySpendingResponse(month=month, amount=round(values["amount"], 2), sessions=int(values["sessions"]))
            for month, values in sorted(monthly.items(), reverse=True)
        ],
        spending_by_payment_method=[
            ParkingExpenseBreakdownResponse(label=label, amount=round(values["amount"], 2), sessions=int(values["sessions"]))
            for label, values in sorted(by_payment.items())
        ],
        spending_by_location=[
            ParkingExpenseBreakdownResponse(label=label, amount=round(values["amount"], 2), sessions=int(values["sessions"]))
            for label, values in sorted(by_location.items())
        ],
    )
