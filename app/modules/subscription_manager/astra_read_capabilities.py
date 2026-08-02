from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from hashlib import sha256
from inspect import getmembers, isfunction
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference
from app.modules.astra_ai.read_access_authorization import (
    AstraCrossAppPolicy,
    AstraNamedReadCapability,
    AstraReadCapabilityStatus,
    AstraReadPurpose,
    AstraReadSensitivity,
)
from app.modules.auth.models import User
from app.modules.subscription_manager import repository
from app.modules.subscription_manager.models import SubscriptionRecord
from app.modules.subscription_manager.service import ACTIVE_STATUSES, FREQUENCY_TO_MONTHS

APP_ID = "subscription_manager"
APP_SCOPE = "app:subscription_manager"
TENANT_SCOPE_NOT_APPLICABLE = "tenant:not_applicable"
CAPABILITY_VERSION = "1.0.0"
MAX_RESULT_LIMIT = 50
AUTHORIZATION_MAX_AGE = timedelta(minutes=15)
_SUBSCRIPTION_ASTRA_GRANT_AUTHORITY = object()


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
    HIGHEST_COST_BY_CURRENCY = "highest_cost_by_currency"
    RECURRING_TOTALS = "recurring_totals"
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
    governance_decision_reference: str = Field(min_length=8, max_length=160)
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


class SubscriptionAstraOwnerAcceptance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    acceptance_id: str = Field(pattern=r"^sub_astra_accept_[a-f0-9]{32}$")
    authenticated_user_id: str = Field(min_length=1, max_length=160)
    authenticated_principal_reference: str = Field(min_length=3, max_length=160)
    app_identity: Literal["subscription_manager"]
    app_scope: Literal["app:subscription_manager"]
    capability_id: str
    capability_version: str
    read_capability_id: str
    request_reference: str = Field(min_length=8, max_length=160)
    accepted_subject_scope: Literal["current_user"]
    accepted_tenant_scope: Literal["tenant:not_applicable"]
    accepted_record_scope: Literal["owned_records"]
    accepted_field_references: tuple[str, ...] = Field(min_length=1, max_length=50)
    accepted_purpose: AstraReadPurpose
    accepted_parameters: tuple[SubscriptionAstraParameter, ...] = ()
    maximum_result_count: int = Field(ge=1, le=MAX_RESULT_LIMIT)
    issued_at: datetime
    expires_at: datetime
    observed_at: datetime
    production_authorization_state: Literal["not_approved"] = "not_approved"

    @model_validator(mode="after")
    def validate_acceptance(self) -> "SubscriptionAstraOwnerAcceptance":
        _ensure_aware(self.issued_at, "Owner acceptance issuance")
        _ensure_aware(self.expires_at, "Owner acceptance expiration")
        _ensure_aware(self.observed_at, "Owner acceptance observation")
        if self.expires_at <= self.issued_at:
            raise SubscriptionAstraCapabilityError("Owner acceptance expiration must follow issuance.")
        if self.expires_at <= self.observed_at:
            raise SubscriptionAstraCapabilityError("Owner acceptance cannot be expired at observation.")
        if self.observed_at - self.issued_at > AUTHORIZATION_MAX_AGE:
            raise SubscriptionAstraCapabilityError("Owner acceptance is stale.")
        if len(self.accepted_field_references) != len(set(self.accepted_field_references)):
            raise SubscriptionAstraCapabilityError("Owner acceptance fields must be unique.")
        if self.read_capability_id != read_capability_id_for_adapter(self.capability_id):
            raise SubscriptionAstraCapabilityError("Owner acceptance read capability does not match adapter capability.")
        return self


class SubscriptionAstraReadGrant(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    grant_id: str = Field(pattern=r"^sub_astra_grant_[a-f0-9]{32}$")
    authenticated_user_id: str = Field(min_length=1, max_length=160)
    capability_id: str
    capability_version: str
    app_scope: Literal["app:subscription_manager"]
    request_reference: str = Field(min_length=8, max_length=160)
    parameter_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    permitted_parameters: tuple[SubscriptionAstraParameter, ...] = ()
    maximum_result_count: int = Field(ge=1, le=MAX_RESULT_LIMIT)
    purpose: str = Field(min_length=8, max_length=120)
    astra_authorization_reference: SubscriptionAstraAuthorizationReference
    issued_at: datetime
    expires_at: datetime
    observed_at: datetime
    production_authorization_state: Literal["not_approved"] = "not_approved"

    @model_validator(mode="after")
    def validate_grant(self) -> "SubscriptionAstraReadGrant":
        _ensure_aware(self.issued_at, "Grant issuance")
        _ensure_aware(self.expires_at, "Grant expiration")
        _ensure_aware(self.observed_at, "Grant observed")
        if self.expires_at <= self.issued_at:
            raise SubscriptionAstraCapabilityError("Read grant expiration must follow issuance.")
        auth = self.astra_authorization_reference
        if auth.capability_id != self.capability_id or auth.capability_version != self.capability_version:
            raise SubscriptionAstraCapabilityError("Read grant does not match Astra authorization metadata.")
        if not auth.governance_decision_reference:
            raise SubscriptionAstraCapabilityError("Read grant requires Governance decision reference.")
        if auth.app_scope != self.app_scope:
            raise SubscriptionAstraCapabilityError("Read grant app scope does not match authorization metadata.")
        if self.parameter_digest != _parameter_digest(self.permitted_parameters):
            raise SubscriptionAstraCapabilityError("Read grant parameter digest does not match permitted parameters.")
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


class _SubscriptionAstraExecutionClock:
    def now(self) -> datetime:
        return _utc_now()


class SubscriptionAstraReadGrantIssuer:
    def __init__(self, *, _app_authority: object | None = None, capacity: int = 200) -> None:
        if _app_authority is not _SUBSCRIPTION_ASTRA_GRANT_AUTHORITY:
            raise SubscriptionAstraCapabilityError("Subscription Manager read grant issuers require app-owned authority.")
        if capacity < 1 or capacity > 1000:
            raise SubscriptionAstraCapabilityError("Subscription Manager read grant issuer capacity is invalid.")
        self._capacity = capacity
        self._issued: dict[str, SubscriptionAstraReadGrant] = {}
        self._accepted: dict[str, SubscriptionAstraOwnerAcceptance] = {}
        self._consumed: set[str] = set()

    def issue_owner_acceptance(
        self,
        *,
        authenticated_user: User,
        principal_reference: str,
        capability_id: str,
        read_capability_id: str,
        request_reference: str,
        requested_fields: tuple[str, ...],
        requested_purpose: AstraReadPurpose,
        requested_maximum_result_count: int,
        parameters: tuple[SubscriptionAstraParameter, ...],
        observed_at: datetime,
        issued_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> SubscriptionAstraOwnerAcceptance:
        if authenticated_user is None or not getattr(authenticated_user, "id", None):
            raise SubscriptionAstraCapabilityError("Authenticated subscription owner is required for owner acceptance.")
        if len(self._accepted) >= self._capacity:
            raise SubscriptionAstraCapabilityError("Subscription Manager owner acceptance issuer capacity reached.")
        timestamp = issued_at or observed_at
        _ensure_aware(timestamp, "Owner acceptance issuance")
        _ensure_aware(observed_at, "Owner acceptance observation")
        if timestamp > observed_at:
            raise SubscriptionAstraCapabilityError("Owner acceptance issuance cannot follow request observation.")
        expiration = expires_at or timestamp + AUTHORIZATION_MAX_AGE
        _ensure_aware(expiration, "Owner acceptance expiration")
        _validate_principal_matches_user(principal_reference, authenticated_user.id)
        definition = _definition_for(capability_id)
        read_capability = _read_authorization_capability(definition)
        if read_capability.read_capability_id != read_capability_id:
            raise SubscriptionAstraCapabilityError("Owner acceptance read capability mismatch.")
        _validate_acceptance_against_definition(
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            requested_fields=requested_fields,
            requested_purpose=requested_purpose,
            requested_maximum_result_count=requested_maximum_result_count,
            parameters=parameters,
            definition=definition,
            read_capability=read_capability,
        )
        acceptance = SubscriptionAstraOwnerAcceptance(
            acceptance_id=f"sub_astra_accept_{uuid4().hex}",
            authenticated_user_id=authenticated_user.id,
            authenticated_principal_reference=principal_reference,
            app_identity=APP_ID,
            app_scope=APP_SCOPE,
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            read_capability_id=read_capability_id,
            request_reference=request_reference,
            accepted_subject_scope=read_capability.allowed_subject_scope,
            accepted_tenant_scope=read_capability.allowed_tenant_scope,
            accepted_record_scope=read_capability.allowed_record_scope,
            accepted_field_references=requested_fields,
            accepted_purpose=requested_purpose,
            accepted_parameters=parameters,
            maximum_result_count=requested_maximum_result_count,
            issued_at=timestamp,
            expires_at=expiration,
            observed_at=observed_at,
        )
        self._accepted[acceptance.acceptance_id] = acceptance
        return acceptance

    def validates_owner_acceptance(
        self,
        acceptance: Any,
        *,
        authenticated_user: User,
        observed_at: datetime,
    ) -> bool:
        _ensure_aware(observed_at, "Owner acceptance validation")
        if not isinstance(acceptance, SubscriptionAstraOwnerAcceptance):
            return False
        if self._accepted.get(acceptance.acceptance_id) is not acceptance:
            return False
        if observed_at < acceptance.issued_at or observed_at < acceptance.observed_at:
            return False
        if acceptance.expires_at <= observed_at:
            return False
        if acceptance.app_identity != APP_ID or acceptance.app_scope != APP_SCOPE:
            return False
        if authenticated_user is None or acceptance.authenticated_user_id != getattr(authenticated_user, "id", None):
            return False
        try:
            _validate_principal_matches_user(acceptance.authenticated_principal_reference, acceptance.authenticated_user_id)
            definition = _definition_for(acceptance.capability_id)
            _validate_acceptance_against_definition(
                capability_id=acceptance.capability_id,
                capability_version=acceptance.capability_version,
                requested_fields=acceptance.accepted_field_references,
                requested_purpose=acceptance.accepted_purpose,
                requested_maximum_result_count=acceptance.maximum_result_count,
                parameters=acceptance.accepted_parameters,
                definition=definition,
                read_capability=_read_authorization_capability(definition),
            )
        except SubscriptionAstraCapabilityError:
            return False
        return True

    def issue(
        self,
        *,
        authenticated_user: User,
        request: SubscriptionAstraReadRequest,
        issued_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> SubscriptionAstraReadGrant:
        if authenticated_user is None or not getattr(authenticated_user, "id", None):
            raise SubscriptionAstraCapabilityError("Authenticated subscription owner is required for read grant issuance.")
        if len(self._issued) >= self._capacity:
            raise SubscriptionAstraCapabilityError("Subscription Manager read grant issuer capacity reached.")
        timestamp = issued_at or request.observed_at
        _ensure_aware(timestamp, "Grant issuance")
        if timestamp > request.observed_at:
            raise SubscriptionAstraCapabilityError("Read grant issuance cannot follow request observation.")
        expiration = expires_at or min(
            request.authorization_reference.expires_at or (timestamp + AUTHORIZATION_MAX_AGE),
            timestamp + AUTHORIZATION_MAX_AGE,
        )
        _ensure_aware(expiration, "Grant expiration")
        _validate_principal_matches_user(request.authorization_reference.authenticated_principal_reference, authenticated_user.id)
        definition = _definition_for(request.capability_id)
        _validate_request_against_definition(request, definition)
        grant = SubscriptionAstraReadGrant(
            grant_id=f"sub_astra_grant_{uuid4().hex}",
            authenticated_user_id=authenticated_user.id,
            capability_id=request.capability_id,
            capability_version=request.capability_version,
            app_scope=APP_SCOPE,
            request_reference=request.request_reference,
            parameter_digest=_parameter_digest(request.parameters),
            permitted_parameters=request.parameters,
            maximum_result_count=request.requested_maximum_result_count,
            purpose=request.purpose,
            astra_authorization_reference=request.authorization_reference,
            issued_at=timestamp,
            expires_at=expiration,
            observed_at=request.observed_at,
        )
        self._issued[grant.grant_id] = grant
        return grant

    def validates(self, grant: Any, *, authenticated_user: User, observed_at: datetime) -> bool:
        _ensure_aware(observed_at, "Grant execution")
        if not isinstance(grant, SubscriptionAstraReadGrant):
            return False
        if self._issued.get(grant.grant_id) is not grant:
            return False
        if grant.grant_id in self._consumed:
            return False
        if observed_at < grant.issued_at or observed_at < grant.observed_at:
            return False
        if grant.expires_at <= observed_at:
            return False
        if authenticated_user is None or grant.authenticated_user_id != getattr(authenticated_user, "id", None):
            return False
        try:
            _validate_principal_matches_user(grant.astra_authorization_reference.authenticated_principal_reference, grant.authenticated_user_id)
        except SubscriptionAstraCapabilityError:
            return False
        return True

    def consume(self, grant: SubscriptionAstraReadGrant) -> None:
        if self._issued.get(grant.grant_id) is not grant or grant.grant_id in self._consumed:
            raise SubscriptionAstraCapabilityError("Subscription Manager read grant cannot be consumed.")
        self._consumed.add(grant.grant_id)


_SUBSCRIPTION_ASTRA_GRANT_ISSUER = SubscriptionAstraReadGrantIssuer(
    _app_authority=_SUBSCRIPTION_ASTRA_GRANT_AUTHORITY
)
_SUBSCRIPTION_ASTRA_EXECUTION_CLOCK = _SubscriptionAstraExecutionClock()


def capability_catalog() -> tuple[SubscriptionAstraCapabilityDefinition, ...]:
    return (
        _capability("subscription.count_all", "Count all authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.COUNT),
        _capability("subscription.count_active", "Count active authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.COUNT),
        _capability("subscription.list_active", "List active authenticated user subscriptions.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.highest_cost", "Return the highest normalized monthly cost subscription within each currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.HIGHEST_COST_BY_CURRENCY),
        _capability("subscription.total_recurring_cost", "Return raw recurring totals grouped by currency and billing frequency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.RECURRING_TOTALS),
        _capability("subscription.monthly_cost_estimate", "Return estimated monthly totals grouped by currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.TOTALS_BY_CURRENCY),
        _capability("subscription.renewing_this_month", "List active subscriptions renewing in the observed month.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.renewing_within_days", "List active subscriptions renewing within an allowed day window.", ("days",), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.overdue_renewals", "List active subscriptions past their expected renewal date.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.LIST),
        _capability("subscription.group_by_category", "Return active subscription totals grouped by category and currency.", (), MAX_RESULT_LIMIT, SubscriptionAstraResultKind.GROUP_BY_CATEGORY),
    )


def read_authorization_capabilities() -> tuple[AstraNamedReadCapability, ...]:
    return tuple(_read_authorization_capability(definition) for definition in capability_catalog())


def read_capability_id_for_adapter(adapter_capability_id: str) -> str:
    _definition_for(adapter_capability_id)
    return f"read_cap_{adapter_capability_id.replace('.', '_')}_0001"


def default_read_fields_for_adapter(adapter_capability_id: str) -> tuple[str, ...]:
    return _read_fields_for(_definition_for(adapter_capability_id))


def default_read_purpose_for_adapter(adapter_capability_id: str) -> AstraReadPurpose:
    definition = _definition_for(adapter_capability_id)
    if definition.result_kind is SubscriptionAstraResultKind.LIST:
        return AstraReadPurpose.USER_REQUESTED_LOOKUP
    if definition.result_kind in {
        SubscriptionAstraResultKind.RECURRING_TOTALS,
        SubscriptionAstraResultKind.TOTALS_BY_CURRENCY,
        SubscriptionAstraResultKind.GROUP_BY_CATEGORY,
    }:
        return AstraReadPurpose.GOVERNED_AGGREGATION
    return AstraReadPurpose.USER_REQUESTED_SUMMARY


def default_read_grant_issuer() -> SubscriptionAstraReadGrantIssuer:
    return _SUBSCRIPTION_ASTRA_GRANT_ISSUER


def issue_read_grant(*, authenticated_user: User, request: SubscriptionAstraReadRequest) -> SubscriptionAstraReadGrant:
    return _SUBSCRIPTION_ASTRA_GRANT_ISSUER.issue(authenticated_user=authenticated_user, request=request)


def issue_owner_acceptance(
    *,
    authenticated_user: User,
    principal_reference: str,
    capability_id: str,
    read_capability_id: str,
    request_reference: str,
    requested_fields: tuple[str, ...],
    requested_purpose: AstraReadPurpose,
    requested_maximum_result_count: int,
    parameters: tuple[SubscriptionAstraParameter, ...],
    observed_at: datetime,
) -> SubscriptionAstraOwnerAcceptance:
    return _SUBSCRIPTION_ASTRA_GRANT_ISSUER.issue_owner_acceptance(
        authenticated_user=authenticated_user,
        principal_reference=principal_reference,
        capability_id=capability_id,
        read_capability_id=read_capability_id,
        request_reference=request_reference,
        requested_fields=requested_fields,
        requested_purpose=requested_purpose,
        requested_maximum_result_count=requested_maximum_result_count,
        parameters=parameters,
        observed_at=observed_at,
    )


def execute_read_capability(
    db: Session,
    authenticated_user: User,
    grant: SubscriptionAstraReadGrant,
    *,
    grant_issuer: SubscriptionAstraReadGrantIssuer | None = None,
) -> SubscriptionAstraReadResult:
    if authenticated_user is None or not getattr(authenticated_user, "id", None):
        raise SubscriptionAstraCapabilityError("Authenticated subscription owner is required.")
    if grant_issuer is not None and grant_issuer is not _SUBSCRIPTION_ASTRA_GRANT_ISSUER:
        raise SubscriptionAstraCapabilityError("Foreign Subscription Manager read grant issuer is prohibited.")
    execution_time = _SUBSCRIPTION_ASTRA_EXECUTION_CLOCK.now()
    _ensure_aware(execution_time, "Grant execution")
    if not _SUBSCRIPTION_ASTRA_GRANT_ISSUER.validates(grant, authenticated_user=authenticated_user, observed_at=execution_time):
        raise SubscriptionAstraCapabilityError("Valid app-owned Subscription Manager read grant is required.")
    _SUBSCRIPTION_ASTRA_GRANT_ISSUER.consume(grant)
    request = _request_from_grant(grant)
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
    if request.capability_id == "subscription.total_recurring_cost":
        return _recurring_totals_by_currency_and_frequency(request, definition, active, reason_codes)
    if request.capability_id == "subscription.monthly_cost_estimate":
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


def _read_authorization_capability(definition: SubscriptionAstraCapabilityDefinition) -> AstraNamedReadCapability:
    fields = _read_fields_for(definition)
    return AstraNamedReadCapability(
        read_capability_id=read_capability_id_for_adapter(definition.capability_id),
        capability_name=definition.capability_id.replace(".", "_"),
        owning_app_id=APP_ID,
        owning_module="subscription_manager.astra_read_capabilities",
        version=definition.capability_version,
        status=(
            AstraReadCapabilityStatus.AVAILABLE
            if definition.status is SubscriptionAstraCapabilityStatus.ENABLED
            else AstraReadCapabilityStatus.DISABLED
        ),
        description=definition.purpose,
        allowed_purposes=_read_purposes_for(definition),
        sensitivity_classification=AstraReadSensitivity.PERSONAL,
        allowed_subject_scope="current_user",
        allowed_tenant_scope=TENANT_SCOPE_NOT_APPLICABLE,
        allowed_record_scope="owned_records",
        allowed_field_references=fields,
        required_field_references=fields,
        maximum_row_count=definition.maximum_result_count,
        maximum_time_range_days=366,
        timeout_class="short",
        cross_app_policy=AstraCrossAppPolicy.PROHIBITED,
        owner_service_acceptance_required=True,
        governance_requirement_references=(_read_requirement(),),
    )


def _read_purposes_for(definition: SubscriptionAstraCapabilityDefinition) -> tuple[AstraReadPurpose, ...]:
    if definition.result_kind is SubscriptionAstraResultKind.LIST:
        return (AstraReadPurpose.USER_REQUESTED_LOOKUP, AstraReadPurpose.USER_REQUESTED_SUMMARY)
    if definition.result_kind in {
        SubscriptionAstraResultKind.RECURRING_TOTALS,
        SubscriptionAstraResultKind.TOTALS_BY_CURRENCY,
        SubscriptionAstraResultKind.GROUP_BY_CATEGORY,
        SubscriptionAstraResultKind.HIGHEST_COST_BY_CURRENCY,
    }:
        return (AstraReadPurpose.USER_REQUESTED_SUMMARY, AstraReadPurpose.GOVERNED_AGGREGATION)
    return (AstraReadPurpose.USER_REQUESTED_SUMMARY,)


def _read_fields_for(definition: SubscriptionAstraCapabilityDefinition) -> tuple[str, ...]:
    common = ("subscription.status",)
    if definition.result_kind is SubscriptionAstraResultKind.COUNT:
        return ("subscription.count",)
    if definition.result_kind is SubscriptionAstraResultKind.LIST:
        return (
            "subscription.name",
            "subscription.provider",
            "subscription.category",
            "subscription.billing_amount",
            "subscription.currency",
            "subscription.billing_frequency",
            "subscription.next_billing_date",
            "subscription.status",
            "subscription.auto_renew",
        )
    if definition.result_kind is SubscriptionAstraResultKind.HIGHEST_COST_BY_CURRENCY:
        return (
            "subscription.name",
            "subscription.provider",
            "subscription.billing_amount",
            "subscription.currency",
            "subscription.billing_frequency",
            "subscription.monthly_estimate",
        )
    if definition.result_kind in {
        SubscriptionAstraResultKind.RECURRING_TOTALS,
        SubscriptionAstraResultKind.TOTALS_BY_CURRENCY,
    }:
        return (
            "subscription.currency",
            "subscription.billing_frequency",
            "subscription.recurring_amount",
            "subscription.monthly_estimate",
            "subscription.annual_estimate",
            "subscription.count",
        )
    if definition.result_kind is SubscriptionAstraResultKind.GROUP_BY_CATEGORY:
        return (
            "subscription.category",
            "subscription.currency",
            "subscription.monthly_estimate",
            "subscription.count",
        )
    return common


def _read_requirement() -> ConstitutionalRequirementReference:
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-CM-009",
        requirement_version="1.0.0",
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


def _validate_acceptance_against_definition(
    *,
    capability_id: str,
    capability_version: str,
    requested_fields: tuple[str, ...],
    requested_purpose: AstraReadPurpose,
    requested_maximum_result_count: int,
    parameters: tuple[SubscriptionAstraParameter, ...],
    definition: SubscriptionAstraCapabilityDefinition,
    read_capability: AstraNamedReadCapability,
) -> None:
    if definition.status is not SubscriptionAstraCapabilityStatus.ENABLED:
        raise SubscriptionAstraCapabilityError("Subscription Manager capability is disabled.")
    if capability_id != definition.capability_id:
        raise SubscriptionAstraCapabilityError("Owner acceptance capability mismatch.")
    if capability_version != definition.capability_version:
        raise SubscriptionAstraCapabilityError("Unsupported Subscription Manager capability version.")
    if requested_maximum_result_count > definition.maximum_result_count:
        raise SubscriptionAstraCapabilityError("Requested result limit exceeds capability bound.")
    if not set(requested_fields).issubset(read_capability.allowed_field_references):
        raise SubscriptionAstraCapabilityError("Owner acceptance field scope exceeds app declaration.")
    if not set(read_capability.required_field_references).issubset(requested_fields):
        raise SubscriptionAstraCapabilityError("Owner acceptance omitted required fields.")
    if requested_purpose not in read_capability.allowed_purposes:
        raise SubscriptionAstraCapabilityError("Owner acceptance purpose is not permitted.")
    requested_parameters = {parameter.name for parameter in parameters}
    if not requested_parameters.issubset(definition.allowed_parameters):
        raise SubscriptionAstraCapabilityError("Unsupported capability parameter.")


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
    grouped: dict[str, list[SubscriptionRecord]] = defaultdict(list)
    for item in subscriptions:
        grouped[_currency(item.currency_code)].append(item)
    records = []
    for currency, items in sorted(grouped.items()):
        ordered = sorted(items, key=lambda item: (-_monthly_decimal(item), item.name.lower(), item.provider.lower(), item.id))
        top = ordered[0]
        records.append(
            {
                "currency": currency,
                "subscription": _subscription_record(top) | {"monthly_estimate": _money(_monthly_decimal(top))},
            }
        )
    return _result(
        request,
        definition,
        summary={
            "answer_type": "highest_cost_by_currency",
            "items": records,
            "comparison_policy": "within_currency_only_no_fx",
        },
        record_count=len(records),
        records=tuple(records),
        reason_codes=[*reason_codes, "within_currency_only_no_fx"],
    )


def _recurring_totals_by_currency_and_frequency(
    request: SubscriptionAstraReadRequest,
    definition: SubscriptionAstraCapabilityDefinition,
    subscriptions: list[SubscriptionRecord],
    reason_codes: list[str],
) -> SubscriptionAstraReadResult:
    totals: dict[tuple[str, str], dict[str, Decimal | int]] = defaultdict(lambda: {"recurring_amount": Decimal("0.00"), "subscription_count": 0})
    for item in subscriptions:
        key = (_currency(item.currency_code), item.billing_frequency)
        totals[key]["recurring_amount"] = totals[key]["recurring_amount"] + Decimal(str(item.billing_amount))
        totals[key]["subscription_count"] = int(totals[key]["subscription_count"]) + 1
    records = tuple(
        {
            "currency": currency,
            "billing_frequency": billing_frequency,
            "recurring_amount": _money(values["recurring_amount"]),
            "subscription_count": values["subscription_count"],
        }
        for (currency, billing_frequency), values in sorted(totals.items())
    )
    return _result(
        request,
        definition,
        summary={
            "answer_type": "recurring_totals_by_currency_and_frequency",
            "totals": list(records),
            "aggregation_policy": "raw_frequency_buckets_no_fx_no_frequency_merge",
        },
        record_count=len(records),
        records=records,
        reason_codes=[*reason_codes, "raw_frequency_buckets", "currency_grouped_no_fx"],
    )


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


def _request_from_grant(grant: SubscriptionAstraReadGrant) -> SubscriptionAstraReadRequest:
    return SubscriptionAstraReadRequest(
        capability_id=grant.capability_id,
        capability_version=grant.capability_version,
        app_identity=APP_ID,
        request_reference=grant.request_reference,
        requested_maximum_result_count=grant.maximum_result_count,
        authorization_reference=grant.astra_authorization_reference,
        purpose=grant.purpose,
        observed_at=grant.observed_at,
        parameters=grant.permitted_parameters,
    )


def _parameter_digest(parameters: tuple[SubscriptionAstraParameter, ...]) -> str:
    payload = [
        parameter.model_dump(mode="json")
        for parameter in sorted(parameters, key=lambda item: (item.name, str(item.value)))
    ]
    return f"sha256:{sha256(str(payload).encode()).hexdigest()}"


def _validate_principal_matches_user(principal_reference: str, user_id: str) -> None:
    allowed = {user_id, f"user:{user_id}", f"principal:{user_id}"}
    if principal_reference not in allowed:
        raise SubscriptionAstraCapabilityError("Astra authorization principal does not match authenticated subscription owner.")


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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
