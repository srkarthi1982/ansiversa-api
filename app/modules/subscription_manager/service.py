from collections import defaultdict
from datetime import date
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.subscription_manager import repository
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord, SubscriptionRenewal
from app.modules.subscription_manager.schemas import (
    SubscriptionManagerBreakdownResponse,
    SubscriptionManagerCategoryCreateRequest,
    SubscriptionManagerCategoryDetailResponse,
    SubscriptionManagerCategorySummaryResponse,
    SubscriptionManagerCategoryUpdateRequest,
    SubscriptionManagerCurrencyTotalResponse,
    SubscriptionManagerDashboardResponse,
    SubscriptionManagerRenewalCreateRequest,
    SubscriptionManagerRenewalDetailResponse,
    SubscriptionManagerRenewalSummaryResponse,
    SubscriptionManagerRenewalUpdateRequest,
    SubscriptionManagerSubscriptionActionRequest,
    SubscriptionManagerSubscriptionCreateRequest,
    SubscriptionManagerSubscriptionDetailResponse,
    SubscriptionManagerSubscriptionSummaryResponse,
    SubscriptionManagerSubscriptionUpdateRequest,
    SubscriptionManagerTimelineResponse,
)

PREVIEW_LENGTH = 220
ACTIVE_STATUSES = {"active", "trial"}
FREQUENCY_TO_MONTHS = {"weekly": 12 / 52, "monthly": 1, "quarterly": 3, "semiannual": 6, "annual": 12, "custom": 1}


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


def _conflict(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def _get_owned_category(db: Session, user: User, category_id: str) -> SubscriptionCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Subscription category was not found.")
    return category


def _get_owned_subscription(db: Session, user: User, subscription_id: str) -> SubscriptionRecord:
    subscription = repository.get_subscription(db, subscription_id)
    if not subscription or subscription.owner_id != user.id:
        _not_found("Subscription was not found.")
    return subscription


def _get_owned_renewal(db: Session, user: User, renewal_id: str) -> SubscriptionRenewal:
    renewal = repository.get_renewal(db, renewal_id)
    if not renewal or renewal.owner_id != user.id:
        _not_found("Subscription renewal was not found.")
    return renewal


def _renewal_state(subscription: SubscriptionRecord) -> str:
    if subscription.status in {"cancelled", "expired"}:
        return subscription.status
    today = date.today().isoformat()
    if subscription.next_billing_date < today:
        return "overdue"
    return "upcoming"


def _monthly_amount(subscription: SubscriptionRecord) -> float:
    months = FREQUENCY_TO_MONTHS.get(subscription.billing_frequency, 1)
    if months <= 0:
        return subscription.billing_amount
    return subscription.billing_amount / months


def _category_summary(category: SubscriptionCategory) -> SubscriptionManagerCategorySummaryResponse:
    return SubscriptionManagerCategorySummaryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        notes_preview=_preview(category.notes),
        subscription_count=len(category.subscriptions),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _category_detail(category: SubscriptionCategory) -> SubscriptionManagerCategoryDetailResponse:
    return SubscriptionManagerCategoryDetailResponse(**_category_summary(category).model_dump(), notes=category.notes)


def _subscription_summary(subscription: SubscriptionRecord) -> SubscriptionManagerSubscriptionSummaryResponse:
    return SubscriptionManagerSubscriptionSummaryResponse(
        id=subscription.id,
        category_id=subscription.category_id,
        category_name=subscription.category.name if subscription.category else "Category",
        name=subscription.name,
        provider=subscription.provider,
        billing_amount=subscription.billing_amount,
        currency_code=subscription.currency_code,
        billing_frequency=subscription.billing_frequency,
        start_date=subscription.start_date,
        next_billing_date=subscription.next_billing_date,
        trial_end_date=subscription.trial_end_date,
        payment_method=subscription.payment_method,
        status=subscription.status,
        auto_renew=subscription.auto_renew,
        cancellation_notice_days=subscription.cancellation_notice_days,
        website=subscription.website,
        reference=subscription.reference,
        notes_preview=_preview(subscription.notes),
        renewal_state=_renewal_state(subscription),
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
    )


def _subscription_detail(subscription: SubscriptionRecord) -> SubscriptionManagerSubscriptionDetailResponse:
    return SubscriptionManagerSubscriptionDetailResponse(**_subscription_summary(subscription).model_dump(), notes=subscription.notes)


def _renewal_summary(renewal: SubscriptionRenewal) -> SubscriptionManagerRenewalSummaryResponse:
    subscription = renewal.subscription
    return SubscriptionManagerRenewalSummaryResponse(
        id=renewal.id,
        subscription_id=renewal.subscription_id,
        subscription_name=subscription.name if subscription else "Subscription",
        provider=subscription.provider if subscription else "",
        category_id=subscription.category_id if subscription else "",
        category_name=subscription.category.name if subscription and subscription.category else "Category",
        renewal_date=renewal.renewal_date,
        amount=renewal.amount,
        currency_code=renewal.currency_code,
        status=renewal.status,
        next_billing_date=renewal.next_billing_date,
        notes_preview=_preview(renewal.notes),
        created_at=renewal.created_at,
        updated_at=renewal.updated_at,
    )


def _renewal_detail(renewal: SubscriptionRenewal) -> SubscriptionManagerRenewalDetailResponse:
    return SubscriptionManagerRenewalDetailResponse(**_renewal_summary(renewal).model_dump(), notes=renewal.notes)


def _commit_or_conflict(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc


def list_categories(db: Session, user: User) -> list[SubscriptionManagerCategorySummaryResponse]:
    return [_category_summary(category) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: SubscriptionManagerCategoryCreateRequest) -> SubscriptionManagerCategoryDetailResponse:
    category = SubscriptionCategory(owner_id=user.id, **payload.model_dump())
    repository.add(db, category)
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_detail(category)


def get_category(db: Session, user: User, category_id: str) -> SubscriptionManagerCategoryDetailResponse:
    return _category_detail(_get_owned_category(db, user, category_id))


def update_category(db: Session, user: User, category_id: str, payload: SubscriptionManagerCategoryUpdateRequest) -> SubscriptionManagerCategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_detail(category)


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    if category.subscriptions:
        _conflict("This category is used by subscriptions. Reassign or delete them first.")
    repository.delete_record(db, category)
    db.commit()


def list_subscriptions(db: Session, user: User) -> list[SubscriptionManagerSubscriptionSummaryResponse]:
    return [_subscription_summary(item) for item in repository.list_subscriptions(db, user.id)]


def create_subscription(db: Session, user: User, payload: SubscriptionManagerSubscriptionCreateRequest) -> SubscriptionManagerSubscriptionDetailResponse:
    data = payload.model_dump()
    _get_owned_category(db, user, data["category_id"])
    subscription = SubscriptionRecord(owner_id=user.id, **data)
    repository.add(db, subscription)
    _commit_or_conflict(db, "A subscription with this provider and name already exists.")
    db.refresh(subscription)
    return _subscription_detail(subscription)


def get_subscription(db: Session, user: User, subscription_id: str) -> SubscriptionManagerSubscriptionDetailResponse:
    return _subscription_detail(_get_owned_subscription(db, user, subscription_id))


def update_subscription(db: Session, user: User, subscription_id: str, payload: SubscriptionManagerSubscriptionUpdateRequest) -> SubscriptionManagerSubscriptionDetailResponse:
    subscription = _get_owned_subscription(db, user, subscription_id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"]:
        _get_owned_category(db, user, data["category_id"])
    for field, value in data.items():
        setattr(subscription, field, value)
    _commit_or_conflict(db, "A subscription with this provider and name already exists.")
    db.refresh(subscription)
    return _subscription_detail(subscription)


def duplicate_subscription(db: Session, user: User, subscription_id: str) -> SubscriptionManagerSubscriptionDetailResponse:
    original = _get_owned_subscription(db, user, subscription_id)
    copy = SubscriptionRecord(
        owner_id=user.id,
        category_id=original.category_id,
        name=f"{original.name} copy {uuid4().hex[:6]}",
        provider=original.provider,
        billing_amount=original.billing_amount,
        currency_code=original.currency_code,
        billing_frequency=original.billing_frequency,
        start_date=original.start_date,
        next_billing_date=original.next_billing_date,
        trial_end_date=original.trial_end_date,
        payment_method=original.payment_method,
        status=original.status,
        auto_renew=original.auto_renew,
        cancellation_notice_days=original.cancellation_notice_days,
        website=original.website,
        reference=original.reference,
        notes=original.notes,
    )
    repository.add(db, copy)
    _commit_or_conflict(db, "A copied subscription with this provider and name already exists.")
    db.refresh(copy)
    return _subscription_detail(copy)


def delete_subscription(db: Session, user: User, subscription_id: str) -> None:
    subscription = _get_owned_subscription(db, user, subscription_id)
    repository.delete_record(db, subscription)
    db.commit()


def pause_subscription(db: Session, user: User, subscription_id: str, payload: SubscriptionManagerSubscriptionActionRequest) -> SubscriptionManagerSubscriptionDetailResponse:
    subscription = _get_owned_subscription(db, user, subscription_id)
    subscription.status = "paused"
    if payload.next_billing_date:
        subscription.next_billing_date = payload.next_billing_date
    if payload.notes:
        subscription.notes = payload.notes
    db.commit()
    db.refresh(subscription)
    return _subscription_detail(subscription)


def cancel_subscription(db: Session, user: User, subscription_id: str, payload: SubscriptionManagerSubscriptionActionRequest) -> SubscriptionManagerSubscriptionDetailResponse:
    subscription = _get_owned_subscription(db, user, subscription_id)
    subscription.status = "cancelled"
    subscription.auto_renew = False
    if payload.notes:
        subscription.notes = payload.notes
    db.commit()
    db.refresh(subscription)
    return _subscription_detail(subscription)


def list_renewals(db: Session, user: User) -> list[SubscriptionManagerRenewalSummaryResponse]:
    return [_renewal_summary(item) for item in repository.list_renewals(db, user.id)]


def create_renewal(db: Session, user: User, payload: SubscriptionManagerRenewalCreateRequest) -> SubscriptionManagerRenewalDetailResponse:
    data = payload.model_dump()
    subscription = _get_owned_subscription(db, user, data["subscription_id"])
    renewal = SubscriptionRenewal(owner_id=user.id, **data)
    if data.get("next_billing_date"):
        subscription.next_billing_date = data["next_billing_date"]
    repository.add(db, renewal)
    _commit_or_conflict(db, "A renewal record already exists for this subscription and date.")
    db.refresh(renewal)
    return _renewal_detail(renewal)


def get_renewal(db: Session, user: User, renewal_id: str) -> SubscriptionManagerRenewalDetailResponse:
    return _renewal_detail(_get_owned_renewal(db, user, renewal_id))


def update_renewal(db: Session, user: User, renewal_id: str, payload: SubscriptionManagerRenewalUpdateRequest) -> SubscriptionManagerRenewalDetailResponse:
    renewal = _get_owned_renewal(db, user, renewal_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(renewal, field, value)
    _commit_or_conflict(db, "A renewal record already exists for this subscription and date.")
    db.refresh(renewal)
    return _renewal_detail(renewal)


def delete_renewal(db: Session, user: User, renewal_id: str) -> None:
    renewal = _get_owned_renewal(db, user, renewal_id)
    repository.delete_record(db, renewal)
    db.commit()


def get_dashboard(db: Session, user: User) -> SubscriptionManagerDashboardResponse:
    category_records = repository.list_categories(db, user.id)
    subscription_records = repository.list_subscriptions(db, user.id)
    renewal_records = repository.list_renewals(db, user.id)
    categories = [_category_summary(category) for category in category_records]
    subscriptions = [_subscription_summary(subscription) for subscription in subscription_records]
    renewals = [_renewal_summary(renewal) for renewal in renewal_records]
    today = date.today().isoformat()
    active = [item for item in subscriptions if item.status in ACTIVE_STATUSES]
    upcoming = [item for item in active if item.next_billing_date >= today]
    overdue = [item for item in active if item.next_billing_date < today]
    totals: dict[str, dict[str, float]] = defaultdict(lambda: {"monthly": 0, "count": 0})
    by_category: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})
    by_frequency: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})
    monthly: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})

    for subscription in subscription_records:
        if subscription.status not in ACTIVE_STATUSES:
            continue
        monthly_amount = _monthly_amount(subscription)
        currency_code = subscription.currency_code
        category_name = subscription.category.name if subscription.category else "Category"
        total = totals[currency_code]
        total["monthly"] += monthly_amount
        total["count"] += 1
        by_category[(category_name, currency_code)]["amount"] += monthly_amount
        by_category[(category_name, currency_code)]["count"] += 1
        by_frequency[(subscription.billing_frequency, currency_code)]["amount"] += monthly_amount
        by_frequency[(subscription.billing_frequency, currency_code)]["count"] += 1
        monthly[(_month_key(subscription.next_billing_date), currency_code)]["amount"] += subscription.billing_amount
        monthly[(_month_key(subscription.next_billing_date), currency_code)]["count"] += 1

    return SubscriptionManagerDashboardResponse(
        categories=categories,
        subscriptions=subscriptions,
        renewals=renewals,
        total_active=len(active),
        trial_count=sum(1 for item in subscriptions if item.status == "trial"),
        upcoming_renewals=len(upcoming),
        overdue_renewals=len(overdue),
        currency_totals=[
            SubscriptionManagerCurrencyTotalResponse(currency_code=currency, monthly_amount=round(values["monthly"], 2), annual_amount=round(values["monthly"] * 12, 2), subscription_count=int(values["count"]))
            for currency, values in sorted(totals.items())
        ],
        spending_by_category=[
            SubscriptionManagerBreakdownResponse(label=label, currency_code=currency, amount=round(values["amount"], 2), count=int(values["count"]))
            for (label, currency), values in sorted(by_category.items())
        ],
        spending_by_frequency=[
            SubscriptionManagerBreakdownResponse(label=label, currency_code=currency, amount=round(values["amount"], 2), count=int(values["count"]))
            for (label, currency), values in sorted(by_frequency.items())
        ],
        monthly_activity=[
            SubscriptionManagerTimelineResponse(month=month, currency_code=currency, amount=round(values["amount"], 2), count=int(values["count"]))
            for (month, currency), values in sorted(monthly.items(), reverse=True)
        ],
        recent_activity=renewals[:8],
    )
