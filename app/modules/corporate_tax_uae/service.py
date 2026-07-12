from collections import defaultdict
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.corporate_tax_uae import repository
from app.modules.corporate_tax_uae.models import CorporateTaxAdjustment, CorporateTaxObligation, CorporateTaxPeriod
from app.modules.corporate_tax_uae.schemas import (
    CorporateTaxAdjustmentCreateRequest,
    CorporateTaxAdjustmentDetailResponse,
    CorporateTaxAdjustmentSummaryResponse,
    CorporateTaxAdjustmentUpdateRequest,
    CorporateTaxAssumptionResponse,
    CorporateTaxBreakdownResponse,
    CorporateTaxDashboardResponse,
    CorporateTaxMoneyResponse,
    CorporateTaxObligationCreateRequest,
    CorporateTaxObligationDetailResponse,
    CorporateTaxObligationSummaryResponse,
    CorporateTaxObligationUpdateRequest,
    CorporateTaxPeriodComparisonResponse,
    CorporateTaxPeriodCreateRequest,
    CorporateTaxPeriodDetailResponse,
    CorporateTaxPeriodSummaryResponse,
    CorporateTaxPeriodUpdateRequest,
)

PREVIEW_LENGTH = 220
DISCLAIMER = (
    "Corporate Tax UAE stores user-entered planning records and produces estimates from configured assumptions. "
    "It does not provide legal, accounting, audit, filing, or tax advice. Verify current requirements and calculations "
    "with the UAE Federal Tax Authority and a qualified professional."
)


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _today_key() -> str:
    return date.today().isoformat()


def _get_owned_period(db: Session, user: User, period_id: str) -> CorporateTaxPeriod:
    period = repository.get_period(db, period_id)
    if not period or period.owner_id != user.id:
        _not_found("Tax period was not found.")
    return period


def _get_owned_adjustment(db: Session, user: User, adjustment_id: str) -> CorporateTaxAdjustment:
    adjustment = repository.get_adjustment(db, adjustment_id)
    if not adjustment or adjustment.owner_id != user.id:
        _not_found("Adjustment was not found.")
    return adjustment


def _get_owned_obligation(db: Session, user: User, obligation_id: str) -> CorporateTaxObligation:
    obligation = repository.get_obligation(db, obligation_id)
    if not obligation or obligation.owner_id != user.id:
        _not_found("Obligation was not found.")
    return obligation


def _signed_adjustment(adjustment: CorporateTaxAdjustment) -> float:
    sign = -1 if adjustment.direction == "decrease_taxable_income" else 1
    return round(adjustment.amount * sign, 2)


def _net_adjustment(period: CorporateTaxPeriod) -> float:
    return round(sum(_signed_adjustment(adjustment) for adjustment in period.adjustments if adjustment.currency_code == period.currency_code), 2)


def _calculated_taxable_income(period: CorporateTaxPeriod) -> float:
    if period.taxable_income_estimate is not None:
        return round(period.taxable_income_estimate, 2)
    return round(period.accounting_profit + _net_adjustment(period), 2)


def _indicative_tax_estimate(period: CorporateTaxPeriod) -> float:
    taxable_income = _calculated_taxable_income(period)
    taxable_above_threshold = max(0, taxable_income - period.tax_threshold)
    return round(taxable_above_threshold * (period.tax_rate_percent / 100), 2)


def _assumption(period: CorporateTaxPeriod) -> CorporateTaxAssumptionResponse:
    return CorporateTaxAssumptionResponse(
        tax_rate_percent=period.tax_rate_percent,
        tax_threshold=period.tax_threshold,
        currency_code=period.currency_code,
        effective_date=period.assumption_effective_date,
        reference_note=period.assumption_reference_note,
        basis="Estimate only: taxable income uses the user-entered estimate when present, otherwise accounting profit plus same-currency user-entered adjustments.",
    )


def _period_summary(period: CorporateTaxPeriod) -> CorporateTaxPeriodSummaryResponse:
    return CorporateTaxPeriodSummaryResponse(
        id=period.id,
        name=period.name,
        financial_year_start=period.financial_year_start,
        financial_year_end=period.financial_year_end,
        filing_due_date=period.filing_due_date,
        entity_name=period.entity_name,
        entity_type=period.entity_type,
        revenue=period.revenue,
        accounting_profit=period.accounting_profit,
        taxable_income_estimate=period.taxable_income_estimate,
        calculated_taxable_income_estimate=_calculated_taxable_income(period),
        indicative_tax_estimate=_indicative_tax_estimate(period),
        currency_code=period.currency_code,
        status=period.status,
        adjustment_count=len(period.adjustments),
        obligation_count=len(period.obligations),
        net_adjustment=_net_adjustment(period),
        notes_preview=_preview(period.notes),
        assumption=_assumption(period),
        created_at=period.created_at,
        updated_at=period.updated_at,
    )


def _period_detail(period: CorporateTaxPeriod) -> CorporateTaxPeriodDetailResponse:
    return CorporateTaxPeriodDetailResponse(
        **_period_summary(period).model_dump(),
        trade_licence_number=period.trade_licence_number,
        tax_registration_number=period.tax_registration_number,
        notes=period.notes,
    )


def _adjustment_summary(adjustment: CorporateTaxAdjustment) -> CorporateTaxAdjustmentSummaryResponse:
    return CorporateTaxAdjustmentSummaryResponse(
        id=adjustment.id,
        period_id=adjustment.period_id,
        period_name=adjustment.period.name if adjustment.period else "Tax period",
        title=adjustment.title,
        category=adjustment.category,
        direction=adjustment.direction,
        amount=adjustment.amount,
        signed_amount=_signed_adjustment(adjustment),
        currency_code=adjustment.currency_code,
        reference=adjustment.reference,
        supporting_document_note=adjustment.supporting_document_note,
        treatment_status=adjustment.treatment_status,
        explanation_preview=_preview(adjustment.explanation),
        notes_preview=_preview(adjustment.notes),
        created_at=adjustment.created_at,
        updated_at=adjustment.updated_at,
    )


def _adjustment_detail(adjustment: CorporateTaxAdjustment) -> CorporateTaxAdjustmentDetailResponse:
    return CorporateTaxAdjustmentDetailResponse(**_adjustment_summary(adjustment).model_dump(), explanation=adjustment.explanation, notes=adjustment.notes)


def _obligation_summary(obligation: CorporateTaxObligation) -> CorporateTaxObligationSummaryResponse:
    return CorporateTaxObligationSummaryResponse(
        id=obligation.id,
        period_id=obligation.period_id,
        period_name=obligation.period.name if obligation.period else "Tax period",
        title=obligation.title,
        obligation_type=obligation.obligation_type,
        due_date=obligation.due_date,
        priority=obligation.priority,
        status=obligation.status,
        responsible_person=obligation.responsible_person,
        external_reference=obligation.external_reference,
        completion_date=obligation.completion_date,
        notes_preview=_preview(obligation.notes),
        created_at=obligation.created_at,
        updated_at=obligation.updated_at,
    )


def _obligation_detail(obligation: CorporateTaxObligation) -> CorporateTaxObligationDetailResponse:
    return CorporateTaxObligationDetailResponse(**_obligation_summary(obligation).model_dump(), notes=obligation.notes)


def _money_items(values: dict[str, float]) -> list[CorporateTaxMoneyResponse]:
    return [CorporateTaxMoneyResponse(currency_code=currency, amount=round(amount, 2)) for currency, amount in sorted(values.items())]


def list_periods(db: Session, user: User) -> list[CorporateTaxPeriodSummaryResponse]:
    return [_period_summary(period) for period in repository.list_periods(db, user.id)]


def create_period(db: Session, user: User, payload: CorporateTaxPeriodCreateRequest) -> CorporateTaxPeriodDetailResponse:
    period = CorporateTaxPeriod(owner_id=user.id, **payload.model_dump())
    repository.add(db, period)
    db.commit()
    db.refresh(period)
    return _period_detail(period)


def get_period(db: Session, user: User, period_id: str) -> CorporateTaxPeriodDetailResponse:
    return _period_detail(_get_owned_period(db, user, period_id))


def update_period(db: Session, user: User, period_id: str, payload: CorporateTaxPeriodUpdateRequest) -> CorporateTaxPeriodDetailResponse:
    period = _get_owned_period(db, user, period_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(period, field, value)
    db.commit()
    db.refresh(period)
    return _period_detail(period)


def duplicate_period(db: Session, user: User, period_id: str) -> CorporateTaxPeriodDetailResponse:
    source = _get_owned_period(db, user, period_id)
    copy = CorporateTaxPeriod(
        owner_id=user.id,
        name=f"{source.name} copy",
        financial_year_start=source.financial_year_start,
        financial_year_end=source.financial_year_end,
        filing_due_date=source.filing_due_date,
        entity_name=source.entity_name,
        trade_licence_number=source.trade_licence_number,
        tax_registration_number=source.tax_registration_number,
        entity_type=source.entity_type,
        revenue=source.revenue,
        accounting_profit=source.accounting_profit,
        taxable_income_estimate=source.taxable_income_estimate,
        currency_code=source.currency_code,
        status="draft",
        tax_rate_percent=source.tax_rate_percent,
        tax_threshold=source.tax_threshold,
        assumption_effective_date=source.assumption_effective_date,
        assumption_reference_note=source.assumption_reference_note,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _period_detail(copy)


def delete_period(db: Session, user: User, period_id: str) -> None:
    period = _get_owned_period(db, user, period_id)
    repository.delete_record(db, period)
    db.commit()


def list_adjustments(db: Session, user: User) -> list[CorporateTaxAdjustmentSummaryResponse]:
    return [_adjustment_summary(adjustment) for adjustment in repository.list_adjustments(db, user.id)]


def create_adjustment(db: Session, user: User, payload: CorporateTaxAdjustmentCreateRequest) -> CorporateTaxAdjustmentDetailResponse:
    data = payload.model_dump()
    _get_owned_period(db, user, data["period_id"])
    adjustment = CorporateTaxAdjustment(owner_id=user.id, **data)
    repository.add(db, adjustment)
    db.commit()
    db.refresh(adjustment)
    return _adjustment_detail(adjustment)


def get_adjustment(db: Session, user: User, adjustment_id: str) -> CorporateTaxAdjustmentDetailResponse:
    return _adjustment_detail(_get_owned_adjustment(db, user, adjustment_id))


def update_adjustment(db: Session, user: User, adjustment_id: str, payload: CorporateTaxAdjustmentUpdateRequest) -> CorporateTaxAdjustmentDetailResponse:
    adjustment = _get_owned_adjustment(db, user, adjustment_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(adjustment, field, value)
    db.commit()
    db.refresh(adjustment)
    return _adjustment_detail(adjustment)


def delete_adjustment(db: Session, user: User, adjustment_id: str) -> None:
    adjustment = _get_owned_adjustment(db, user, adjustment_id)
    repository.delete_record(db, adjustment)
    db.commit()


def list_obligations(db: Session, user: User) -> list[CorporateTaxObligationSummaryResponse]:
    return [_obligation_summary(obligation) for obligation in repository.list_obligations(db, user.id)]


def create_obligation(db: Session, user: User, payload: CorporateTaxObligationCreateRequest) -> CorporateTaxObligationDetailResponse:
    data = payload.model_dump()
    _get_owned_period(db, user, data["period_id"])
    obligation = CorporateTaxObligation(owner_id=user.id, **data)
    repository.add(db, obligation)
    db.commit()
    db.refresh(obligation)
    return _obligation_detail(obligation)


def get_obligation(db: Session, user: User, obligation_id: str) -> CorporateTaxObligationDetailResponse:
    return _obligation_detail(_get_owned_obligation(db, user, obligation_id))


def update_obligation(db: Session, user: User, obligation_id: str, payload: CorporateTaxObligationUpdateRequest) -> CorporateTaxObligationDetailResponse:
    obligation = _get_owned_obligation(db, user, obligation_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obligation, field, value)
    db.commit()
    db.refresh(obligation)
    return _obligation_detail(obligation)


def complete_obligation(db: Session, user: User, obligation_id: str) -> CorporateTaxObligationDetailResponse:
    obligation = _get_owned_obligation(db, user, obligation_id)
    obligation.status = "completed_externally"
    obligation.completion_date = obligation.completion_date or _today_key()
    db.commit()
    db.refresh(obligation)
    return _obligation_detail(obligation)


def delete_obligation(db: Session, user: User, obligation_id: str) -> None:
    obligation = _get_owned_obligation(db, user, obligation_id)
    repository.delete_record(db, obligation)
    db.commit()


def get_dashboard(db: Session, user: User) -> CorporateTaxDashboardResponse:
    raw_periods = repository.list_periods(db, user.id)
    raw_adjustments = repository.list_adjustments(db, user.id)
    raw_obligations = repository.list_obligations(db, user.id)
    periods = [_period_summary(period) for period in raw_periods]
    adjustments = [_adjustment_summary(adjustment) for adjustment in raw_adjustments]
    obligations = [_obligation_summary(obligation) for obligation in raw_obligations]

    accounting_profit: dict[str, float] = defaultdict(float)
    net_adjustments: dict[str, float] = defaultdict(float)
    taxable_income: dict[str, float] = defaultdict(float)
    indicative_tax: dict[str, float] = defaultdict(float)
    category: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})

    for period in raw_periods:
        accounting_profit[period.currency_code] += period.accounting_profit
        net_adjustments[period.currency_code] += _net_adjustment(period)
        taxable_income[period.currency_code] += _calculated_taxable_income(period)
        indicative_tax[period.currency_code] += _indicative_tax_estimate(period)

    for adjustment in raw_adjustments:
        item = category[adjustment.category]
        item["amount"] += _signed_adjustment(adjustment)
        item["count"] += 1

    today = _today_key()
    return CorporateTaxDashboardResponse(
        periods=periods,
        adjustments=adjustments,
        obligations=obligations,
        total_periods=len(periods),
        draft_periods=len([period for period in periods if period.status == "draft"]),
        upcoming_filings=len([period for period in periods if period.filing_due_date and period.filing_due_date >= today and period.status not in {"filed_externally", "closed"}]),
        accounting_profit_by_currency=_money_items(accounting_profit),
        net_adjustments_by_currency=_money_items(net_adjustments),
        estimated_taxable_income_by_currency=_money_items(taxable_income),
        indicative_tax_estimate_by_currency=_money_items(indicative_tax),
        upcoming_obligations=len([obligation for obligation in obligations if obligation.status == "upcoming"]),
        overdue_obligations=len([obligation for obligation in obligations if obligation.status == "overdue"]),
        completed_obligations=len([obligation for obligation in obligations if obligation.status == "completed_externally"]),
        adjustment_breakdown_by_category=[
            CorporateTaxBreakdownResponse(label=label, amount=round(values["amount"], 2), count=int(values["count"]))
            for label, values in sorted(category.items())
        ],
        period_comparison=[
            CorporateTaxPeriodComparisonResponse(
                period_id=period.id,
                period_name=period.name,
                currency_code=period.currency_code,
                accounting_profit=period.accounting_profit,
                net_adjustment=_net_adjustment(period),
                calculated_taxable_income_estimate=_calculated_taxable_income(period),
                indicative_tax_estimate=_indicative_tax_estimate(period),
            )
            for period in raw_periods
        ],
        recent_activity=adjustments[:6],
        disclaimer=DISCLAIMER,
    )
