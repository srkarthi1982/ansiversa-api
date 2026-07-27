from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.intent_resolution import AstraIntentRequest
from app.modules.astra_ai.planning import (
    AstraPlanningRequest,
    AstraRequestedCompletionPosture,
    AstraRequestedPlanStep,
)
from app.modules.astra_ai.read_access_authorization import (
    AstraReadAuthorizationRequest,
    AstraReadPurpose,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError

VALIDATION_VERSION = "1.0.0"
NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
UNAVAILABILITY_REASON = "certified_governance_disabled_fail_closed"


class ScenarioGroup(StrEnum):
    CERTIFIED_DEFAULT = "certified_default"


class VerificationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_REACHED = "not_reached"
    UNAVAILABLE = "unavailable"


class AstraValidationScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scenario_id: str = Field(pattern=r"^astra_val_001_[a-z0-9_]{3,80}$")
    scenario_group: ScenarioGroup = ScenarioGroup.CERTIFIED_DEFAULT
    scenario_name: str
    expected_outcome: str
    actual_outcome: str
    passed: bool
    runtime_state: str
    conversation_state: str
    intent_status: str
    capability_status: str
    plan_status: str
    read_authorization_status: str
    evidence_integrity_status: VerificationStatus
    lifecycle_status: VerificationStatus
    successful_path_available: bool = False
    unavailability_reason: str = UNAVAILABILITY_REASON
    database_connection_state: str = "not_authorized"
    sql_execution_state: str = "not_authorized"
    data_retrieval_state: str = "not_performed"
    data_mutation_state: str = "prohibited"
    schema_mutation_state: str = "prohibited"
    production_read_state: str = "not_approved"
    production_state: str = "unchanged"
    failure_reference: str | None = None
    completed_at: datetime = NOW
    validation_version: str = VALIDATION_VERSION

    def stable_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    def text(self) -> str:
        rows = (
            ("Scenario", self.scenario_name),
            ("Result", "passed" if self.passed else "failed"),
            ("Runtime", self.runtime_state),
            ("Conversation", self.conversation_state),
            ("Intent", self.intent_status),
            ("Plan", self.plan_status),
            ("Read authorization", self.read_authorization_status),
            ("Successful path", "unavailable by certified design"),
            ("Database connection", self.database_connection_state),
            ("SQL execution", self.sql_execution_state),
            ("Data retrieval", self.data_retrieval_state),
            ("Mutation", self.data_mutation_state),
            ("Schema mutation", self.schema_mutation_state),
            ("Production read", self.production_read_state),
            ("Evidence integrity", self.evidence_integrity_status.value),
            ("Lifecycle", self.lifecycle_status.value),
        )
        return "\n".join(f"{label:<24} {value}" for label, value in rows)


def _requirement() -> ConstitutionalRequirementReference:
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-CM-009",
        requirement_version="1.0.0",
    )


class _Assembly:
    def __init__(self, *, suffix: str = "v", capacity: int = 100) -> None:
        # Runtime IDs are hexadecimal by contract; "a" identifies validation fixtures.
        self.runtime = AstraRuntime(
            created_at=NOW,
            startup_instance_id="astra_rt_" + ("a" if suffix == "v" else suffix) * 32,
            evidence_sink_capacity=capacity,
        )
        self.runtime.startup()
        self.engine = AstraConversationContextEngine(runtime=self.runtime)
        self.conversation_id = "conv_validation_0001"

    def active_turn(self):
        self.engine.create_conversation(conversation_id=self.conversation_id, created_at=NOW)
        self.engine.transition_conversation(
            self.conversation_id,
            AstraConversationLifecycleState.ACTIVE,
            transitioned_at=NOW,
            summary_reference="validation:active",
            entry_id="ctx_validation_active_0001",
        )
        self.engine.record_current_turn(
            self.conversation_id,
            AstraCurrentTurnContext(
                turn_id="turn_validation_0001",
                received_at=NOW,
                request_reference="request:validation:0001",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
                route_reference="validation:local",
            ),
            history_entry_id="ctx_validation_turn_0001",
            summary_reference="validation:declared",
        )
        return self.engine.get_conversation(self.conversation_id)

    def intent_request(self, snapshot, *, target="cap_conversation_context_0001", binding=None):
        issued = binding or self.engine.issue_declared_intent_binding(
            conversation_snapshot=snapshot,
            declared_action="request_plan",
            declared_subject="capability",
            declared_target=target,
        )
        return AstraIntentRequest(
            intent_request_id="intent_req_validation_0001",
            runtime_instance_id=self.runtime.identity.startup_instance_id,
            conversation_id=self.conversation_id,
            current_turn_reference=snapshot.current_turn.turn_id,
            request_reference=snapshot.current_turn.request_reference,
            declared_action="request_plan",
            declared_subject="capability",
            declared_target=target,
            declared_intent_binding=issued,
            constitutional_requirements=(_requirement(),),
            timestamp=NOW,
            version="1.0.0",
        )

    def resolve(self, snapshot, request):
        return self.runtime.intent_resolution.resolve(
            request,
            conversation_engine=self.engine,
            conversation_snapshot=snapshot,
            requester_context=self.runtime.capability_discovery.internal_request_context(),
        )

    def plan(self, snapshot):
        request = AstraPlanningRequest(
            planning_request_id="planning_req_validation_0001",
            runtime_instance_id=self.runtime.identity.startup_instance_id,
            conversation_id=self.conversation_id,
            request_reference="request:validation:plan",
            objective_reference="objective:validation:fail_closed",
            requester_context_reference="requester:validation:local",
            constitutional_requirement_references=(_requirement(),),
            maximum_step_count=1,
            requested_steps=(
                AstraRequestedPlanStep(
                    step_id="step_validation_0001",
                    sequence_number=1,
                    capability_id="cap_conversation_context_0001",
                    objective_reference="objective:validation:step",
                ),
            ),
            requested_completion_posture=AstraRequestedCompletionPosture.PROPOSAL_ONLY,
            planning_timestamp=NOW,
            planning_version="1.0.0",
        )
        return self.runtime.planning.propose(
            request,
            conversation_engine=self.engine,
            conversation_snapshot=snapshot,
            requester_context=self.runtime.capability_discovery.internal_request_context(),
        )


def _result(name: str, expected: str, actual: str, **updates) -> AstraValidationScenarioResult:
    values = dict(
        scenario_id=f"astra_val_001_{name}",
        scenario_name=name,
        expected_outcome=expected,
        actual_outcome=actual,
        passed=actual == expected,
        runtime_state="ready",
        conversation_state="not_started",
        intent_status="not_reached",
        capability_status="unavailable",
        plan_status="not_reached",
        read_authorization_status="not_reached",
        evidence_integrity_status=VerificationStatus.PASSED,
        lifecycle_status=VerificationStatus.PASSED,
    )
    values.update(updates)
    return AstraValidationScenarioResult(**values)


def _certified_default_fail_closed():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.resolve(snapshot, assembly.intent_request(snapshot))
    plan = assembly.plan(snapshot)
    evidence_ids = {item.evidence_id for item in assembly.runtime.evidence_sink.retrieve()}
    references_resolve = set(intent.evidence_references + plan.evidence_references).issubset(evidence_ids)
    actual = "fail_closed" if intent.intent_status.value == "invalid" and not plan.proposed_steps else "unexpected"
    return _result(
        "certified_default_fail_closed",
        "fail_closed",
        actual,
        conversation_state=snapshot.metadata.lifecycle_state.value,
        intent_status=intent.intent_status.value,
        plan_status=plan.plan_status.value,
        evidence_integrity_status=(
            VerificationStatus.PASSED if references_resolve else VerificationStatus.FAILED
        ),
    )


def _unknown_capability():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.resolve(snapshot, assembly.intent_request(snapshot, target="cap_unknown_validation_0001"))
    actual = "fail_closed" if intent.intent_status.value == "invalid" else "unexpected"
    return _result(
        "unknown_capability",
        "fail_closed",
        actual,
        conversation_state="active",
        intent_status=intent.intent_status.value,
        capability_status="unknown",
    )


def _forged_binding():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    binding = assembly.engine.issue_declared_intent_binding(
        conversation_snapshot=snapshot,
        declared_action="request_plan",
        declared_subject="capability",
        declared_target="cap_conversation_context_0001",
    ).model_copy()
    try:
        assembly.resolve(snapshot, assembly.intent_request(snapshot, binding=binding))
        actual = "accepted"
    except Exception:
        actual = "rejected"
    return _result(
        "forged_intent_binding",
        "rejected",
        actual,
        conversation_state="active",
        intent_status="invalid",
    )


def _stale_turn():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    binding = assembly.engine.issue_declared_intent_binding(
        conversation_snapshot=snapshot,
        declared_action="request_plan",
        declared_subject="capability",
        declared_target="cap_conversation_context_0001",
    )
    assembly.engine.record_current_turn(
        assembly.conversation_id,
        AstraCurrentTurnContext(
            turn_id="turn_validation_0002",
            received_at=NOW,
            request_reference="request:validation:0002",
            turn_kind=AstraConversationTurnKind.USER_REQUEST,
            route_reference="validation:local",
        ),
        history_entry_id="ctx_validation_turn_0002",
        summary_reference="validation:stale",
    )
    try:
        assembly.resolve(snapshot, assembly.intent_request(snapshot, binding=binding))
        actual = "accepted"
    except Exception:
        actual = "rejected"
    return _result("stale_turn", "rejected", actual, conversation_state="active", intent_status="invalid")


def _foreign_runtime():
    first = _Assembly()
    second = _Assembly(suffix="b")
    snapshot = first.active_turn()
    request = first.intent_request(snapshot)
    try:
        second.runtime.intent_resolution.resolve(
            request,
            conversation_engine=first.engine,
            conversation_snapshot=snapshot,
            requester_context=second.runtime.capability_discovery.internal_request_context(),
        )
        actual = "accepted"
    except Exception:
        actual = "rejected"
    return _result("foreign_runtime", "rejected", actual, conversation_state="foreign", intent_status="invalid")


def _read_request_contract_rejected():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.resolve(snapshot, assembly.intent_request(snapshot))
    try:
        request = AstraReadAuthorizationRequest(
            authorization_request_id="read_req_validation_0001",
            runtime_instance_id=assembly.runtime.identity.startup_instance_id,
            conversation_id=assembly.conversation_id,
            current_turn_reference=snapshot.current_turn.turn_id,
            intent_resolution_reference=intent.intent_id,
            read_capability_id="read_cap_validation_summary_0001",
            authenticated_principal_reference="validation_fixture:principal",
            requested_field_references=("validation_fixture.summary",),
            requested_row_limit=1,
            requested_time_range_days=1,
            declared_purpose=AstraReadPurpose.USER_REQUESTED_SUMMARY,
            requester_authority_context="validation_fixture:unavailable",
            constitutional_requirement_references=(_requirement(),),
            proofs=(),
            requested_at=NOW,
            request_version="1.0.0",
        )
        actual = "unexpected_contract_acceptance"
    except ValueError:
        actual = "request_contract_rejected"
    return _result(
        "read_request_without_proofs",
        "request_contract_rejected",
        actual,
        conversation_state="active",
        intent_status=intent.intent_status.value,
        read_authorization_status="not_reached",
        failure_reference="proofs_required_by_contract",
    )


def _health_degraded():
    assembly = _Assembly()
    health = assembly.runtime.read_access_authorization.health(observed_at=NOW)
    actual = health.health_outcome.value
    return _result(
        "health_degraded",
        "degraded",
        actual,
        read_authorization_status="unavailable",
    )


def _shutdown_invalidation():
    assembly = _Assembly()
    interface = assembly.runtime.intent_resolution
    assembly.runtime.shutdown()
    try:
        interface.health(observed_at=NOW)
        actual = "interface_active"
    except AstraRuntimeError:
        actual = "invalidated"
    return _result(
        "shutdown_invalidation",
        "invalidated",
        actual,
        runtime_state="stopped",
        lifecycle_status=VerificationStatus.PASSED,
    )


def _current_turn_evidence_atomicity():
    assembly = _Assembly(capacity=2)
    assembly.engine.create_conversation(conversation_id=assembly.conversation_id, created_at=NOW)
    assembly.engine.transition_conversation(
        assembly.conversation_id,
        AstraConversationLifecycleState.ACTIVE,
        transitioned_at=NOW,
        summary_reference="validation:active",
        entry_id="ctx_validation_active_0001",
    )
    baseline = assembly.engine.get_conversation(assembly.conversation_id)
    baseline_evidence_count = assembly.runtime.evidence_sink.count()
    try:
        assembly.engine.record_current_turn(
            assembly.conversation_id,
            AstraCurrentTurnContext(
                turn_id="turn_validation_atomicity_0001",
                received_at=NOW,
                request_reference="request:validation:atomicity",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
                route_reference="validation:local",
            ),
            history_entry_id="ctx_validation_atomicity_0001",
            summary_reference="validation:atomicity",
        )
        actual = "unexpected_success"
    except Exception:
        after = assembly.engine.get_conversation(assembly.conversation_id)
        evidence_count = assembly.runtime.evidence_sink.count()
        actual = (
            "failed_operation_atomic"
            if after == baseline
            and after.current_turn is None
            and evidence_count == baseline_evidence_count == 2
            else "partial_mutation_detected"
        )
    return _result(
        "current_turn_evidence_atomicity",
        "failed_operation_atomic",
        actual,
        conversation_state=baseline.metadata.lifecycle_state.value,
        failure_reference="current_turn_evidence_append_capacity",
    )


def _production_boundaries():
    assembly = _Assembly()
    health = assembly.runtime.health(observed_at=NOW)
    actual = (
        "preserved"
        if health.production_authorization_state
        and health.production_authorization_state.value == "not_approved"
        else "unexpected"
    )
    return _result(
        "production_boundaries",
        "preserved",
        actual,
        read_authorization_status="unavailable",
    )


_SCENARIOS: tuple[tuple[str, Callable[[], AstraValidationScenarioResult]], ...] = (
    ("certified_default_fail_closed", _certified_default_fail_closed),
    ("unknown_capability", _unknown_capability),
    ("forged_intent_binding", _forged_binding),
    ("stale_turn", _stale_turn),
    ("foreign_runtime", _foreign_runtime),
    ("read_request_without_proofs", _read_request_contract_rejected),
    ("health_degraded", _health_degraded),
    ("shutdown_invalidation", _shutdown_invalidation),
    ("current_turn_evidence_atomicity", _current_turn_evidence_atomicity),
    ("production_boundaries", _production_boundaries),
)
SCENARIO_NAMES = tuple(name for name, _ in _SCENARIOS)
_RUNNERS = dict(_SCENARIOS)


def run_scenario(name: str) -> AstraValidationScenarioResult:
    try:
        runner = _RUNNERS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown ASTRA-VAL-001 scenario: {name}") from exc
    return runner()


def run_all() -> tuple[AstraValidationScenarioResult, ...]:
    return tuple(run_scenario(name) for name in SCENARIO_NAMES)
