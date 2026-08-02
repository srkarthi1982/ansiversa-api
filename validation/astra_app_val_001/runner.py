from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import patch

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.astra_ai import read_execution
from app.modules.astra_ai.constitutional_contracts import FailurePosture, GovernanceOutcome
from app.modules.astra_ai.read_access_authorization import (
    AstraOwnerAcceptanceState,
    AstraReadAuthorizationDecision,
    AstraReadCheckResult,
    AstraReadDecisionStatus,
)
from app.modules.astra_ai.read_execution import (
    AstraReadAdapterDefinition,
    AstraReadAdapterRegistry,
    AstraReadExecutionBridge,
    AstraReadExecutionError,
)
from app.modules.astra_ai.runtime import AstraRuntime
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import (
    CAPABILITY_VERSION,
    SubscriptionAstraAuthorizationReference,
    SubscriptionAstraReadRequest,
    SubscriptionAstraReadResult,
    issue_read_grant,
)
from app.modules.subscription_manager.db import SubscriptionManagerBase
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord


VALIDATION_VERSION = "1.0.0"
OBSERVED_AT = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "d" * 32

FORBIDDEN_RESULT_TERMS = (
    "authority_token",
    "app_read_grant",
    "sql",
    "authorization: bearer",
    "provider_payload",
    "raw_prompt",
    "hidden_reasoning",
    "app.modules.astra_ai",
    "/Users/",
)
FORBIDDEN_RESULT_KEYS = ("db", "session", "authority_token", "app_read_grant", "sql")


class ScenarioGroup(StrEnum):
    RUNTIME_REQUEST = "runtime_request"
    AUTHORIZATION = "authorization"
    ADAPTER_SELECTION = "adapter_selection"
    APP_READ = "app_read"
    RESPONSE_CONTRACT = "response_contract"
    FAIL_CLOSED = "fail_closed"
    SESSION_BOUNDARY = "session_boundary"
    PRODUCTION_BOUNDARY = "production_boundary"


class AstraAppVal001ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(pattern=r"^astra_app_val_001_[a-z0-9_]{3,100}$")
    scenario_group: ScenarioGroup
    scenario_name: str
    expected_outcome: str
    actual_outcome: str
    passed: bool
    runtime_request_status: str = "not_applicable"
    read_authorization_status: str = "not_applicable"
    adapter_selection_status: str = "not_applicable"
    app_read_status: str = "not_applicable"
    response_contract_status: str = "not_applicable"
    privacy_status: str = "not_applicable"
    session_boundary_status: str = "not_applicable"
    fail_closed_status: str = "not_applicable"
    production_boundary_status: str = "unchanged"
    failure_reference: str | None = None
    completed_at: datetime = OBSERVED_AT
    validation_version: str = VALIDATION_VERSION

    def stable_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    def text(self) -> str:
        rows = (
            ("Scenario", self.scenario_name),
            ("Group", self.scenario_group.value),
            ("Result", "passed" if self.passed else "failed"),
            ("Expected", self.expected_outcome),
            ("Actual", self.actual_outcome),
            ("Runtime request", self.runtime_request_status),
            ("Read authorization", self.read_authorization_status),
            ("Adapter selection", self.adapter_selection_status),
            ("App read", self.app_read_status),
            ("Response contract", self.response_contract_status),
            ("Privacy", self.privacy_status),
            ("Session boundary", self.session_boundary_status),
            ("Fail closed", self.fail_closed_status),
            ("Production", self.production_boundary_status),
        )
        return "\n".join(f"{label:<24} {value}" for label, value in rows)


class TrackingSession(Session):
    def execute(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self.info.setdefault("astra_app_val_001_session_calls", []).append("execute")
        return super().execute(*args, **kwargs)

    @property
    def astra_session_calls(self) -> tuple[str, ...]:
        return tuple(self.info.get("astra_app_val_001_session_calls", ()))

    def clear_astra_session_calls(self) -> None:
        self.info["astra_app_val_001_session_calls"] = []


class _Fixture:
    def __enter__(self) -> "_Fixture":
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SubscriptionManagerBase.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine, class_=TrackingSession)()
        self.user = SimpleNamespace(id="user-a")
        self.foreign_user = SimpleNamespace(id="user-b")
        category = SubscriptionCategory(id="cat-streaming", owner_id=self.user.id, name="Streaming")
        self.db.add_all(
            [
                category,
                SubscriptionRecord(
                    id="sub-video",
                    owner_id=self.user.id,
                    category_id=category.id,
                    name="Video",
                    provider="Video",
                    billing_amount=10,
                    currency_code="AED",
                    billing_frequency="monthly",
                    next_billing_date="2026-08-01",
                    status="active",
                ),
                SubscriptionRecord(
                    id="sub-paused",
                    owner_id=self.user.id,
                    category_id=category.id,
                    name="Paused",
                    provider="Paused",
                    billing_amount=20,
                    currency_code="AED",
                    billing_frequency="monthly",
                    next_billing_date="2026-08-02",
                    status="paused",
                ),
            ]
        )
        self.db.commit()
        self.db.clear_astra_session_calls()
        self.runtime = AstraRuntime(created_at=OBSERVED_AT, startup_instance_id=RUNTIME_ID)
        self.runtime.startup()
        self.decision = self.decision_fixture()
        self.register_decision(self.decision)
        self.sequence = 0
        return self

    def __exit__(self, *_):
        if self.runtime.state.value == "ready":
            self.runtime.shutdown()
        self.db.close()

    def register_decision(self, decision: AstraReadAuthorizationDecision) -> None:
        self.runtime._read_execution_bridge.register_read_authorization_decision(
            decision,
            registration_authority=self.runtime._read_execution_registration_authority,
        )

    def decision_fixture(
        self,
        *,
        authorization_id: str = "read_auth_subscription_app_val_0001",
        status: AstraReadDecisionStatus = AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY,
        owning_app_id: str = "subscription_manager",
    ) -> AstraReadAuthorizationDecision:
        return AstraReadAuthorizationDecision(
            authorization_decision_id=authorization_id,
            authorization_request_id="read_req_subscription_app_val_0001",
            governance_decision_reference="APP-VAL-GOV-001",
            read_capability_id="read_cap_subscription_count_active_0001",
            owning_app_id=owning_app_id,
            decision_status=status,
            governance_outcome=GovernanceOutcome.ALLOW,
            purpose_result=AstraReadCheckResult.SATISFIED,
            principal_scope_result=AstraReadCheckResult.SATISFIED,
            tenant_scope_result=AstraReadCheckResult.SATISFIED,
            app_scope_result=AstraReadCheckResult.SATISFIED,
            record_scope_result=AstraReadCheckResult.SATISFIED,
            field_scope_result=AstraReadCheckResult.SATISFIED,
            filter_scope_result=AstraReadCheckResult.SATISFIED,
            minimization_result=AstraReadCheckResult.SATISFIED,
            row_limit_result=AstraReadCheckResult.SATISFIED,
            time_range_result=AstraReadCheckResult.SATISFIED,
            aggregation_result=AstraReadCheckResult.SATISFIED,
            cross_app_result=AstraReadCheckResult.SATISFIED,
            owner_acceptance_requirement=AstraOwnerAcceptanceState.ACCEPTED,
            evidence_references=("evd_app_val_read_auth_0001",),
            failure_posture=FailurePosture.FAIL_CLOSED,
            authorized_scope_summary=("subscription.count",),
            issued_at=OBSERVED_AT,
            version="1.0.0",
        )

    def grant(self, capability_id: str = "subscription.count_active"):
        request = SubscriptionAstraReadRequest(
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_identity="subscription_manager",
            request_reference=f"subscription/app-val/{capability_id.replace('.', '-')}",
            requested_maximum_result_count=50,
            authorization_reference=SubscriptionAstraAuthorizationReference(
                authorization_id=self.decision.authorization_decision_id,
                governance_decision_reference=self.decision.governance_decision_reference,
                capability_id=capability_id,
                capability_version=CAPABILITY_VERSION,
                app_scope="app:subscription_manager",
                decision_status="authorized_metadata_only",
                authenticated_principal_reference="principal:user-a",
                issued_at=OBSERVED_AT,
                expires_at=OBSERVED_AT + timedelta(minutes=5),
            ),
            purpose="Summarize current user subscriptions.",
            observed_at=OBSERVED_AT,
        )
        return issue_read_grant(authenticated_user=self.user, request=request)

    def execution_request(self, grant=None, *, capability_id: str = "subscription.count_active"):
        self.sequence += 1
        grant = grant or self.grant(capability_id)
        return self.runtime.read_execution.issue_request(
            execution_request_id=f"read_exec_req_app_val_{self.sequence:04d}",
            read_authorization_decision=self.decision,
            app_read_grant=grant,
            authenticated_principal_reference="principal:user-a",
            request_reference=grant.request_reference,
            requested_maximum_result_count=grant.maximum_result_count,
            requested_at=OBSERVED_AT,
            adapter_capability_id=capability_id,
            adapter_capability_version=CAPABILITY_VERSION,
        )

    def execute(self, request=None):
        request = request or self.execution_request()
        with _clocks():
            return self.runtime.read_execution.execute(request, db=self.db, authenticated_user=self.user)

    def replace_bridge_with_tracking_adapter(self) -> list[tuple[str, tuple[str, ...]]]:
        observed: list[tuple[str, tuple[str, ...]]] = []
        definition = AstraReadAdapterDefinition(
            owning_app_id="subscription_manager",
            adapter_capability_id="subscription.count_active",
            adapter_capability_version=CAPABILITY_VERSION,
            operation="read",
            implementation_reference="ASTRA-READ-EXEC-001",
        )

        def adapter(context):
            observed.append((context.request.adapter_capability_id, context.db.astra_session_calls))
            return subscription_reads.execute_read_capability(
                context.db,
                context.authenticated_user,
                context.app_read_grant,
            )

        self.runtime._read_execution_bridge = AstraReadExecutionBridge(
            runtime=self.runtime,
            registration_authority=self.runtime._read_execution_registration_authority,
            request_authority=self.runtime._read_execution_request_authority,
            registry=AstraReadAdapterRegistry(((definition, adapter),)),
        )
        self.register_decision(self.decision)
        return observed


def scenario_names() -> tuple[str, ...]:
    return tuple(SCENARIOS)


def run_scenario(name: str) -> AstraAppVal001ScenarioResult:
    try:
        handler = SCENARIOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown ASTRA-APP-VAL-001 scenario: {name}") from exc
    with _Fixture() as fixture:
        return handler(fixture)


def run_all() -> tuple[AstraAppVal001ScenarioResult, ...]:
    return tuple(run_scenario(name) for name in scenario_names())


def runtime_produces_execution_request(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    request = fixture.execution_request()
    passed = (
        request.runtime_instance_id == fixture.runtime.identity.startup_instance_id
        and fixture.runtime._read_execution_bridge._requests.get(request.execution_request_id) is request
        and request.authority_token is fixture.runtime._read_execution_request_authority
    )
    return _result(
        "runtime_produces_execution_request",
        ScenarioGroup.RUNTIME_REQUEST,
        passed,
        runtime_request_status="exact_runtime_issued_request",
        read_authorization_status="registered_decision_required",
    )


def read_authorization_enforced(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    refused = fixture.decision_fixture(
        authorization_id="read_auth_subscription_app_val_refused",
        status=AstraReadDecisionStatus.REFUSED,
    )
    passed = _raises(AstraReadExecutionError, lambda: fixture.register_decision(refused))
    return _result(
        "read_authorization_enforced",
        ScenarioGroup.AUTHORIZATION,
        passed,
        read_authorization_status="authorized_metadata_only_required",
        fail_closed_status="passed",
    )


def adapter_selection_is_explicit(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    observed = fixture.replace_bridge_with_tracking_adapter()
    request = fixture.execution_request()
    result = fixture.execute(request)
    passed = (
        result.summary.get("count") == 1
        and observed == [("subscription.count_active", ())]
        and fixture.runtime._read_execution_bridge.registry.adapter_keys
        == (("subscription_manager", "subscription.count_active", CAPABILITY_VERSION, "read"),)
    )
    return _result(
        "adapter_selection_is_explicit",
        ScenarioGroup.ADAPTER_SELECTION,
        passed,
        adapter_selection_status="explicit_subscription_manager_registry",
        session_boundary_status="session_unused_before_adapter",
    )


def app_owned_read_executes(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    result = fixture.execute()
    passed = result.summary.get("count") == 1 and result.record_count == 1
    return _result(
        "app_owned_read_executes",
        ScenarioGroup.APP_READ,
        passed,
        app_read_status="subscription_manager_adapter_read",
        response_contract_status=result.status.value,
    )


def response_is_validated_and_redacted(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    result = fixture.execute()
    payload = result.model_dump(mode="json")
    findings = _privacy_findings(payload)
    passed = not findings and result.production_authorization_state == "not_approved"
    return _result(
        "response_is_validated_and_redacted",
        ScenarioGroup.RESPONSE_CONTRACT,
        passed,
        response_contract_status="bounded_structured_result",
        privacy_status="no_forbidden_material" if not findings else ",".join(findings),
    )


def unauthorized_and_malformed_fail_closed(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    request = fixture.execution_request()
    copied = request.model_copy()
    bad_context = fixture.execution_request()
    object.__setattr__(bad_context, "execution_context_reference", "read-exec/bad-context")
    write = fixture.execution_request()
    object.__setattr__(write, "operation", "write")

    with _clocks():
        first = fixture.runtime.read_execution.execute(request, db=fixture.db, authenticated_user=fixture.user)
    failures = (
        _raises(AstraReadExecutionError, lambda: fixture.runtime.read_execution.execute(copied, db=fixture.db, authenticated_user=fixture.user)),
        _raises(AstraReadExecutionError, lambda: fixture.runtime.read_execution.execute(request, db=fixture.db, authenticated_user=fixture.user)),
        _raises(AstraReadExecutionError, lambda: fixture.runtime.read_execution.execute(bad_context, db=fixture.db, authenticated_user=fixture.user)),
        _raises(AstraReadExecutionError, lambda: fixture.runtime.read_execution.execute(write, db=fixture.db, authenticated_user=fixture.user)),
        _raises(AstraReadExecutionError, lambda: fixture.runtime.read_execution.execute(fixture.execution_request(), db=fixture.db, authenticated_user=fixture.foreign_user)),
        first.summary.get("count") == 1,
    )
    return _result(
        "unauthorized_and_malformed_fail_closed",
        ScenarioGroup.FAIL_CLOSED,
        all(failures),
        fail_closed_status="copied_reused_context_write_subject_rejected",
    )


def database_session_boundary_proof(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    observed = fixture.replace_bridge_with_tracking_adapter()
    result = fixture.execute()
    payload = result.model_dump(mode="json")
    passed = (
        observed == [("subscription.count_active", ())]
        and fixture.db.astra_session_calls == ("execute",)
        and "db" not in payload
        and "session" not in json.dumps(payload, sort_keys=True).lower()
    )
    return _result(
        "database_session_boundary_proof",
        ScenarioGroup.SESSION_BOUNDARY,
        passed,
        session_boundary_status="opaque_until_registered_adapter",
        app_read_status="adapter_only_session_use",
    )


def production_boundaries_unchanged(fixture: _Fixture) -> AstraAppVal001ScenarioResult:
    result = fixture.execute()
    passed = (
        result.production_authorization_state == "not_approved"
        and result.data_mutation_state == "prohibited"
        and result.schema_mutation_state == "prohibited"
    )
    return _result(
        "production_boundaries_unchanged",
        ScenarioGroup.PRODUCTION_BOUNDARY,
        passed,
        production_boundary_status="not_approved_unchanged",
    )


SCENARIOS: dict[str, Callable[[_Fixture], AstraAppVal001ScenarioResult]] = {
    "runtime_produces_execution_request": runtime_produces_execution_request,
    "read_authorization_enforced": read_authorization_enforced,
    "adapter_selection_is_explicit": adapter_selection_is_explicit,
    "app_owned_read_executes": app_owned_read_executes,
    "response_is_validated_and_redacted": response_is_validated_and_redacted,
    "unauthorized_and_malformed_fail_closed": unauthorized_and_malformed_fail_closed,
    "database_session_boundary_proof": database_session_boundary_proof,
    "production_boundaries_unchanged": production_boundaries_unchanged,
}


def _result(
    name: str,
    group: ScenarioGroup,
    passed: bool,
    **updates: Any,
) -> AstraAppVal001ScenarioResult:
    values = dict(
        scenario_id=f"astra_app_val_001_{name}",
        scenario_group=group,
        scenario_name=name,
        expected_outcome="passed",
        actual_outcome="passed" if passed else "failed",
        passed=passed,
    )
    values.update(updates)
    return AstraAppVal001ScenarioResult(**values)


def _raises(expected: type[Exception], callback: Callable[[], Any]) -> bool:
    try:
        callback()
    except expected:
        return True
    return False


def _privacy_findings(value: Any) -> tuple[str, ...]:
    findings: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = str(key).lower()
                if lowered in FORBIDDEN_RESULT_KEYS:
                    findings.append(lowered)
                visit(child)
        elif isinstance(item, (list, tuple)):
            for child in item:
                visit(child)

    visit(value)
    text = json.dumps(value, default=str, sort_keys=True).lower()
    findings.extend(term for term in FORBIDDEN_RESULT_TERMS if term in text)
    return tuple(dict.fromkeys(findings))


@contextmanager
def _clocks():
    with (
        patch.object(read_execution, "_utc_now", return_value=OBSERVED_AT),
        patch.object(subscription_reads._SUBSCRIPTION_ASTRA_EXECUTION_CLOCK, "now", return_value=OBSERVED_AT),
    ):
        yield
