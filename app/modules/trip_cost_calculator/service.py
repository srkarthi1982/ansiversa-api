from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.trip_cost_calculator import repository
from app.modules.trip_cost_calculator.models import TripCostExpense, TripCostTrip
from app.modules.trip_cost_calculator.schemas import (
    TripCostBreakdownResponse,
    TripCostComparisonResponse,
    TripCostDashboardResponse,
    TripCostExpenseCreateRequest,
    TripCostExpenseDetailResponse,
    TripCostExpenseSummaryResponse,
    TripCostExpenseUpdateRequest,
    TripCostMonthlyResponse,
    TripCostTripCreateRequest,
    TripCostTripDetailResponse,
    TripCostTripSummaryResponse,
    TripCostTripUpdateRequest,
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


def _get_owned_trip(db: Session, user: User, trip_id: str) -> TripCostTrip:
    trip = repository.get_trip(db, trip_id)
    if not trip or trip.owner_id != user.id:
        _not_found("Trip was not found.")
    return trip


def _get_owned_expense(db: Session, user: User, expense_id: str) -> TripCostExpense:
    expense = repository.get_expense(db, expense_id)
    if not expense or expense.owner_id != user.id:
        _not_found("Cost item was not found.")
    return expense


def _trip_total(trip: TripCostTrip) -> float:
    return round(sum(expense.amount for expense in trip.expenses), 2)


def _trip_summary(trip: TripCostTrip) -> TripCostTripSummaryResponse:
    total = _trip_total(trip)
    return TripCostTripSummaryResponse(
        id=trip.id,
        name=trip.name,
        start_location=trip.start_location,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        travelers=trip.travelers,
        vehicle=trip.vehicle,
        distance=trip.distance,
        currency_code=trip.currency_code,
        notes_preview=_preview(trip.notes),
        expense_count=len(trip.expenses),
        total_cost=total,
        cost_per_traveler=round(total / trip.travelers, 2) if trip.travelers else 0,
        cost_per_kilometer=round(total / trip.distance, 2) if trip.distance else 0,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


def _trip_detail(trip: TripCostTrip) -> TripCostTripDetailResponse:
    return TripCostTripDetailResponse(**_trip_summary(trip).model_dump(), notes=trip.notes)


def _expense_summary(expense: TripCostExpense) -> TripCostExpenseSummaryResponse:
    return TripCostExpenseSummaryResponse(
        id=expense.id,
        trip_id=expense.trip_id,
        trip_name=expense.trip.name if expense.trip else "Trip",
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        currency_code=expense.currency_code,
        expense_date=expense.expense_date,
        notes_preview=_preview(expense.notes),
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


def _expense_detail(expense: TripCostExpense) -> TripCostExpenseDetailResponse:
    return TripCostExpenseDetailResponse(**_expense_summary(expense).model_dump(), notes=expense.notes)


def _comparison(trip: TripCostTrip) -> TripCostComparisonResponse:
    total = _trip_total(trip)
    by_category: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})
    for expense in trip.expenses:
        item = by_category[expense.category]
        item["amount"] += expense.amount
        item["count"] += 1
    breakdown = [
        TripCostBreakdownResponse(label=label, amount=round(values["amount"], 2), count=int(values["count"]))
        for label, values in sorted(by_category.items())
    ]
    non_empty = [item for item in breakdown if item.amount > 0]
    highest = max(non_empty, key=lambda item: item.amount).label if non_empty else None
    lowest = min(non_empty, key=lambda item: item.amount).label if non_empty else None
    return TripCostComparisonResponse(
        trip_id=trip.id,
        trip_name=trip.name,
        total_cost=total,
        cost_per_traveler=round(total / trip.travelers, 2) if trip.travelers else 0,
        cost_per_kilometer=round(total / trip.distance, 2) if trip.distance else 0,
        category_breakdown=breakdown,
        highest_expense_category=highest,
        lowest_expense_category=lowest,
    )


def list_trips(db: Session, user: User) -> list[TripCostTripSummaryResponse]:
    return [_trip_summary(trip) for trip in repository.list_trips(db, user.id)]


def create_trip(db: Session, user: User, payload: TripCostTripCreateRequest) -> TripCostTripDetailResponse:
    trip = TripCostTrip(owner_id=user.id, **payload.model_dump())
    repository.add(db, trip)
    db.commit()
    db.refresh(trip)
    return _trip_detail(trip)


def get_trip(db: Session, user: User, trip_id: str) -> TripCostTripDetailResponse:
    return _trip_detail(_get_owned_trip(db, user, trip_id))


def update_trip(db: Session, user: User, trip_id: str, payload: TripCostTripUpdateRequest) -> TripCostTripDetailResponse:
    trip = _get_owned_trip(db, user, trip_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return _trip_detail(trip)


def duplicate_trip(db: Session, user: User, trip_id: str) -> TripCostTripDetailResponse:
    source = _get_owned_trip(db, user, trip_id)
    copy = TripCostTrip(
        owner_id=user.id,
        name=f"{source.name} copy",
        start_location=source.start_location,
        destination=source.destination,
        start_date=source.start_date,
        end_date=source.end_date,
        travelers=source.travelers,
        vehicle=source.vehicle,
        distance=source.distance,
        currency_code=source.currency_code,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _trip_detail(copy)


def delete_trip(db: Session, user: User, trip_id: str) -> None:
    trip = _get_owned_trip(db, user, trip_id)
    repository.delete_record(db, trip)
    db.commit()


def list_expenses(db: Session, user: User) -> list[TripCostExpenseSummaryResponse]:
    return [_expense_summary(expense) for expense in repository.list_expenses(db, user.id)]


def create_expense(db: Session, user: User, payload: TripCostExpenseCreateRequest) -> TripCostExpenseDetailResponse:
    data = payload.model_dump()
    _get_owned_trip(db, user, data["trip_id"])
    expense = TripCostExpense(owner_id=user.id, **data)
    repository.add(db, expense)
    db.commit()
    db.refresh(expense)
    return _expense_detail(expense)


def get_expense(db: Session, user: User, expense_id: str) -> TripCostExpenseDetailResponse:
    return _expense_detail(_get_owned_expense(db, user, expense_id))


def update_expense(db: Session, user: User, expense_id: str, payload: TripCostExpenseUpdateRequest) -> TripCostExpenseDetailResponse:
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


def get_dashboard(db: Session, user: User) -> TripCostDashboardResponse:
    raw_trips = repository.list_trips(db, user.id)
    raw_expenses = repository.list_expenses(db, user.id)
    trips = [_trip_summary(trip) for trip in raw_trips]
    expenses = [_expense_summary(expense) for expense in raw_expenses]
    total = round(sum(expense.amount for expense in expenses), 2)
    category: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})
    for expense in expenses:
        category_item = category[expense.category]
        category_item["amount"] += expense.amount
        category_item["count"] += 1
        month_item = monthly[_month_key(expense.expense_date)]
        month_item["amount"] += expense.amount
        month_item["count"] += 1
    traveler_costs = [trip.cost_per_traveler for trip in trips if trip.travelers]
    return TripCostDashboardResponse(
        trips=trips,
        expenses=expenses,
        comparisons=[_comparison(trip) for trip in raw_trips],
        total_trips=len(trips),
        total_expenses=total,
        average_trip_cost=round(total / len(trips), 2) if trips else 0,
        average_cost_per_traveler=round(sum(traveler_costs) / len(traveler_costs), 2) if traveler_costs else 0,
        cost_by_category=[
            TripCostBreakdownResponse(label=label, amount=round(values["amount"], 2), count=int(values["count"]))
            for label, values in sorted(category.items())
        ],
        monthly_spending=[
            TripCostMonthlyResponse(month=month, amount=round(values["amount"], 2), count=int(values["count"]))
            for month, values in sorted(monthly.items(), reverse=True)
        ],
        recent_activity=expenses[:6],
    )
