from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from inspect import getmembers, isfunction
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.subscription_manager import repository
from app.modules.subscription_manager.models import SubscriptionRecord
from app.modules.subscription_manager.service import ACTIVE_STATUSES, FREQUENCY_TO_MONTHS

APP_ID = "subscription_manager"
APP_SCOPE = "app:subscription_manager"
CAPABILITY_VERSION = "1.0.0"
MAX_RESULT_LIMIT = 50
AUTHORIZATION_MAX_AGE = timedelta(minutes=15)


class SubscriptionAstraCapabilityError(ValueError):
    pass


class SubscriptionAstraCapabilityStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class SubscriptionAstraResultStatus(StrEnum):
    OK = "ok"
    EMPTY = "empty"
    REJECTED = "rejected"
    UNSUPPORTED = "unsupported"


class SubscriptionAstraResultKind(StrEnum):
    COUNT = "count"
    LIST = "list"
    HIGHEST_COST = "highest_cost"
    TOTALS_BY_CURRENCY = "totals_by_currency"
    GROUP_BY_CATEGORY = "group_by_category"
    VALIDATION = "validation"


class SubscriptionAstraParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Literal["days", "status", "category"] = Field(min_length=1, max_length=40)
    value: int | str = Field(union_mode="left_to_right")


class SubscriptionAstraCapabilityDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    app_identity: Literal["subscription_manager"]
    status: SubscriptionAstraCapabilityStatus
    purpose: str
    allowed_parameters: tuple[str, ...]
    maximum_result_count: int
    result_kind: SubscriptionAstraResultKind

    @model_validator(mode="after")
    def validate_definition(self) -> "SubscriptionAstraCapabilityDefinition":
        if len(self.allowed_parameters) != len(set(self.allowed_parameters)):
            raise SubscriptionAstraCapabilityError("Capability parameter names must be unique.")
        return self


class SubscriptionAstraAuthorizationReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    authorization_id: str = Field(min_length=8, max_length=160)
    capability_id: str
    capability_version: str
    app_scope: Literal["app:subscription_manager"]
    decision_status: Literal["authorized_metadata_only"]
    authenticated_principal_reference: str = Field(min_length=3, max_length=160)
    issued_at: datetime
    expires_at: datetime | None = None
    production_authorization_state: Literal["not_approved"] = "not_approved"

    @model_validator(mode="after")
    def validate_authorization(self) -> "SubscriptionAstraAuthorizationReference":
        _ensure_aware(self.issued_at, "Authorization issuance")
        if self.expires_at is not None:
            _ensure_aware(self.expires_at, "Authorization expiration")
            if self.expires_at <= self.issued_at:
                raise SubscriptionAstraCapabilityError("Authorization expiration must follow issuance.")
        return self


class SubscriptionAstraReadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    app_identity: Literal["subscription_manager"]
    request_reference: str = Field(min_length=8, max_length=160)
    requested_maximum_result_count: int = Field(ge=1, le=MAX_RESULT_LIMIT)
    authorization_reference: SubscriptionAstraAuthorizationReference
    purpose: str = Field(min_length=8, max_length=120)
    observed_at: datetime
    parameters: tuple[SubscriptionAstraParameter, ...] = ()
    plan_reference: str | None = Field(default=None, max_length=160)
    caller_supplied_user_id: str | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_request(self) -> "SubscriptionAstraReadRequest":
        _ensure_aware(self.observed_at, "Observed timestamp")
        names = tuple(parameter.name for parameter in self.parameters)
        if len(names) != len(set(names)):
            raise SubscriptionAstraCapabilityError("Duplicate capability parameters are prohibited.")
        if self.caller_supplied_user_id is not None:
            raise SubscriptionAstraCapabilityError("Caller-supplied user IDs cannot establish subscription ownership.")
        auth = self.authorization_reference
        if auth.capability_id != self.capability_id or auth.capability_version != self.capability_version:
            raise SubscriptionAstraCapabilityError("Authorization reference does not match requested capability.")
        if auth.expires_at is not None and auth.expires_at <= self.observed_at:
            raise SubscriptionAstraCapabilityError("Authorization reference is expired.")
        if self.observed_at - auth.issued_at > AUTHORIZATION_MAX_AGE:
            raise SubscriptionAstraCapabilityError("Authorization reference is stale.")
        return self


class SubscriptionAstraReadResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    status: SubscriptionAstraResultStatus
    result_kind: SubscriptionAstraResultKind
    records: tuple[dict[str, Any], ...] = ()
    summary: dict[str, Any] = Field(default_factory=dict)
    currency: str | None = None
    calculation_basis: str
    record_count: int
    returned_count: int
    truncated: bool
    reason_codes: tuple[str, ...]
    observed_at: datetime
    app_scope: Literal["app:subscription_manager"]
    user_scope_state: Literal["authenticated_user_only"]
    authorization_state: Literal["authorized_metadata_only"]
    production_authorization_state: Literal["not_approved"]


def capability_catalog() -> tuple[SubscriptionAstraCapabilityDefinition, ...]:
    return (
        _capability("subscription.count_all", "Count all authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.COUNT),
        _capability("subscription.count_active", "Count active authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.COUNT),
        _capability("subscription.list_active", "List active authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.highest_cost", "Return the highest normalized monthly cost subscription.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.HIGHEST_COST),
        _capability("subscription.total_recurring_cost", "Return recurring totals grouped by currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.TOTALS_BY_CURRENCY),
        _capability("subscription.monthly_cost_estimate", "Return estimated monthly totals grouped by currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.TOTALS_BY_CURRENCY),
        _capability("subscription.renewing_this_month", "List active subscriptions renewing in the observed month.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.renewing_within_days", "List active subscriptions renewing within an allowed day window.", ("days",), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.overdue_renewals", "List active subscriptions past their expected renewal date.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.group_by_category", "Return active subscription totals grouped by category and currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.GROUP_BY_CATEGORY),
    )


def execute_read_capability(db: Session, authenticated_user: User, request: SubscriptionAstraReadRequest) -> SubscriptionAstraReadResult:
    if authenticated_user is None or not getattr(authenticated_user, "id", None):
        raise SubscriptionAstraCapabilityError("Authenticated subscription owner is required.")
    definition = _definition_for(request.capability_id)
    _validate_request_against_definition(request, definition)
    subscriptions = repository.list_subscriptions(db, authenticated_user.id)
    owned = [item for item in subscriptions if item.owner_id == authenticated_user.id]
    if len(owned) != len(subscriptions):
        raise SubscriptionAstraCapabilityError("Subscription repository returned records outside authenticated owner scope.")

    active = [item for item in owned if item.status in ACTIVE_STATUSES]
    reason_codes = ["app_owned_read", "authenticated_user_scope", "production_not_approved"]

    if request.capability_id == "subscription.count_all":
        return _result(request, definition, summary={"answer_type": "count", "subject": "subscriptions", "count": len(owned)}, record_count=len(owned), reason_codes=reason_codes)
    if request.capability_id == "subscription.count_active":
        return _result(request, definition, summary={"answer_type": "count", "subject": "active subscriptions", "count": len(active)}, record_count=len(active), reason_codes=reason_codes)
    if request.capability_id == "subscription.list_active":
        return _record_result(request, definition, _sort_by_next_billing(active), reason_codes)
    if request.capability_id == "subscription.highest_cost":
        return _highest_cost(request, definition, active, reason_codes)
    if request.capability_id in {"subscription.total_recurring_cost", "subscription.monthly_cost_estimate"}:
        return _totals_by_currency(request, definition, active, reason_codes)
    if request.capability_id == "subscription.renewing_this_month":
        return _record_result(request, definition, _renewing_this_month(active, request.observed_at), reason_codes)
    if request.capability_id == "subscription.renewing_within_days":
        days = _int_parameter(request, "days", default=30)
        if days < 1 or days > 366:
            raise SubscriptionAstraCapabilityError("Renewal day window must be between 1 and 366.")
        return _record_result(request, definition, _renewing_within_days(active, request.observed_at, days), reason_codes)
    if request.capability_id == "subscription.overdue_renewals":
        return _record_result(request, definition, _overdue(active, request.observed_at), reason_codes)
    if request.capability_id == "subscription.group_by_category":
        return _group_by_category(request, definition, active, reason_codes)
    raise SubscriptionAstraCapabilityError("Unsupported Subscription Manager capability.")


def deterministic_answer(result: SubscriptionAstraReadResult) -> dict[str, Any]:
    if result.status in {SubscriptionAstraResultStatus.REJECTED, SubscriptionAstraResultStatus.UNSUPPORTED}:
        return {"answer_type": "unavailable", "reason_codes": list(result.reason_codes)}
    if result.summary:
        return dict(result.summary)
    return {
        "answer_type": result.result_kind.value,
        "records": [dict(record) for record in result.records],
        "record_count": result.record_count,
        "returned_count": result.returned_count,
        "truncated": result.truncated,
    }


def mutation_surface_report() -> dict[str, Any]:
    forbidden = ("add", "create", "update", "delete", "duplicate", "pause", "cancel", "commit", "flush", "merge")
    functions = tuple(name for name, value in getmembers(__import__(__name__, fromlist=["*"]), isfunction) if not name.startswith("_"))
    detected = tuple(name for name in functions if any(term in name.lower() for term in forbidden))
    return {
        "module": __name__,
        "forbidden_public_functions": detected,
        "mutation_surface_absent": detected == (),
    }


def _capability(capability_id: str, purpose: str, parameters: tuple[str, ...], maximum: int, kind: SubscriptionAstraResultKind) -> SubscriptionAstraCapabilityDefinition:
    return SubscriptionAstraCapabilityDefinition(
        capability_id=capability_id,
        capability_version=CAPABILITY_VERSION,
        app_identity=APP_ID,
        status=SubscriptionAstraCapabilityStatus.ENABLED,
        purpose=purpose,
        allowed_parameters=parameters,
        maximum_result_count=maximum,
        result_kind=kind,
    )


def _definition_for(capability_id: str) -> SubscriptionAstraCapabilityDefinition:
    for definition in capability_catalog():
        if definition.capability_id == capability_id:
            return definition
    raise SubscriptionAstraCapabilityError("Unsupported Subscription Manager capability.")


def _validate_request_against_definition(request: SubscriptionAstraReadRequest, definition: SubscriptionAstraCapabilityDefinition) -> None:
    if definition.status is not SubscriptionAstraCapabilityStatus.ENABLED:
        raise SubscriptionAstraCapabilityError("Subscription Manager capability is disabled.")
    if request.app_identity != APP_ID or request.authorization_reference.app_scope != APP_SCOPE:
        raise SubscriptionAstraCapabilityError("Foreign app scope is prohibited.")
    if request.capability_version != definition.capability_version:
        raise SubscriptionAstraCapabilityError("Unsupported Subscription Manager capability version.")
    requested_parameters = {parameter.name for parameter in request.parameters}
    if not requested_parameters.issubset(definition.allowed_parameters):
        raise SubscriptionAstraCapabilityError("Unsupported capability parameter.")
    if request.requested_maximum_result_count > definition.maximum_result_count:
        raise SubscriptionAstraCapabilityError("Requested result limit exceeds capability bound.")


def _result(
    request: SubscriptionAstraReadRequest,
    definition: SubscriptionAstraCapabilityDefinition,
    *,
    summary: dict[str, Any],
    record_count: int,
    records: tuple[dict[str, Any], ...] = (),
    reason_codes: list[str],
) -> SubscriptionAstraReadResult:
    return SubscriptionAstraReadResult(
        capability_id=request.capability_id,
        capability_version=request.capability_version,
        status=SubscriptionAstraResultStatus.OK if record_count else SubscriptionAstraResultStatus.EMPTY,
        result_kind=definition.result_kind,
        records=records,
        summary=summary,
        currency=summary.get("currency"),
        calculation_basis=_calculation_basis(),
        record_count=record_count,
        returned_count=len(records),
        truncated=False,
        reason_codes=tuple(reason_codes),
        observed_at=request.observed_at,
        app_scope=APP_SCOPE,
        user_scope_state="authenticated_user_only",
        authorization_state="authorized_metadata_only",
        production_authorization_state="not_approved",
    )


def _record_result(
    request: SubscriptionAstraReadRequest,
    definition: SubscriptionAstraCapabilityDefinition,
    subscriptions: list[SubscriptionRecord],
    reason_codes: list[str],
) -> SubscriptionAstraReadResult:
    limit = request.requested_maximum_result_count
    truncated = len(subscriptions) > limit
    records = tuple(_subscription_record(item) for item in subscriptions[:limit])
    return SubscriptionAstraReadResult(
        capability_id=request.capability_id,
        capability_version=request.capability_version,
        status=SubscriptionAstraResultStatus.OK if subscriptions else SubscriptionAstraResultStatus.EMPTY,
        result_kind=definition.result_kind,
        records=records,
        summary={"answer_type": definition.result_kind.value, "record_count": len(subscriptions), "returned_count": len(records), "truncated": truncated},
        calculation_basis=_calculation_basis(),
        record_count=len(subscriptions),
        returned_count=len(records),
        truncated=truncated,
        reason_codes=tuple([*reason_codes, "bounded_result"] if truncated else reason_codes),
        observed_at=request.observed_at,
        app_scope=APP_SCOPE,
        user_scope_state="authenticated_user_only",
        authorization_state="authorized_metadata_only",
        production_authorization_state="not_approved",
    )


def _highest_cost(request: SubscriptionAstraReadRequest, definition: SubscriptionAstraCapabilityDefinition, subscriptions: list[SubscriptionRecord], reason_codes: list[str]) -> SubscriptionAstraReadResult:
    ordered = sorted(subscriptions, key=lambda item: (-_monthly_decimal(item), item.name.lower(), item.provider.lower(), item.id))
    if not ordered:
        return _result(request, definition, summary={"answer_type": "highest_cost", "subscription": None}, record_count=0, reason_codes=reason_codes)
    top = ordered[0]
    record = _subscription_record(top) | {"monthly_estimate": _money(_monthly_decimal(top))}
    return _result(request, definition, summary={"answer_type": "highest_cost", "subscription": record}, record_count=1, records=(record,), reason_codes=reason_codes)


def _totals_by_currency(request: SubscriptionAstraReadRequest, definition: SubscriptionAstraCapabilityDefinition, subscriptions: list[SubscriptionRecord], reason_codes: list[str]) -> SubscriptionAstraReadResult:
    totals: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"monthly_estimate": Decimal("0.00"), "subscription_count": 0})
    for item in subscriptions:
        currency = _currency(item.currency_code)
        totals[currency]["monthly_estimate"] = totals[currency]["monthly_estimate"] + _monthly_decimal(item)
        totals[currency]["subscription_count"] = int(totals[currency]["subscription_count"]) + 1
    records = tuple(
        {
            "currency": currency,
            "monthly_estimate": _money(values["monthly_estimate"]),
            "annual_estimate": _money(values["monthly_estimate"] * Decimal("12")),
            "subscription_count": values["subscription_count"],
        }
        for currency, values in sorted(totals.items())
    )
    return _result(
        request,
        definition,
        summary={"answer_type": "totals_by_currency", "totals": list(records), "mixed_currency_policy": "grouped_totals_no_fx_conversion"},
        record_count=len(records),
        records=records,
        reason_codes=[*reason_codes, "currency_grouped_no_fx"],
    )


def _group_by_category(request: SubscriptionAstraReadRequest, definition: SubscriptionAstraCapabilityDefinition, subscriptions: list[SubscriptionRecord], reason_codes: list[str]) -> SubscriptionAstraReadResult:
    grouped: dict[tuple[str, str], dict[str, Decimal | int]] = defaultdict(lambda: {"monthly_estimate": Decimal("0.00"), "subscription_count": 0})
    for item in subscriptions:
        category = item.category.name if item.category else "Category"
        key = (category, _currency(item.currency_code))
        grouped[key]["monthly_estimate"] = grouped[key]["monthly_estimate"] + _monthly_decimal(item)
        grouped[key]["subscription_count"] = int(grouped[key]["subscription_count"]) + 1
    records = tuple(
        {
            "category": category,
            "currency": currency,
            "monthly_estimate": _money(values["monthly_estimate"]),
            "subscription_count": values["subscription_count"],
        }
        for (category, currency), values in sorted(grouped.items())
    )
    return _result(request, definition, summary={"answer_type": "group_by_category", "groups": list(records)}, record_count=len(records), records=records, reason_codes=reason_codes)


def _subscription_record(subscription: SubscriptionRecord) -> dict[str, Any]:
    return {
        "id": subscription.id,
        "name": subscription.name,
        "provider": subscription.provider,
        "category": subscription.category.name if subscription.category else "Category",
        "billing_amount": _money(Decimal(str(subscription.billing_amount))),
        "currency": _currency(subscription.currency_code),
        "billing_frequency": subscription.billing_frequency,
        "next_billing_date": subscription.next_billing_date,
        "status": subscription.status,
        "auto_renew": subscription.auto_renew,
    }


def _sort_by_next_billing(subscriptions: list[SubscriptionRecord]) -> list[SubscriptionRecord]:
    return sorted(subscriptions, key=lambda item: (_date_or_max(item.next_billing_date), item.name.lower(), item.provider.lower(), item.id))


def _renewing_this_month(subscriptions: list[SubscriptionRecord], observed_at: datetime) -> list[SubscriptionRecord]:
    observed = observed_at.date()
    return _sort_by_next_billing(
        [
            item
            for item in subscriptions
            if (parsed := _parse_date(item.next_billing_date))
            and parsed >= observed
            and parsed.year == observed.year
            and parsed.month == observed.month
        ]
    )


def _renewing_within_days(subscriptions: list[SubscriptionRecord], observed_at: datetime, days: int) -> list[SubscriptionRecord]:
    observed = observed_at.date()
    end = observed + timedelta(days=days)
    return _sort_by_next_billing([item for item in subscriptions if (parsed := _parse_date(item.next_billing_date)) and observed <= parsed <= end])


def _overdue(subscriptions: list[SubscriptionRecord], observed_at: datetime) -> list[SubscriptionRecord]:
    observed = observed_at.date()
    return _sort_by_next_billing([item for item in subscriptions if (parsed := _parse_date(item.next_billing_date)) and parsed < observed])


def _monthly_decimal(subscription: SubscriptionRecord) -> Decimal:
    months = Decimal(str(FREQUENCY_TO_MONTHS.get(subscription.billing_frequency, 1)))
    amount = Decimal(str(subscription.billing_amount))
    if months <= 0:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return (amount / months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _int_parameter(request: SubscriptionAstraReadRequest, name: str, *, default: int) -> int:
    for parameter in request.parameters:
        if parameter.name == name:
            if not isinstance(parameter.value, int):
                raise SubscriptionAstraCapabilityError(f"{name} parameter must be an integer.")
            return parameter.value
    return default


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _date_or_max(value: str | None) -> date:
    return _parse_date(value) or date.max


def _currency(value: str | None) -> str:
    return (value or "USD").strip().upper() or "USD"


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _calculation_basis() -> str:
    return "active statuses are active/trial; weekly=amount*52/12, monthly=amount, quarterly=amount/3, semiannual=amount/6, annual=amount/12, custom=amount; totals are grouped by currency without FX conversion"


def _ensure_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise SubscriptionAstraCapabilityError(f"{label} timestamp must be timezone-aware.")
