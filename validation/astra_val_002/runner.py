from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    BoundedEvidence,
    ConstitutionalRequirementReference,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    MinimizationClass,
    RedactionStatus,
    RetentionClass,
    SensitivityClass,
)
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.diagnostic_projection import (
    AstraDiagnosticCompleteness,
    AstraDiagnosticDigestStatus,
    AstraDiagnosticOverallIntegrity,
    AstraDiagnosticProjectionError,
    AstraDiagnosticProjectionKind,
    AstraDiagnosticProjectionRequest,
    AstraDiagnosticProofState,
    AstraDiagnosticRedactionPosture,
    AstraDiagnosticSection,
)
from app.modules.astra_ai.intent_resolution import AstraIntentRequest
from app.modules.astra_ai.planning import (
    AstraPlanningRequest,
    AstraRequestedCompletionPosture,
    AstraRequestedPlanStep,
)
from app.modules.astra_ai.read_access_authorization import AstraReadAuthorizationDecision
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError

VALIDATION_VERSION = "1.0.0"
NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
PROTECTED_VALUES = (
    "conv_val002_protected_0001",
    "turn_val002_protected_0001",
    "request:val002:protected",
    "raw-user-message-val002",
    "secret-val002",
)
FORBIDDEN_LEAK_TERMS = (
    "authority_token",
    "issuer_authority",
    "proof_object",
    "password",
    "credential",
    "secret-val002",
    "raw-user-message-val002",
    "conversation_content",
    "hidden_reasoning",
    "provider_payload",
    "database_record",
    "runtime_handle",
)


class ScenarioGroup(StrEnum):
    DETERMINISM = "determinism"
    AUTHORITY = "authority"
    CORRELATION = "correlation"
    EVIDENCE = "evidence"
    PRIVACY = "privacy"
    COMPLETENESS = "completeness"
    TIMELINE = "timeline"
    ATOMICITY = "atomicity"
    LIFECYCLE = "lifecycle"
    EXPOSURE = "exposure"


class AstraVal002ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scenario_id: str = Field(pattern=r"^astra_val_002_[a-z0-9_]{3,80}$")
    scenario_group: ScenarioGroup
    scenario_name: str
    expected_outcome: str
    actual_outcome: str
    passed: bool
    projection_kind: str
    completeness: str
    redaction_state: str
    correlation_status: str
    evidence_integrity_status: str
    digest_status: str
    timeline_status: str
    lifecycle_status: str
    exposure_boundary_status: str
    deterministic_comparison_status: str
    failure_reference: str | None = None
    completed_at: datetime = NOW
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
            ("Projection", self.projection_kind),
            ("Completeness", self.completeness),
            ("Redaction", self.redaction_state),
            ("Correlation", self.correlation_status),
            ("Evidence integrity", self.evidence_integrity_status),
            ("Digest", self.digest_status),
            ("Timeline", self.timeline_status),
            ("Lifecycle", self.lifecycle_status),
            ("Exposure", self.exposure_boundary_status),
            ("Determinism", self.deterministic_comparison_status),
        )
        return "\n".join(f"{label:<24} {value}" for label, value in rows)


def _requirement() -> ConstitutionalRequirementReference:
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-CM-009",
        requirement_version="1.0.0",
    )


class _Assembly:
    def __init__(self, *, suffix: str = "b", capacity: int = 200) -> None:
        self.runtime = AstraRuntime(
            created_at=NOW,
            startup_instance_id="astra_rt_" + suffix * 32,
            evidence_sink_capacity=capacity,
        )
        self.runtime.startup()
        self.conversation = AstraConversationContextEngine(runtime=self.runtime)

    def active_turn(self, *, suffix: str = "0001"):
        conversation_id = f"conv_val002_protected_{suffix}"
        self.conversation.create_conversation(conversation_id=conversation_id, created_at=NOW)
        self.conversation.transition_conversation(
            conversation_id,
            AstraConversationLifecycleState.ACTIVE,
            transitioned_at=NOW,
            summary_reference=f"val002:active:{suffix}",
            entry_id=f"ctx_val002_active_{suffix}",
        )
        self.conversation.record_current_turn(
            conversation_id,
            AstraCurrentTurnContext(
                turn_id=f"turn_val002_protected_{suffix}",
                received_at=NOW,
                request_reference=f"request:val002:{suffix}",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
                route_reference="validation:local",
            ),
            history_entry_id=f"ctx_val002_turn_{suffix}",
            summary_reference=f"val002:turn:{suffix}",
        )
        return self.conversation.get_conversation(conversation_id)

    def intent(self, snapshot, *, suffix: str = "0001"):
        binding = self.conversation.issue_declared_intent_binding(
            conversation_snapshot=snapshot,
            declared_action="request_plan",
            declared_subject="capability",
            declared_target="cap_conversation_context_0001",
        )
        request = AstraIntentRequest(
            intent_request_id=f"intent_req_val002_{suffix}",
            runtime_instance_id=self.runtime.identity.startup_instance_id,
            conversation_id=snapshot.metadata.conversation_id,
            current_turn_reference=snapshot.current_turn.turn_id,
            request_reference=snapshot.current_turn.request_reference,
            declared_action="request_plan",
            declared_subject="capability",
            declared_target="cap_conversation_context_0001",
            declared_intent_binding=binding,
            constitutional_requirements=(_requirement(),),
            timestamp=NOW,
            version="1.0.0",
        )
        return self.runtime.intent_resolution.resolve(
            request,
            conversation_engine=self.conversation,
            conversation_snapshot=snapshot,
            requester_context=self.runtime.capability_discovery.internal_request_context(),
        )

    def plan(self, snapshot, *, suffix: str = "0001"):
        request = AstraPlanningRequest(
            planning_request_id=f"planning_req_val002_{suffix}",
            runtime_instance_id=self.runtime.identity.startup_instance_id,
            conversation_id=snapshot.metadata.conversation_id,
            request_reference=f"request:val002:plan:{suffix}",
            objective_reference=f"objective:val002:{suffix}",
            requester_context_reference="requester:val002:local",
            constitutional_requirement_references=(_requirement(),),
            maximum_step_count=1,
            requested_steps=(
                AstraRequestedPlanStep(
                    step_id=f"step_val002_{suffix}",
                    sequence_number=1,
                    capability_id="cap_conversation_context_0001",
                    objective_reference=f"objective:val002:step:{suffix}",
                ),
            ),
            requested_completion_posture=AstraRequestedCompletionPosture.PROPOSAL_ONLY,
            planning_timestamp=NOW,
            planning_version="1.0.0",
        )
        return self.runtime.planning.propose(
            request,
            conversation_engine=self.conversation,
            conversation_snapshot=snapshot,
            requester_context=self.runtime.capability_discovery.internal_request_context(),
        )

    def projection_request(
        self,
        *,
        request_id: str,
        kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
        sections=(AstraDiagnosticSection.RUNTIME,),
        posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        maximum=50,
        requested_at=NOW,
        **inputs,
    ):
        return self.runtime.diagnostic_projection.issue_request(
            projection_request_id=request_id,
            projection_kind=kind,
            requested_sections=sections,
            maximum_timeline_entries=maximum,
            requested_redaction_posture=posture,
            requested_at=requested_at,
            **inputs,
        )


def _evidence(index: int, *, timestamp=NOW) -> BoundedEvidence:
    digest = hashlib.sha256(f"astra-val-002:{index}".encode()).hexdigest()
    return BoundedEvidence(
        evidence_id=f"evd_val002_{index:04d}",
        evidence_type=EvidenceType.AUDIT_INTEGRITY,
        requirement_references=(_requirement(),),
        actor_or_service_class=ActorOrServiceClass.COMPONENT,
        decision_or_operation_reference=f"val002:evidence:{index}",
        timestamp=timestamp,
        sensitivity_class=SensitivityClass.INTERNAL,
        minimization_class=MinimizationClass.METADATA_ONLY,
        retention_class=RetentionClass.GOVERNANCE_RECORD,
        integrity=EvidenceIntegrityMetadata(
            source_system="astra_val_002:fixture",
            provenance_reference="ASTRA-VAL-002:1.0.0",
            content_digest=f"sha256:{digest}",
        ),
        correction=EvidenceCorrectionMetadata(evidence_version="1.0.0"),
        redaction_status=RedactionStatus.NOT_REQUIRED,
    )


def semantic_projection(projection) -> dict:
    """Exclude only independently issued request/evidence identity and issuance time."""
    return {
        "projection_kind": projection.projection_kind.value,
        "completeness": projection.completeness.value,
        "redaction_state": projection.redaction_state,
        "runtime_state": projection.runtime_state,
        "authoritative_configuration_state": projection.authoritative_configuration_state,
        "component_states": tuple(item.model_dump(mode="json") for item in projection.component_states),
        "correlation": {
            "completeness": projection.correlation_manifest.completeness.value,
            "links": tuple(
                {
                    "relationship": item.relationship,
                    "proof_state": item.proof_state.value,
                    "reason_code": item.reason_code.value if item.reason_code else None,
                }
                for item in projection.correlation_manifest.link_results
            ),
        },
        "evidence": tuple(
            {
                "reference_status": item.reference_status.value,
                "contract_status": item.contract_status.value,
                "provenance_status": item.provenance_status.value,
                "digest_status": item.digest_status.value,
                "overall_integrity": item.overall_integrity.value,
                "sensitivity_class": item.sensitivity_class,
                "redaction_status": item.redaction_status,
            }
            for item in projection.evidence_summaries
        ),
        "timeline": tuple(
            {
                "sequence": item.sequence,
                "stage": item.stage,
                "state": item.state.value,
                "reference": item.reference,
                "evidence_reference": item.evidence_reference,
                "timestamp": item.timestamp.isoformat(),
                "reason_code": item.reason_code.value if item.reason_code else None,
                "redaction_state": item.redaction_state,
            }
            for item in projection.timeline_entries
        ),
        "truncated": projection.truncated,
        "remaining_entries_unavailable": projection.remaining_entries_unavailable,
        "reason_codes": tuple(item.value for item in projection.reason_codes),
        "exposure": (
            projection.internal_only,
            projection.api_exposure_authorized,
            projection.ui_exposure_authorized,
            projection.public_access_authorized,
            projection.production_exposure_approved,
        ),
    }


def _result(name, group, expected, actual, **updates):
    values = dict(
        scenario_id=f"astra_val_002_{name}",
        scenario_group=group,
        scenario_name=name,
        expected_outcome=expected,
        actual_outcome=actual,
        passed=actual == expected,
        projection_kind="not_reached",
        completeness="not_reached",
        redaction_state="not_reached",
        correlation_status="not_reached",
        evidence_integrity_status="not_reached",
        digest_status="not_reached",
        timeline_status="not_reached",
        lifecycle_status="ready",
        exposure_boundary_status="internal_only",
        deterministic_comparison_status="not_applicable",
    )
    values.update(updates)
    return AstraVal002ScenarioResult(**values)


def _deterministic_projection():
    assembly = _Assembly()
    health = assembly.runtime.health(observed_at=NOW)
    first = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(request_id="diag_req_val002_determinism_0001", runtime_health=health),
        created_at=NOW,
    )
    second = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(request_id="diag_req_val002_determinism_0002", runtime_health=health),
        created_at=NOW,
    )
    strict = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_determinism_0003",
            posture=AstraDiagnosticRedactionPosture.STRICT,
            runtime_health=health,
        ),
        created_at=NOW,
    )
    exact = semantic_projection(first) == semantic_projection(second)
    distinct = semantic_projection(first) != semantic_projection(strict)
    actual = "deterministic_distinct_postures" if exact and distinct else "mismatch"
    return _result(
        "deterministic_projection",
        ScenarioGroup.DETERMINISM,
        "deterministic_distinct_postures",
        actual,
        projection_kind=first.projection_kind.value,
        completeness=first.completeness.value,
        redaction_state=first.redaction_state,
        deterministic_comparison_status="exact_semantic_match" if exact else "mismatch",
    )


def _authority_tamper_resistance():
    assembly = _Assembly()
    health = assembly.runtime.health(observed_at=NOW)
    request = assembly.projection_request(
        request_id="diag_req_val002_authority_0001", runtime_health=health
    )
    checks = []
    assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    for candidate, timestamp in (
        (request.model_copy(), NOW),
        (request.model_copy(update={"maximum_timeline_entries": 1}), NOW),
        (request, NOW + timedelta(minutes=16)),
    ):
        try:
            assembly.runtime.diagnostic_projection.project(candidate, created_at=timestamp)
            checks.append(False)
        except AstraDiagnosticProjectionError:
            checks.append(True)
    caller = AstraDiagnosticProjectionRequest(
        **request.model_dump(),
        runtime_health=health,
        authority_token=object(),
    )
    try:
        assembly.runtime.diagnostic_projection.project(caller, created_at=NOW)
        checks.append(False)
    except AstraDiagnosticProjectionError:
        checks.append(True)
    snapshot = assembly.active_turn()
    intent = assembly.intent(snapshot)
    plan = assembly.plan(snapshot)
    fabricated_read = AstraReadAuthorizationDecision.model_construct(
        runtime_instance_id=assembly.runtime.identity.startup_instance_id,
        authorization_decision_id="read_decision_val002_fabricated",
    )
    for index, (field, value, section) in enumerate(
        (
            ("intent_resolution", intent.model_copy(), AstraDiagnosticSection.INTENT),
            ("plan", plan.model_copy(), AstraDiagnosticSection.PLANNING),
            (
                "read_authorization_decision",
                fabricated_read,
                AstraDiagnosticSection.READ_AUTHORIZATION,
            ),
        ),
        start=2,
    ):
        candidate = assembly.projection_request(
            request_id=f"diag_req_val002_authority_000{index}",
            kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
            sections=(section,),
            **{field: value},
        )
        try:
            assembly.runtime.diagnostic_projection.project(candidate, created_at=NOW)
            checks.append(False)
        except AstraDiagnosticProjectionError:
            checks.append(True)
    foreign = _Assembly(suffix="c")
    foreign_health = foreign.runtime.health(observed_at=NOW)
    foreign_output_request = assembly.projection_request(
        request_id="diag_req_val002_authority_0005",
        runtime_health=foreign_health,
    )
    try:
        assembly.runtime.diagnostic_projection.project(foreign_output_request, created_at=NOW)
        checks.append(False)
    except AstraDiagnosticProjectionError:
        checks.append(True)
    foreign_request = foreign.projection_request(
        request_id="diag_req_val002_foreign_0001",
        runtime_health=foreign.runtime.health(observed_at=NOW),
    )
    try:
        assembly.runtime.diagnostic_projection.project(foreign_request, created_at=NOW)
        checks.append(False)
    except AstraDiagnosticProjectionError:
        checks.append(True)
    checks.append(not hasattr(assembly.runtime.diagnostic_projection, "register_certified_output"))
    checks.append(not hasattr(assembly.runtime.diagnostic_projection, "register_runtime_output"))
    actual = "all_rejected" if all(checks) else "authority_gap"
    return _result(
        "authority_tamper_resistance",
        ScenarioGroup.AUTHORITY,
        "all_rejected",
        actual,
        lifecycle_status="exact_runtime_authority",
    )


def _correlation_integrity():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.intent(snapshot)
    plan = assembly.plan(snapshot)
    request = assembly.projection_request(
        request_id="diag_req_val002_correlation_0001",
        kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
        sections=(
            AstraDiagnosticSection.CONVERSATION,
            AstraDiagnosticSection.INTENT,
            AstraDiagnosticSection.PLANNING,
        ),
        conversation_snapshot=snapshot,
        conversation_engine=assembly.conversation,
        intent_resolution=intent,
        plan=plan,
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    states = {item.relationship: item.proof_state for item in projection.correlation_manifest.link_results}
    no_gap = all(item.stage != "intent_plan" for item in projection.timeline_entries)
    expected = {
        "conversation_current_turn": AstraDiagnosticProofState.PROVEN,
        "intent_conversation": AstraDiagnosticProofState.PROVEN,
        "intent_current_turn": AstraDiagnosticProofState.PROVEN,
        "plan_conversation": AstraDiagnosticProofState.PROVEN,
        "intent_plan": AstraDiagnosticProofState.MISSING,
    }
    conflicting_snapshot = assembly.active_turn(suffix="0002")
    conflicting_plan = assembly.plan(conflicting_snapshot, suffix="0002")
    conflicting_request = assembly.projection_request(
        request_id="diag_req_val002_correlation_0002",
        kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
        sections=(AstraDiagnosticSection.INTENT, AstraDiagnosticSection.PLANNING),
        intent_resolution=intent,
        plan=conflicting_plan,
    )
    conflicting_projection = assembly.runtime.diagnostic_projection.project(
        conflicting_request, created_at=NOW
    )
    conflict_visible = any(
        item.relationship == "intent_plan"
        and item.proof_state is AstraDiagnosticProofState.CONFLICTING
        for item in conflicting_projection.correlation_manifest.link_results
    )
    actual = (
        "explicit_only"
        if all(states.get(k) is v for k, v in expected.items()) and no_gap and conflict_visible
        else "inferred"
    )
    return _result(
        "correlation_integrity",
        ScenarioGroup.CORRELATION,
        "explicit_only",
        actual,
        projection_kind=projection.projection_kind.value,
        completeness=projection.completeness.value,
        redaction_state=projection.redaction_state,
        correlation_status="intent_plan_missing",
        timeline_status="no_synthetic_gap",
    )


def _evidence_integrity():
    assembly = _Assembly()
    stored = assembly.runtime.evidence_sink.append(_evidence(1))
    request = assembly.projection_request(
        request_id="diag_req_val002_evidence_0001",
        kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        sections=(AstraDiagnosticSection.EVIDENCE,),
        evidence_references=(stored.evidence_id,),
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    summary = projection.evidence_summaries[0]
    sink_ids = {item.evidence_id for item in assembly.runtime.evidence_sink.retrieve()}
    exact = (
        summary.reference_status.value == "resolved"
        and summary.contract_status.value == "valid"
        and summary.provenance_status.value == "valid_structural"
        and summary.digest_status is AstraDiagnosticDigestStatus.NOT_REPRODUCIBLE
        and summary.overall_integrity is AstraDiagnosticOverallIntegrity.RESOLVED_STRUCTURAL
        and set(projection.evidence_references).issubset(sink_ids)
    )
    missing_request = assembly.projection_request(
        request_id="diag_req_val002_evidence_0002",
        kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        sections=(AstraDiagnosticSection.EVIDENCE,),
        evidence_references=("evd_val002_foreign_0001",),
    )
    missing = assembly.runtime.diagnostic_projection.project(missing_request, created_at=NOW)
    invalid_payload = _evidence(2).model_dump(mode="python")
    invalid_payload["integrity"]["content_digest"] = "format-only-is-not-verification"
    try:
        BoundedEvidence.model_validate(invalid_payload)
        invalid_rejected = False
    except Exception:
        invalid_rejected = True
    exact = (
        exact
        and missing.evidence_summaries[0].overall_integrity.value == "missing"
        and invalid_rejected
    )
    actual = "structural_not_reproducible" if exact else "overstated"
    return _result(
        "evidence_integrity",
        ScenarioGroup.EVIDENCE,
        "structural_not_reproducible",
        actual,
        projection_kind=projection.projection_kind.value,
        completeness=projection.completeness.value,
        redaction_state=projection.redaction_state,
        evidence_integrity_status=summary.overall_integrity.value,
        digest_status=summary.digest_status.value,
    )


def _strict_redaction_no_leak():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.intent(snapshot)
    plan = assembly.plan(snapshot)
    request = assembly.projection_request(
        request_id="diag_req_val002_privacy_0001",
        kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
        sections=(
            AstraDiagnosticSection.CONVERSATION,
            AstraDiagnosticSection.INTENT,
            AstraDiagnosticSection.PLANNING,
            AstraDiagnosticSection.EVIDENCE,
        ),
        posture=AstraDiagnosticRedactionPosture.STRICT,
        conversation_snapshot=snapshot,
        conversation_engine=assembly.conversation,
        intent_resolution=intent,
        plan=plan,
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    serialized = projection.model_dump_json().lower()
    protected = (
        snapshot.metadata.conversation_id,
        snapshot.current_turn.turn_id,
        intent.intent_id,
        plan.plan_id,
        *intent.evidence_references,
        *plan.evidence_references,
    )
    operation_evidence = assembly.runtime.evidence_sink.retrieve()[-1].model_dump_json().lower()
    absent = not any(
        value.lower() in serialized or value.lower() in operation_evidence
        for value in protected + FORBIDDEN_LEAK_TERMS
    )
    matrix = (
        projection.correlation_manifest.conversation_reference is None
        and projection.correlation_manifest.current_turn_reference is None
        and projection.correlation_manifest.intent_reference is None
        and projection.correlation_manifest.plan_reference is None
        and not projection.correlation_manifest.evidence_references
        and all(item.reference is None for item in projection.component_states)
        and all(item.source_system is None for item in projection.evidence_summaries)
        and all(item.provenance_reference is None for item in projection.evidence_summaries)
        and all(item.recorded_digest_reference is None for item in projection.evidence_summaries)
        and all(item.reference == "[redacted]" for item in projection.timeline_entries)
        and all(item.evidence_reference is None for item in projection.timeline_entries)
    )
    unknown = _evidence(99).model_dump(mode="python")
    unknown["sensitivity_class"] = "unknown_future_sensitivity"
    try:
        BoundedEvidence.model_validate(unknown)
        unknown_rejected = False
    except Exception:
        unknown_rejected = True
    actual = "strict_no_leak" if absent and matrix and unknown_rejected else "privacy_leak"
    return _result(
        "strict_redaction_no_leak",
        ScenarioGroup.PRIVACY,
        "strict_no_leak",
        actual,
        projection_kind=projection.projection_kind.value,
        completeness=projection.completeness.value,
        redaction_state=projection.redaction_state,
        correlation_status="references_redacted",
        evidence_integrity_status="structural_metadata_redacted",
        timeline_status="references_redacted",
    )


def _completeness_precedence():
    assembly = _Assembly()
    health = assembly.runtime.health(observed_at=NOW)
    complete = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_complete_0001", runtime_health=health
        ),
        created_at=NOW,
    )
    partial = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_partial_0001",
            sections=(AstraDiagnosticSection.RUNTIME, AstraDiagnosticSection.EVIDENCE),
            runtime_health=health,
            evidence_references=("evd_val002_optional_missing",),
        ),
        created_at=NOW,
    )
    unavailable = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_unavailable_0001",
            kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
            sections=(AstraDiagnosticSection.EVIDENCE,),
            evidence_references=("evd_val002_required_missing",),
        ),
        created_at=NOW,
    )
    redacted = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_redacted_0001",
            posture=AstraDiagnosticRedactionPosture.STRICT,
            runtime_health=health,
        ),
        created_at=NOW,
    )
    values = (complete.completeness, partial.completeness, unavailable.completeness, redacted.completeness)
    expected = (
        AstraDiagnosticCompleteness.COMPLETE,
        AstraDiagnosticCompleteness.PARTIAL,
        AstraDiagnosticCompleteness.UNAVAILABLE,
        AstraDiagnosticCompleteness.REDACTED,
    )
    stage_states = {item.component_name: item.state.value for item in complete.component_states}
    not_applicable_is_stage_only = (
        stage_states.get("conversation") == "not_applicable"
        and complete.completeness is AstraDiagnosticCompleteness.COMPLETE
    )
    missing_distinct = unavailable.evidence_summaries[0].reference_status.value == "missing"
    actual = (
        "precedence_preserved"
        if values == expected and not_applicable_is_stage_only and missing_distinct
        else "precedence_mismatch"
    )
    return _result(
        "completeness_precedence",
        ScenarioGroup.COMPLETENESS,
        "precedence_preserved",
        actual,
        completeness="complete_partial_unavailable_redacted",
        redaction_state=redacted.redaction_state,
    )


def _timeline_bounds():
    assembly = _Assembly(capacity=100)
    references = tuple(
        assembly.runtime.evidence_sink.append(_evidence(index)).evidence_id
        for index in range(1, 56)
    )
    exact_request = assembly.projection_request(
        request_id="diag_req_val002_timeline_0050",
        kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        sections=(AstraDiagnosticSection.EVIDENCE,),
        evidence_references=references[:50],
        maximum=50,
    )
    exact_projection = assembly.runtime.diagnostic_projection.project(
        exact_request, created_at=NOW
    )
    request = assembly.projection_request(
        request_id="diag_req_val002_timeline_0001",
        kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        sections=(AstraDiagnosticSection.EVIDENCE,),
        evidence_references=references,
        maximum=50,
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    ordered = tuple(item.reference for item in projection.timeline_entries) == tuple(sorted(references)[:50])
    bounded = (
        len(projection.timeline_entries) == 50
        and projection.truncated
        and projection.remaining_entries_unavailable
        and "timeline_truncated" in tuple(item.value for item in projection.reason_codes)
        and not hasattr(projection, "continuation_token")
        and len(exact_projection.timeline_entries) == 50
        and not exact_projection.truncated
        and not exact_projection.remaining_entries_unavailable
    )
    actual = "bounded_deterministic" if ordered and bounded else "timeline_mismatch"
    return _result(
        "timeline_bounds",
        ScenarioGroup.TIMELINE,
        "bounded_deterministic",
        actual,
        projection_kind=projection.projection_kind.value,
        completeness=projection.completeness.value,
        redaction_state=projection.redaction_state,
        timeline_status="truncated_at_50",
        deterministic_comparison_status="reference_secondary_order",
    )


def _evidence_atomicity():
    assembly = _Assembly(capacity=1)
    assembly.runtime.evidence_sink.append(_evidence(1))
    health = assembly.runtime.health(observed_at=NOW)
    request = assembly.projection_request(
        request_id="diag_req_val002_atomicity_0001", runtime_health=health
    )
    before_health = assembly.runtime.health(observed_at=NOW)
    before_projection_health = assembly.runtime.diagnostic_projection.health(observed_at=NOW)
    before_count = assembly.runtime.evidence_sink.count()
    released = False
    try:
        assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
        released = True
    except Exception:
        pass
    after_health = assembly.runtime.health(observed_at=NOW)
    after_projection_health = assembly.runtime.diagnostic_projection.health(observed_at=NOW)
    atomic = (
        not released
        and before_count == assembly.runtime.evidence_sink.count() == 1
        and before_health == after_health
        and before_projection_health.last_successful_projection_sequence
        == after_projection_health.last_successful_projection_sequence
        == None
    )
    actual = "append_failure_atomic" if atomic else "partial_release"
    return _result(
        "evidence_atomicity",
        ScenarioGroup.ATOMICITY,
        "append_failure_atomic",
        actual,
        failure_reference="projection_evidence_capacity",
        evidence_integrity_status="append_failed_no_release",
    )


def _lifecycle_health():
    assembly = _Assembly()
    interface = assembly.runtime.diagnostic_projection
    health = assembly.runtime.health(observed_at=NOW)
    request = assembly.projection_request(
        request_id="diag_req_val002_lifecycle_0001", runtime_health=health
    )
    engine = assembly.runtime._diagnostic_projection
    healthy_while_fail_closed = (
        interface.health(observed_at=NOW).projection_health_outcome.value == "healthy"
        and assembly.runtime.read_access_authorization.health(observed_at=NOW).health_outcome.value
        == "degraded"
    )
    assembly.runtime.shutdown()
    rejected = False
    try:
        interface.project(request, created_at=NOW)
    except AstraRuntimeError:
        rejected = True
    stopped = engine.health(observed_at=NOW).projection_health_outcome.value == "stopped"
    actual = "shutdown_invalidated" if rejected and stopped and healthy_while_fail_closed else "lifecycle_gap"
    return _result(
        "lifecycle_health",
        ScenarioGroup.LIFECYCLE,
        "shutdown_invalidated",
        actual,
        lifecycle_status="stopped",
    )


def _exposure_boundaries():
    assembly = _Assembly()
    projection = assembly.runtime.diagnostic_projection.project(
        assembly.projection_request(
            request_id="diag_req_val002_exposure_0001",
            runtime_health=assembly.runtime.health(observed_at=NOW),
        ),
        created_at=NOW,
    )
    flags = (
        projection.internal_only
        and not projection.api_exposure_authorized
        and not projection.ui_exposure_authorized
        and not projection.public_access_authorized
        and not projection.production_exposure_approved
    )
    interface = assembly.runtime.diagnostic_projection
    no_enumeration = not any(
        hasattr(interface, name)
        for name in ("list", "list_all", "enumerate", "paginate", "continuation_token")
    )
    actual = "internal_only" if flags and no_enumeration else "external_surface"
    return _result(
        "exposure_boundaries",
        ScenarioGroup.EXPOSURE,
        "internal_only",
        actual,
        projection_kind=projection.projection_kind.value,
        completeness=projection.completeness.value,
        redaction_state=projection.redaction_state,
        exposure_boundary_status="internal_only",
    )


_SCENARIOS: tuple[tuple[str, Callable[[], AstraVal002ScenarioResult]], ...] = (
    ("deterministic_projection", _deterministic_projection),
    ("authority_tamper_resistance", _authority_tamper_resistance),
    ("correlation_integrity", _correlation_integrity),
    ("evidence_integrity", _evidence_integrity),
    ("strict_redaction_no_leak", _strict_redaction_no_leak),
    ("completeness_precedence", _completeness_precedence),
    ("timeline_bounds", _timeline_bounds),
    ("evidence_atomicity", _evidence_atomicity),
    ("lifecycle_health", _lifecycle_health),
    ("exposure_boundaries", _exposure_boundaries),
)
SCENARIO_NAMES = tuple(name for name, _ in _SCENARIOS)
_RUNNERS = dict(_SCENARIOS)


def run_scenario(name: str) -> AstraVal002ScenarioResult:
    try:
        scenario = _RUNNERS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown ASTRA-VAL-002 scenario: {name}") from exc
    return scenario()


def run_all() -> tuple[AstraVal002ScenarioResult, ...]:
    return tuple(run_scenario(name) for name in SCENARIO_NAMES)
