from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

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
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeComponentIdentifier, AstraRuntimeError
from validation.astra_val_001.runner import _Assembly

NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)


def runtime(*, suffix="d", capacity=200):
    value = AstraRuntime(
        created_at=NOW,
        startup_instance_id="astra_rt_" + suffix * 32,
        evidence_sink_capacity=capacity,
    )
    value.startup()
    return value


def runtime_request(value, *, request_id="diag_req_runtime_0001", maximum=10, health=None):
    return value.diagnostic_projection.issue_request(
        projection_request_id=request_id,
        projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
        requested_sections=(AstraDiagnosticSection.RUNTIME,),
        maximum_timeline_entries=maximum,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        runtime_health=health or value.health(observed_at=NOW),
    )


def evidence(index):
    reference = f"evd_test_diag_{index:04d}"
    return BoundedEvidence(
        evidence_id=reference,
        evidence_type=EvidenceType.AUDIT_INTEGRITY,
        requirement_references=(
            ConstitutionalRequirementReference(
                constitutional_source="ASTRA-010",
                requirement_id="AIR-CM-009",
                requirement_version="1.0.0",
            ),
        ),
        actor_or_service_class=ActorOrServiceClass.COMPONENT,
        decision_or_operation_reference=f"diagnostic:test:{index}",
        timestamp=NOW + timedelta(seconds=index),
        sensitivity_class=SensitivityClass.INTERNAL,
        minimization_class=MinimizationClass.METADATA_ONLY,
        retention_class=RetentionClass.GOVERNANCE_RECORD,
        integrity=EvidenceIntegrityMetadata(
            source_system="astra_ai:test_fixture",
            provenance_reference="ASTRA-IMP-011:test",
            content_digest="sha256:" + f"{index:064x}",
        ),
        correction=EvidenceCorrectionMetadata(evidence_version="1.0.0"),
        redaction_status=RedactionStatus.NOT_REQUIRED,
    )


def test_runtime_registers_exactly_one_lifecycle_bound_projection_engine():
    value = runtime()
    assert value.registered_component_identifiers.count(
        AstraRuntimeComponentIdentifier.DIAGNOSTIC_PROJECTION
    ) == 1
    interface = value.diagnostic_projection
    request = runtime_request(value)
    value.shutdown()
    with pytest.raises(AstraRuntimeError):
        interface.project(request, created_at=NOW)


def test_runtime_issued_exact_request_required_and_copies_rejected():
    value = runtime()
    request = runtime_request(value)
    assert value.diagnostic_projection.project(request, created_at=NOW).projection_kind.value == "runtime_summary"
    with pytest.raises(AstraDiagnosticProjectionError, match="exact Runtime-owned"):
        value.diagnostic_projection.project(request.model_copy(), created_at=NOW)
    caller_created = AstraDiagnosticProjectionRequest(
        **request.model_dump(),
        runtime_health=request.runtime_health,
        authority_token=object(),
    )
    with pytest.raises(AstraDiagnosticProjectionError, match="exact Runtime-owned"):
        value.diagnostic_projection.project(caller_created, created_at=NOW)


def test_altered_foreign_expired_and_stale_requests_fail():
    value = runtime()
    request = runtime_request(value)
    with pytest.raises(AstraDiagnosticProjectionError):
        value.diagnostic_projection.project(
            request.model_copy(update={"maximum_timeline_entries": 1}), created_at=NOW
        )
    foreign = runtime(suffix="e")
    with pytest.raises(AstraDiagnosticProjectionError):
        foreign.diagnostic_projection.project(request, created_at=NOW)
    with pytest.raises(AstraDiagnosticProjectionError, match="expired"):
        value.diagnostic_projection.project(request, created_at=NOW + timedelta(minutes=16))


def test_runtime_projection_is_internal_structural_and_deterministic():
    value = runtime()
    first = value.diagnostic_projection.project(runtime_request(value), created_at=NOW)
    second = value.diagnostic_projection.project(
        runtime_request(value, request_id="diag_req_runtime_0002"), created_at=NOW
    )
    assert first.completeness is AstraDiagnosticCompleteness.COMPLETE
    assert first.internal_only is True
    assert not first.api_exposure_authorized
    assert not first.ui_exposure_authorized
    assert not first.public_access_authorized
    assert not first.production_exposure_approved
    assert first.authoritative_configuration_state == "disabled"
    assert first.production_authorization_state == "not_approved"
    assert first.projection_id != second.projection_id
    assert first.component_states == second.component_states


def test_request_projection_uses_real_certified_objects_and_does_not_infer_intent_plan_link():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.resolve(snapshot, assembly.intent_request(snapshot))
    plan = assembly.plan(snapshot)
    request = assembly.runtime.diagnostic_projection.issue_request(
        projection_request_id="diag_req_request_0001",
        projection_kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
        requested_sections=(
            AstraDiagnosticSection.CONVERSATION,
            AstraDiagnosticSection.INTENT,
            AstraDiagnosticSection.PLANNING,
            AstraDiagnosticSection.EVIDENCE,
        ),
        maximum_timeline_entries=50,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        conversation_snapshot=snapshot,
        conversation_engine=assembly.engine,
        intent_resolution=intent,
        plan=plan,
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    link = next(
        item for item in projection.correlation_manifest.link_results if item.relationship == "intent_plan"
    )
    assert link.proof_state is AstraDiagnosticProofState.MISSING
    assert projection.completeness is AstraDiagnosticCompleteness.PARTIAL
    assert all(item.relationship != "read_authorization_plan" for item in projection.correlation_manifest.link_results)


def test_same_ids_or_timestamps_do_not_create_missing_relationships():
    assembly = _Assembly()
    snapshot = assembly.active_turn()
    intent = assembly.resolve(snapshot, assembly.intent_request(snapshot))
    plan = assembly.plan(snapshot)
    request = assembly.runtime.diagnostic_projection.issue_request(
        projection_request_id="diag_req_request_0002",
        projection_kind=AstraDiagnosticProjectionKind.REQUEST_DIAGNOSTIC,
        requested_sections=(AstraDiagnosticSection.INTENT, AstraDiagnosticSection.PLANNING),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
        requested_at=NOW,
        intent_resolution=intent,
        plan=plan,
    )
    projection = assembly.runtime.diagnostic_projection.project(request, created_at=NOW)
    assert any(
        link.relationship == "intent_plan" and link.proof_state is AstraDiagnosticProofState.MISSING
        for link in projection.correlation_manifest.link_results
    )


def test_missing_required_evidence_is_visible_and_projection_unavailable():
    value = runtime()
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_evidence_0001",
        projection_kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        requested_sections=(AstraDiagnosticSection.EVIDENCE,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        evidence_references=("evd_missing_diag_0001",),
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    assert projection.completeness is AstraDiagnosticCompleteness.UNAVAILABLE
    assert projection.evidence_summaries[0].overall_integrity is AstraDiagnosticOverallIntegrity.MISSING
    assert projection.evidence_references == (projection.evidence_references[-1],)


def test_missing_optional_runtime_evidence_is_partial_not_unavailable():
    value = runtime()
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_runtime_0003",
        projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
        requested_sections=(AstraDiagnosticSection.RUNTIME, AstraDiagnosticSection.EVIDENCE),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        runtime_health=value.health(observed_at=NOW),
        evidence_references=("evd_missing_optional_0001",),
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    assert projection.completeness is AstraDiagnosticCompleteness.PARTIAL


def test_runtime_sink_resolution_is_structural_and_digest_not_reproducible():
    value = runtime()
    stored = value.evidence_sink.append(evidence(1))
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_evidence_0002",
        projection_kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        requested_sections=(AstraDiagnosticSection.EVIDENCE,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        evidence_references=(stored.evidence_id,),
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    summary = projection.evidence_summaries[0]
    assert summary.overall_integrity is AstraDiagnosticOverallIntegrity.RESOLVED_STRUCTURAL
    assert summary.digest_status is AstraDiagnosticDigestStatus.NOT_REPRODUCIBLE
    assert stored.evidence_id in projection.evidence_references


def test_redaction_precedes_partial_and_complete():
    value = runtime()
    redacted = evidence(9).model_copy(
        update={
            "sensitivity_class": SensitivityClass.RESTRICTED,
            "minimization_class": MinimizationClass.NO_PAYLOAD,
            "redaction_status": RedactionStatus.REDACTED,
        }
    )
    value.evidence_sink.append(redacted)
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_evidence_0004",
        projection_kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        requested_sections=(AstraDiagnosticSection.EVIDENCE,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
        requested_at=NOW,
        evidence_references=(redacted.evidence_id,),
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    assert projection.completeness is AstraDiagnosticCompleteness.REDACTED
    assert projection.redaction_state == "redacted"


def test_mutable_runtime_payload_and_unregistered_health_copy_are_rejected():
    value = runtime()
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_runtime_0004",
        projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
        requested_sections=(AstraDiagnosticSection.RUNTIME,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        runtime_health=value,
    )
    with pytest.raises(AstraDiagnosticProjectionError):
        value.diagnostic_projection.project(request, created_at=NOW)
    health = value.health(observed_at=NOW)
    copied = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_runtime_0005",
        projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
        requested_sections=(AstraDiagnosticSection.RUNTIME,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        runtime_health=health.model_copy(),
    )
    with pytest.raises(AstraDiagnosticProjectionError, match="Exact Runtime-produced"):
        value.diagnostic_projection.project(copied, created_at=NOW)


def test_component_health_summary_requires_exact_runtime_output_and_health_stops():
    value = runtime()
    planning_health = value.planning.health(observed_at=NOW)
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_health_0001",
        projection_kind=AstraDiagnosticProjectionKind.COMPONENT_HEALTH_SUMMARY,
        requested_sections=(AstraDiagnosticSection.COMPONENT_HEALTH,),
        maximum_timeline_entries=10,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        component_health_snapshots=(planning_health,),
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    assert any(item.component_name == "component_health_1" for item in projection.component_states)
    engine = value._diagnostic_projection
    value.shutdown()
    assert engine.health(observed_at=NOW).projection_health_outcome.value == "stopped"


def test_timeline_is_deterministic_bounded_and_truncation_is_partial():
    value = runtime(capacity=100)
    references = tuple(value.evidence_sink.append(evidence(index)).evidence_id for index in range(1, 56))
    request = value.diagnostic_projection.issue_request(
        projection_request_id="diag_req_evidence_0003",
        projection_kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
        requested_sections=(AstraDiagnosticSection.EVIDENCE,),
        maximum_timeline_entries=50,
        requested_redaction_posture=AstraDiagnosticRedactionPosture.METADATA_ONLY,
        requested_at=NOW,
        evidence_references=references,
    )
    projection = value.diagnostic_projection.project(request, created_at=NOW)
    assert len(projection.timeline_entries) == 50
    assert projection.truncated and projection.remaining_entries_unavailable
    assert projection.completeness is AstraDiagnosticCompleteness.PARTIAL
    assert tuple(item.sequence for item in projection.timeline_entries) == tuple(range(1, 51))
    assert not hasattr(projection, "continuation_token")


def test_evidence_append_failure_releases_no_projection_or_sequence():
    value = runtime(capacity=1)
    value.evidence_sink.append(evidence(1))
    request = runtime_request(value)
    before = value.diagnostic_projection.health(observed_at=NOW)
    with pytest.raises(Exception):
        value.diagnostic_projection.project(request, created_at=NOW)
    after = value.diagnostic_projection.health(observed_at=NOW)
    assert before.last_successful_projection_sequence is None
    assert after.last_successful_projection_sequence is None
    assert value.evidence_sink.count() == 1


def test_projection_health_is_healthy_while_operational_astra_remains_disabled():
    value = runtime()
    health = value.diagnostic_projection.health(observed_at=NOW)
    assert health.projection_health_outcome.value == "healthy"
    assert health.runtime_health_outcome == "healthy"
    assert value.read_access_authorization.health(observed_at=NOW).health_outcome.value == "degraded"


def test_no_global_listing_pagination_or_external_surface():
    value = runtime()
    interface = value.diagnostic_projection
    assert not hasattr(interface, "list")
    assert not hasattr(interface, "list_all")
    assert not hasattr(interface, "enumerate")
    request = runtime_request(value)
    projection = interface.project(request, created_at=NOW)
    dumped = projection.model_dump(mode="json")
    forbidden = ("credential", "authority_token", "proof", "sql", "records", "payload")
    assert not any(term in json_text.lower() for term in forbidden for json_text in (str(dumped),))
