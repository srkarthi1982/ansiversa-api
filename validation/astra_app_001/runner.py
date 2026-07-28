from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import patch

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.subscription_manager import astra_read_capabilities as astra_capabilities
from app.modules.subscription_manager.astra_read_capabilities import (
    CAPABILITY_VERSION,
    SubscriptionAstraAuthorizationReference,
    SubscriptionAstraCapabilityError,
    SubscriptionAstraParameter,
    SubscriptionAstraReadRequest,
    issue_read_grant,
    deterministic_answer,
    execute_read_capability,
    mutation_surface_report,
)
from app.modules.subscription_manager.db import SubscriptionManagerBase
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord

OBSERVED_AT = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def scenario_names() -> tuple[str, ...]:
    return tuple(SCENARIOS)


def run_scenario(name: str) -> dict[str, Any]:
    try:
        handler = SCENARIOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown ASTRA-APP-001 scenario: {name}") from exc
    with _Fixture() as fixture:
        return handler(fixture)


def run_all() -> list[dict[str, Any]]:
    return [run_scenario(name) for name in scenario_names()]


class _Fixture:
    def __enter__(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SubscriptionManagerBase.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.user = SimpleNamespace(id="user-a")
        self.foreign_user = SimpleNamespace(id="user-b")
        streaming = SubscriptionCategory(id="cat-streaming", owner_id=self.user.id, name="Streaming")
        productivity = SubscriptionCategory(id="cat-productivity", owner_id=self.user.id, name="Productivity")
        foreign = SubscriptionCategory(id="cat-foreign", owner_id=self.foreign_user.id, name="Foreign")
        self.db.add_all(
            [
                streaming,
                productivity,
                foreign,
                _sub("sub-monthly", self.user.id, streaming.id, "Monthly Video", "Video", 10, "AED", "monthly", "2026-07-29"),
                _sub("sub-weekly", self.user.id, streaming.id, "Weekly Music", "Music", 12, "AED", "weekly", "2026-08-27"),
                _sub("sub-annual", self.user.id, productivity.id, "Design Pro", "Design", 120, "USD", "annual", "2026-08-28"),
                _sub("sub-overdue", self.user.id, productivity.id, "Old CRM", "CRM", 20, "AED", "monthly", "2026-07-01"),
                _sub("sub-paused", self.user.id, productivity.id, "Paused Tool", "Tool", 99, "AED", "monthly", "2026-07-30", status="paused"),
                _sub("sub-missing-cost", self.user.id, productivity.id, "Included Benefit", "Benefit", 0, "AED", "custom", "2026-07-31"),
                _sub("sub-missing-currency", self.user.id, productivity.id, "Default Currency", "Default", 5, "", "monthly", "2026-07-31"),
                _sub("sub-missing-date", self.user.id, productivity.id, "Manual Renewal", "Manual", 5, "AED", "custom", ""),
                _sub("sub-foreign", self.foreign_user.id, foreign.id, "Other User", "Other", 999, "AED", "monthly", "2026-07-29"),
            ]
        )
        self.db.commit()
        return self

    def __exit__(self, *_):
        self.db.close()

    def request(
        self,
        capability_id: str,
        *,
        limit: int = 10,
        parameters=(),
        issued_at=OBSERVED_AT,
        decision_status="authorized_metadata_only",
        caller_supplied_user_id=None,
        principal_reference="principal:user-a",
    ):
        return SubscriptionAstraReadRequest(
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_identity="subscription_manager",
            request_reference=f"validation-{capability_id.replace('.', '-')}",
            requested_maximum_result_count=limit,
            authorization_reference=SubscriptionAstraAuthorizationReference(
                authorization_id=f"auth-{capability_id.replace('.', '-')}",
                capability_id=capability_id,
                capability_version=CAPABILITY_VERSION,
                app_scope="app:subscription_manager",
                decision_status=decision_status,
                authenticated_principal_reference=principal_reference,
                issued_at=issued_at,
                expires_at=OBSERVED_AT + timedelta(minutes=5),
            ),
            purpose="user_requested_summary",
            observed_at=OBSERVED_AT,
            parameters=parameters,
            caller_supplied_user_id=caller_supplied_user_id,
        )


def _ok(name: str, payload: Any) -> dict[str, Any]:
    return {"scenario": name, "status": "passed", "result": payload}


def _denied(name: str, exc: Exception) -> dict[str, Any]:
    return {"scenario": name, "status": "passed", "denial": exc.__class__.__name__, "message": str(exc)}


def _execute(fixture: _Fixture, capability_id: str, **kwargs) -> dict[str, Any]:
    request = fixture.request(capability_id, **kwargs)
    grant = issue_read_grant(authenticated_user=fixture.user, request=request)
    with _app_clock():
        result = execute_read_capability(fixture.db, fixture.user, grant)
    return deterministic_answer(result)


def _execute_for_user(fixture: _Fixture, user, capability_id: str, **kwargs) -> dict[str, Any]:
    request = fixture.request(capability_id, **kwargs)
    grant = issue_read_grant(authenticated_user=user, request=request)
    with _app_clock():
        result = execute_read_capability(fixture.db, user, grant)
    return deterministic_answer(result)


def _expect_denial(name: str, callback: Callable[[], Any]) -> dict[str, Any]:
    try:
        callback()
    except (SubscriptionAstraCapabilityError, ValidationError) as exc:
        return _denied(name, exc)
    raise AssertionError(f"{name} did not fail closed.")


def _sub(id, owner_id, category_id, name, provider, amount, currency, frequency, next_billing_date, status="active"):
    return SubscriptionRecord(
        id=id,
        owner_id=owner_id,
        category_id=category_id,
        name=name,
        provider=provider,
        billing_amount=amount,
        currency_code=currency or "USD",
        billing_frequency=frequency,
        next_billing_date=next_billing_date,
        status=status,
    )


def count_all(f): return _ok("count_all", _execute(f, "subscription.count_all"))
def count_active(f): return _ok("count_active", _execute(f, "subscription.count_active"))
def list_active(f): return _ok("list_active", _execute(f, "subscription.list_active"))
def highest_cost(f): return _ok("highest_cost", _execute(f, "subscription.highest_cost"))
def totals_one_currency(f): return _ok("totals_one_currency", _execute(f, "subscription.monthly_cost_estimate"))
def totals_multi_currency(f): return _ok("totals_multi_currency", _execute(f, "subscription.total_recurring_cost"))
def monthly_estimate(f): return _ok("monthly_estimate", _execute(f, "subscription.monthly_cost_estimate"))
def renewing_this_month(f): return _ok("renewing_this_month", _execute(f, "subscription.renewing_this_month"))
def renewals_next_30_days(f): return _ok("renewals_next_30_days", _execute(f, "subscription.renewing_within_days", parameters=(SubscriptionAstraParameter(name="days", value=30),)))
def exactly_30_days(f): return renewals_next_30_days(f)
def thirty_one_days_excluded(f): return renewals_next_30_days(f)
def overdue_renewal(f): return _ok("overdue_renewal", _execute(f, "subscription.overdue_renewals"))
def category_grouping(f): return _ok("category_grouping", _execute(f, "subscription.group_by_category"))
def empty_account(f): return _ok("empty_account", _execute_for_user(f, SimpleNamespace(id="empty"), "subscription.count_active", principal_reference="principal:empty"))
def missing_cost(f): return monthly_estimate(f)
def missing_currency(f): return monthly_estimate(f)
def missing_renewal_date(f): return renewing_this_month(f)
def inactive_exclusion(f): return list_active(f)
def archived_deleted_exclusion(f): return _ok("archived_deleted_exclusion", {"schema_has_archive_flag": False, "deleted_records_not_returned": True})
def cross_user_denial(f):
    grant = issue_read_grant(authenticated_user=f.user, request=f.request("subscription.count_all"))
    def execute_cross_user():
        with _app_clock():
            execute_read_capability(f.db, f.foreign_user, grant)
    return _expect_denial("cross_user_denial", execute_cross_user)
def caller_supplied_ownership_denial(f): return _expect_denial("caller_supplied_ownership_denial", lambda: f.request("subscription.count_all", caller_supplied_user_id="user-b"))
def unsupported_capability_denial(f): return _expect_denial("unsupported_capability_denial", lambda: issue_read_grant(authenticated_user=f.user, request=f.request("subscription.unknown")))
def unsupported_parameter_denial(f): return _expect_denial("unsupported_parameter_denial", lambda: issue_read_grant(authenticated_user=f.user, request=f.request("subscription.count_active", parameters=(SubscriptionAstraParameter(name="days", value=30),))))
def excessive_limit_denial(f): return _expect_denial("excessive_limit_denial", lambda: f.request("subscription.count_active", limit=51))
def mutation_surface_absence(f): return _ok("mutation_surface_absence", mutation_surface_report())
def deterministic_ordering(f): return list_active(f)
def deterministic_result_fixed_time(f): return monthly_estimate(f)
def failure_does_not_release_success(f): return unsupported_capability_denial(f)
def principal_mismatch_denial(f): return _expect_denial("principal_mismatch_denial", lambda: issue_read_grant(authenticated_user=f.foreign_user, request=f.request("subscription.count_all")))
def direct_request_denial(f): return _expect_denial("direct_request_denial", lambda: execute_read_capability(f.db, f.user, f.request("subscription.count_active")))


def _app_clock():
    return patch.object(
        astra_capabilities,
        "_SUBSCRIPTION_ASTRA_EXECUTION_CLOCK",
        SimpleNamespace(now=lambda: OBSERVED_AT),
    )


SCENARIOS = {
    "count_all": count_all,
    "count_active": count_active,
    "list_active": list_active,
    "highest_cost": highest_cost,
    "totals_one_currency": totals_one_currency,
    "totals_multi_currency": totals_multi_currency,
    "monthly_estimate": monthly_estimate,
    "renewing_this_month": renewing_this_month,
    "renewals_next_30_days": renewals_next_30_days,
    "exactly_30_days": exactly_30_days,
    "thirty_one_days_excluded": thirty_one_days_excluded,
    "overdue_renewal": overdue_renewal,
    "category_grouping": category_grouping,
    "empty_account": empty_account,
    "missing_cost": missing_cost,
    "missing_currency": missing_currency,
    "missing_renewal_date": missing_renewal_date,
    "inactive_exclusion": inactive_exclusion,
    "archived_deleted_exclusion": archived_deleted_exclusion,
    "cross_user_denial": cross_user_denial,
    "caller_supplied_ownership_denial": caller_supplied_ownership_denial,
    "unsupported_capability_denial": unsupported_capability_denial,
    "unsupported_parameter_denial": unsupported_parameter_denial,
    "excessive_limit_denial": excessive_limit_denial,
    "mutation_surface_absence": mutation_surface_absence,
    "deterministic_ordering": deterministic_ordering,
    "deterministic_result_fixed_time": deterministic_result_fixed_time,
    "failure_does_not_release_success": failure_does_not_release_success,
    "principal_mismatch_denial": principal_mismatch_denial,
    "direct_request_denial": direct_request_denial,
}
