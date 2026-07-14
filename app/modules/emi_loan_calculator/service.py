from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP, getcontext
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.emi_loan_calculator import repository
from app.modules.emi_loan_calculator.models import LoanScenario
from app.modules.emi_loan_calculator.schemas import (
    EmiLoanCalculationRequest,
    EmiLoanCalculationResponse,
    EmiLoanDashboardResponse,
    EmiLoanInstallmentResponse,
    EmiLoanScenarioCreateRequest,
    EmiLoanScenarioDetailResponse,
    EmiLoanScenarioSummaryResponse,
    EmiLoanScenarioUpdateRequest,
)

getcontext().prec = 28

MONEY = Decimal("0.01")
RATIO = Decimal("0.0001")
ZERO = Decimal("0")
MAX_INSTALLMENTS = 600


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def _ratio(value: Decimal) -> Decimal:
    return value.quantize(RATIO, rounding=ROUND_HALF_UP)


def _months_in_term(duration_value: int, duration_unit: str) -> int:
    months = duration_value * 12 if duration_unit == "years" else duration_value
    if months <= 0 or months > MAX_INSTALLMENTS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Loan duration must be between 1 and 600 monthly installments.")
    return months


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(value.day, days[month - 1]))


def _parse_start_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="startDate must use YYYY-MM-DD format.") from exc


def _emi(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    if annual_rate == ZERO:
        return _money(principal / Decimal(months))
    periodic_rate = annual_rate / Decimal("12") / Decimal("100")
    factor = (Decimal("1") + periodic_rate) ** months
    return _money(principal * periodic_rate * factor / (factor - Decimal("1")))


def _calculate_base_interest(payload: EmiLoanCalculationRequest, extra_payment: Decimal) -> Decimal:
    clone = payload.model_copy(update={"extra_payment": extra_payment})
    return calculate_loan(clone, include_savings=False).total_interest


def calculate_loan(payload: EmiLoanCalculationRequest, include_savings: bool = True) -> EmiLoanCalculationResponse:
    principal = _money(payload.loan_amount)
    processing_fee = _money(payload.processing_fee)
    extra_payment = _money(payload.extra_payment)
    months = _months_in_term(payload.duration_value, payload.duration_unit)
    regular_emi = _emi(principal, payload.annual_interest_rate, months)
    periodic_rate = payload.annual_interest_rate / Decimal("12") / Decimal("100")
    start_date = _parse_start_date(payload.start_date)
    balance = principal
    total_interest = ZERO
    schedule: list[EmiLoanInstallmentResponse] = []

    for installment in range(1, months + 1):
        if balance <= Decimal("0.005"):
            break
        opening = balance
        interest = _money(opening * periodic_rate)
        due = opening + interest
        scheduled_emi = min(regular_emi, due)
        remaining_after_emi = max(due - scheduled_emi, ZERO)
        applied_extra = min(extra_payment, remaining_after_emi)
        total_payment = scheduled_emi + applied_extra
        principal_component = total_payment - interest
        if principal_component <= ZERO:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Loan terms do not reduce principal. Adjust the rate, term, or payment.")
        balance = max(opening - principal_component, ZERO)
        if balance <= Decimal("0.005"):
            balance = ZERO

        total_interest += interest
        payment_date = _add_months(start_date, installment).isoformat() if start_date else None
        schedule.append(
            EmiLoanInstallmentResponse(
                installment_number=installment,
                payment_date=payment_date,
                opening_balance=_money(opening),
                scheduled_emi=_money(scheduled_emi),
                extra_payment=_money(applied_extra),
                principal_component=_money(principal_component),
                interest_component=interest,
                closing_balance=_money(balance),
            )
        )

    if schedule and schedule[-1].closing_balance != ZERO:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Loan schedule did not close within the allowed duration.")

    total_interest = _money(total_interest)
    total_repayment = _money(principal + total_interest)
    savings = ZERO
    if include_savings and extra_payment > ZERO:
        savings = _money(_calculate_base_interest(payload, ZERO) - total_interest)

    estimated_payoff_date = schedule[-1].payment_date if schedule else None
    return EmiLoanCalculationResponse(
        regular_emi=regular_emi,
        total_principal=principal,
        total_interest=total_interest,
        total_repayment=total_repayment,
        processing_fee=processing_fee,
        overall_loan_cost=_money(total_repayment + processing_fee),
        installment_count=len(schedule),
        estimated_payoff_date=estimated_payoff_date,
        interest_to_principal_ratio=_ratio(total_interest / principal if principal else ZERO),
        savings_from_extra_payment=max(savings, ZERO),
        schedule=schedule,
    )


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _commit_or_conflict(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc


def _get_owned_scenario(db: Session, user: User, scenario_id: str) -> LoanScenario:
    scenario = repository.get_scenario(db, scenario_id)
    if not scenario or scenario.owner_id != user.id:
        _not_found("Loan scenario was not found.")
    return scenario


def _calculation_payload_from_scenario(scenario: LoanScenario) -> EmiLoanCalculationRequest:
    return EmiLoanCalculationRequest(
        loan_amount=scenario.loan_amount,
        annual_interest_rate=scenario.annual_interest_rate,
        duration_value=scenario.duration_value,
        duration_unit=scenario.duration_unit,
        repayment_frequency=scenario.repayment_frequency,
        start_date=scenario.start_date,
        processing_fee=scenario.processing_fee,
        extra_payment=scenario.extra_payment,
        currency_code=scenario.currency_code,
    )


def _summary(scenario: LoanScenario) -> EmiLoanScenarioSummaryResponse:
    return EmiLoanScenarioSummaryResponse(
        id=scenario.id,
        name=scenario.name,
        loan_amount=scenario.loan_amount,
        annual_interest_rate=scenario.annual_interest_rate,
        duration_value=scenario.duration_value,
        duration_unit=scenario.duration_unit,
        repayment_frequency=scenario.repayment_frequency,
        start_date=scenario.start_date,
        processing_fee=scenario.processing_fee,
        extra_payment=scenario.extra_payment,
        currency_code=scenario.currency_code,
        calculated_emi=scenario.calculated_emi,
        total_interest=scenario.total_interest,
        total_repayment=scenario.total_repayment,
        overall_loan_cost=scenario.overall_loan_cost,
        estimated_payoff_date=scenario.estimated_payoff_date,
        installment_count=scenario.installment_count,
        interest_to_principal_ratio=scenario.interest_to_principal_ratio,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at,
    )


def _detail(scenario: LoanScenario) -> EmiLoanScenarioDetailResponse:
    return EmiLoanScenarioDetailResponse(**_summary(scenario).model_dump(), calculation=calculate_loan(_calculation_payload_from_scenario(scenario)))


def _scenario_fields(payload: EmiLoanCalculationRequest, calculation: EmiLoanCalculationResponse) -> dict[str, object]:
    return {
        "loan_amount": payload.loan_amount,
        "annual_interest_rate": payload.annual_interest_rate,
        "duration_value": payload.duration_value,
        "duration_unit": payload.duration_unit,
        "repayment_frequency": payload.repayment_frequency,
        "start_date": payload.start_date,
        "processing_fee": payload.processing_fee,
        "extra_payment": payload.extra_payment,
        "currency_code": payload.currency_code,
        "calculated_emi": calculation.regular_emi,
        "total_interest": calculation.total_interest,
        "total_repayment": calculation.total_repayment,
        "overall_loan_cost": calculation.overall_loan_cost,
        "estimated_payoff_date": calculation.estimated_payoff_date,
        "installment_count": calculation.installment_count,
        "interest_to_principal_ratio": calculation.interest_to_principal_ratio,
    }


def get_dashboard(db: Session, user: User) -> EmiLoanDashboardResponse:
    scenarios = repository.list_scenarios(db, user.id)
    summaries = [_summary(item) for item in scenarios]
    return EmiLoanDashboardResponse(
        scenarios=summaries,
        total_scenarios=len(summaries),
        active_scenarios=len(summaries),
        aggregate_principal=_money(sum((item.loan_amount for item in scenarios), ZERO)),
        aggregate_projected_interest=_money(sum((item.total_interest for item in scenarios), ZERO)),
        highest_emi=max((item.calculated_emi for item in scenarios), default=ZERO),
        lowest_emi=min((item.calculated_emi for item in scenarios), default=ZERO),
        highest_total_interest=max((item.total_interest for item in scenarios), default=ZERO),
    )


def list_scenarios(db: Session, user: User) -> list[EmiLoanScenarioSummaryResponse]:
    return [_summary(item) for item in repository.list_scenarios(db, user.id)]


def create_scenario(db: Session, user: User, payload: EmiLoanScenarioCreateRequest) -> EmiLoanScenarioDetailResponse:
    calculation = calculate_loan(payload)
    scenario = LoanScenario(owner_id=user.id, name=payload.name, **_scenario_fields(payload, calculation))
    repository.add(db, scenario)
    _commit_or_conflict(db, "A loan scenario with this name already exists.")
    db.refresh(scenario)
    return _detail(scenario)


def get_scenario(db: Session, user: User, scenario_id: str) -> EmiLoanScenarioDetailResponse:
    return _detail(_get_owned_scenario(db, user, scenario_id))


def update_scenario(db: Session, user: User, scenario_id: str, payload: EmiLoanScenarioUpdateRequest) -> EmiLoanScenarioDetailResponse:
    scenario = _get_owned_scenario(db, user, scenario_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(scenario, field, value)
    calculation_payload = _calculation_payload_from_scenario(scenario)
    calculation = calculate_loan(calculation_payload)
    for field, value in _scenario_fields(calculation_payload, calculation).items():
        setattr(scenario, field, value)
    _commit_or_conflict(db, "A loan scenario with this name already exists.")
    db.refresh(scenario)
    return _detail(scenario)


def duplicate_scenario(db: Session, user: User, scenario_id: str) -> EmiLoanScenarioDetailResponse:
    original = _get_owned_scenario(db, user, scenario_id)
    payload = _calculation_payload_from_scenario(original)
    calculation = calculate_loan(payload)
    scenario = LoanScenario(
        owner_id=user.id,
        name=f"{original.name} copy {uuid4().hex[:6]}",
        **_scenario_fields(payload, calculation),
    )
    repository.add(db, scenario)
    _commit_or_conflict(db, "A copied loan scenario with this name already exists.")
    db.refresh(scenario)
    return _detail(scenario)


def delete_scenario(db: Session, user: User, scenario_id: str) -> None:
    scenario = _get_owned_scenario(db, user, scenario_id)
    repository.delete_record(db, scenario)
    db.commit()
