from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    assert_no_prohibited_contract_material,
)

DIAGNOSTIC_PROJECTION_VERSION = "1.0.0"
MAXIMUM_PROJECTION_REQUESTS = 200
MAXIMUM_TIMELINE_ENTRIES = 50


class AstraDiagnosticProjectionError(ValueError):
    pass


class AstraDiagnosticProjectionKind(StrEnum):
    RUNTIME_SUMMARY = "runtime_summary"
    REQUEST_DIAGNOSTIC = "request_diagnostic"
    EVIDENCE_SUMMARY = "evidence_summary"
    COMPONENT_HEALTH_SUMMARY = "component_health_summary"


class AstraDiagnosticSection(StrEnum):
    RUNTIME = "runtime"
    CONVERSATION = "conversation"
    INTENT = "intent"
    PLANNING = "planning"
    READ_AUTHORIZATION = "read_authorization"
    EVIDENCE = "evidence"
    COMPONENT_HEALTH = "component_health"


class AstraDiagnosticRedactionPosture(StrEnum):
    METADATA_ONLY = "metadata_only"
    STRICT = "strict"


class AstraDiagnosticCompleteness(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    REDACTED = "redacted"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticStageState(StrEnum):
    AVAILABLE = "available"
    BLOCKED = "blocked"
    MISSING = "missing"
    NOT_REACHED = "not_reached"
    NOT_APPLICABLE = "not_applicable"
    REDACTED = "redacted"
    UNAVAILABLE = "unavailable"
    CONFLICTING = "conflicting"


class AstraDiagnosticProofState(StrEnum):
    PROVEN = "proven"
    MISSING = "missing"
    CONFLICTING = "conflicting"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"
    REDACTED = "redacted"


class AstraDiagnosticReasonCode(StrEnum):
    AUTHORITATIVE_CONFIGURATION_DISABLED = "authoritative_configuration_disabled"
    GOVERNANCE_FAIL_CLOSED = "governance_fail_closed"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    EVIDENCE_REFERENCE_MISSING = "evidence_reference_missing"
    EVIDENCE_CONTRACT_INVALID = "evidence_contract_invalid"
    EVIDENCE_PROVENANCE_INVALID = "evidence_provenance_invalid"
    EVIDENCE_DIGEST_NOT_REPRODUCIBLE = "evidence_digest_not_reproducible"
    EVIDENCE_DIGEST_MISMATCH = "evidence_digest_mismatch"
    DIGEST_VERIFICATION_CONTRACT_UNAVAILABLE = "digest_verification_contract_unavailable"
    CORRELATION_REFERENCE_ABSENT = "correlation_reference_absent"
    CERTIFIED_INTENT_PLAN_REFERENCE_ABSENT = "certified_intent_plan_reference_absent"
    CONFLICTING_CERTIFIED_REFERENCES = "conflicting_certified_references"
    AUTHORIZATION_NOT_REACHED = "authorization_not_reached"
    PLANNING_NOT_ACTIONABLE = "planning_not_actionable"
    PRODUCTION_NOT_APPROVED = "production_not_approved"
    REDACTED_BY_SENSITIVITY = "redacted_by_sensitivity"
    NOT_APPLICABLE_DUE_TO_PRIOR_STAGE = "not_applicable_due_to_prior_stage"
    TIMELINE_TRUNCATED = "timeline_truncated"
    HISTORICAL_LINK_NOT_RECORDED = "historical_link_not_recorded"


class AstraDiagnosticReferenceStatus(StrEnum):
    RESOLVED = "resolved"
    MISSING = "missing"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticContractStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticProvenanceStatus(StrEnum):
    VALID_STRUCTURAL = "valid_structural"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticDigestStatus(StrEnum):
    VERIFIED = "verified"
    MISMATCH = "mismatch"
    NOT_REPRODUCIBLE = "not_reproducible"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticOverallIntegrity(StrEnum):
    RESOLVED_STRUCTURAL = "resolved_structural"
    INVALID = "invalid"
    MISSING = "missing"
    UNAVAILABLE = "unavailable"


class AstraDiagnosticProjectionHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AstraDiagnosticProjectionRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)
    projection_request_id: str = Field(pattern=r"^diag_req_[a-z0-9][a-z0-9_-]{7,120}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    projection_kind: AstraDiagnosticProjectionKind
    requested_sections: tuple[AstraDiagnosticSection, ...] = Field(min_length=1, max_length=7)
    conversation_reference: str | None = None
    current_turn_reference: str | None = None
    intent_reference: str | None = None
    plan_reference: str | None = None
    read_authorization_reference: str | None = None
    evidence_references: tuple[str, ...] = Field(default_factory=tuple, max_length=100)
    maximum_timeline_entries: int = Field(ge=1, le=MAXIMUM_TIMELINE_ENTRIES)
    requested_redaction_posture: AstraDiagnosticRedactionPosture
    requested_at: datetime
    expires_at: datetime
    request_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    runtime_health: Any = Field(default=None, exclude=True)
    conversation_snapshot: Any = Field(default=None, exclude=True)
    intent_resolution: Any = Field(default=None, exclude=True)
    plan: Any = Field(default=None, exclude=True)
    read_authorization_decision: Any = Field(default=None, exclude=True)
    component_health_snapshots: tuple[Any, ...] = Field(default_factory=tuple, exclude=True, max_length=10)
    authority_token: Any = Field(exclude=True)

    @model_validator(mode="after")
    def validate_request(self):
        _aware(self.requested_at)
        _aware(self.expires_at)
        if self.expires_at <= self.requested_at:
            raise AstraDiagnosticProjectionError("Projection request expiry must follow issuance.")
        if len(self.requested_sections) != len(set(self.requested_sections)):
            raise AstraDiagnosticProjectionError("Requested diagnostic sections must be unique.")
        if len(self.evidence_references) != len(set(self.evidence_references)):
            raise AstraDiagnosticProjectionError("Evidence references must be unique.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraDiagnosticLinkResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_reference: str
    target_reference: str | None
    relationship: str = Field(pattern=r"^[a-z][a-z0-9_]{2,80}$")
    proof_state: AstraDiagnosticProofState
    reason_code: AstraDiagnosticReasonCode | None = None


class AstraDiagnosticCorrelationManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    manifest_id: str = Field(pattern=r"^diag_manifest_[a-f0-9]{24}$")
    runtime_instance_id: str
    projection_request_id: str
    conversation_reference: str | None
    current_turn_reference: str | None
    intent_reference: str | None
    plan_reference: str | None
    read_authorization_reference: str | None
    evidence_references: tuple[str, ...] = Field(max_length=100)
    link_results: tuple[AstraDiagnosticLinkResult, ...] = Field(max_length=20)
    completeness: AstraDiagnosticCompleteness
    issued_at: datetime
    manifest_version: str


class AstraDiagnosticEvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    evidence_reference: str
    evidence_type: str | None = None
    source_system: str | None = None
    provenance_reference: str | None = None
    recorded_digest_reference: str | None = None
    reference_status: AstraDiagnosticReferenceStatus
    contract_status: AstraDiagnosticContractStatus
    provenance_status: AstraDiagnosticProvenanceStatus
    digest_status: AstraDiagnosticDigestStatus
    overall_integrity: AstraDiagnosticOverallIntegrity
    sensitivity_class: str | None = None
    redaction_status: str | None = None
    observed_at: datetime


class AstraDiagnosticComponentState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    component_name: str = Field(pattern=r"^[a-z][a-z0-9_]{2,80}$")
    state: AstraDiagnosticStageState
    reason_code: AstraDiagnosticReasonCode | None = None
    reference: str | None = None


class AstraDiagnosticTimelineEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    sequence: int = Field(ge=1, le=MAXIMUM_TIMELINE_ENTRIES)
    stage: str = Field(pattern=r"^[a-z][a-z0-9_]{2,80}$")
    state: AstraDiagnosticStageState
    reference: str
    evidence_reference: str | None = None
    timestamp: datetime
    reason_code: AstraDiagnosticReasonCode | None = None
    redaction_state: str = Field(pattern=r"^(none|metadata_only|redacted)$")


class AstraDiagnosticProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    projection_id: str = Field(pattern=r"^diag_projection_[a-f0-9]{24}$")
    projection_request_id: str
    correlation_manifest_id: str
    runtime_instance_id: str
    projection_kind: AstraDiagnosticProjectionKind
    projection_version: str
    completeness: AstraDiagnosticCompleteness
    redaction_state: str = Field(pattern=r"^(none|metadata_only|redacted)$")
    created_at: datetime
    runtime_state: str | None = None
    authoritative_configuration_state: str | None = None
    production_authorization_state: str = "not_approved"
    component_states: tuple[AstraDiagnosticComponentState, ...] = Field(max_length=20)
    evidence_summaries: tuple[AstraDiagnosticEvidenceSummary, ...] = Field(max_length=100)
    correlation_manifest: AstraDiagnosticCorrelationManifest
    timeline_entries: tuple[AstraDiagnosticTimelineEntry, ...] = Field(max_length=MAXIMUM_TIMELINE_ENTRIES)
    truncated: bool
    remaining_entries_unavailable: bool
    reason_codes: tuple[AstraDiagnosticReasonCode, ...] = Field(max_length=20)
    evidence_references: tuple[str, ...] = Field(min_length=1, max_length=101)
    internal_only: bool = True
    api_exposure_authorized: bool = False
    ui_exposure_authorized: bool = False
    public_access_authorized: bool = False
    production_exposure_approved: bool = False


class AstraDiagnosticProjectionHealth(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    runtime_instance_id: str
    runtime_state: str
    runtime_health_outcome: str
    projection_engine_registered: bool
    projection_engine_available: bool
    request_authority_available: bool
    evidence_sink_available: bool
    redaction_policy_valid: bool
    projection_contracts_valid: bool
    last_successful_projection_sequence: int | None
    projection_health_outcome: AstraDiagnosticProjectionHealthOutcome
    observed_at: datetime


class AstraDiagnosticProjectionEngine:
    def __init__(self, *, runtime: Any) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._authority_token = object()
        self._requests: dict[str, AstraDiagnosticProjectionRequest] = {}
        self._certified_outputs: dict[int, Any] = {}
        self._conversation_validated_requests: set[str] = set()
        self._sequence = 0

    def register_certified_output(self, value: Any) -> None:
        if value is not None:
            if len(self._certified_outputs) >= 500:
                self._certified_outputs.pop(next(iter(self._certified_outputs)))
            self._certified_outputs[id(value)] = value

    def issue_request(
        self,
        *,
        projection_request_id: str,
        projection_kind: AstraDiagnosticProjectionKind,
        requested_sections: tuple[AstraDiagnosticSection, ...],
        maximum_timeline_entries: int,
        requested_redaction_posture: AstraDiagnosticRedactionPosture,
        requested_at: datetime,
        runtime_health: Any = None,
        conversation_snapshot: Any = None,
        intent_resolution: Any = None,
        plan: Any = None,
        read_authorization_decision: Any = None,
        evidence_references: tuple[str, ...] = (),
        component_health_snapshots: tuple[Any, ...] = (),
        conversation_engine: Any = None,
    ) -> AstraDiagnosticProjectionRequest:
        self._require_ready()
        if len(self._requests) >= MAXIMUM_PROJECTION_REQUESTS:
            raise AstraDiagnosticProjectionError("Projection request authority capacity exhausted.")
        if conversation_snapshot is not None:
            from app.modules.astra_ai.conversation_context import AstraConversationContextEngine

            if (
                not isinstance(conversation_engine, AstraConversationContextEngine)
                or getattr(conversation_engine, "_runtime", None) is not self._runtime
                or conversation_engine.get_conversation(
                    conversation_snapshot.metadata.conversation_id
                )
                != conversation_snapshot
            ):
                raise AstraDiagnosticProjectionError(
                    "Current Runtime-owned conversation snapshot authority required."
                )
        request = AstraDiagnosticProjectionRequest(
            projection_request_id=projection_request_id,
            runtime_instance_id=self._runtime_instance_id,
            projection_kind=projection_kind,
            requested_sections=requested_sections,
            conversation_reference=_conversation_reference(conversation_snapshot),
            current_turn_reference=_turn_reference(conversation_snapshot),
            intent_reference=getattr(intent_resolution, "intent_id", None),
            plan_reference=getattr(plan, "plan_id", None),
            read_authorization_reference=getattr(read_authorization_decision, "authorization_decision_id", None),
            evidence_references=evidence_references,
            maximum_timeline_entries=maximum_timeline_entries,
            requested_redaction_posture=requested_redaction_posture,
            requested_at=requested_at,
            expires_at=requested_at + timedelta(minutes=15),
            request_version=DIAGNOSTIC_PROJECTION_VERSION,
            runtime_health=runtime_health,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=plan,
            read_authorization_decision=read_authorization_decision,
            component_health_snapshots=component_health_snapshots,
            authority_token=self._authority_token,
        )
        if request.projection_request_id in self._requests:
            raise AstraDiagnosticProjectionError("Duplicate projection request identifier.")
        self._requests[request.projection_request_id] = request
        if conversation_snapshot is not None:
            self._conversation_validated_requests.add(request.projection_request_id)
        return request

    def project(self, request: AstraDiagnosticProjectionRequest, *, created_at: datetime | None = None):
        self._require_ready()
        timestamp = created_at or datetime.now(timezone.utc)
        _aware(timestamp)
        self._validate_request(request, timestamp)
        inputs = self._validate_inputs(request)
        declared_evidence = self._declared_evidence_references(request)
        evidence_summaries, evidence_records, evidence_missing, redacted = self._resolve_evidence(
            declared_evidence, timestamp
        )
        required_missing = evidence_missing and request.projection_kind is not (
            AstraDiagnosticProjectionKind.RUNTIME_SUMMARY
        )
        optional_missing = evidence_missing and not required_missing
        resolved_evidence_references = tuple(item.evidence_id for item in evidence_records)
        manifest = self._manifest(request, inputs, declared_evidence, timestamp)
        components = self._component_states(request, inputs)
        timeline, truncated = self._timeline(request, inputs, evidence_records)
        completeness = self._completeness(
            request=request,
            manifest=manifest,
            required_missing=required_missing,
            optional_missing=optional_missing,
            redacted=redacted,
            truncated=truncated,
        )
        reasons = self._reason_codes(request, manifest, evidence_summaries, truncated)
        semantic = {
            "request": request.model_dump(mode="json"),
            "manifest": manifest.model_dump(mode="json"),
            "components": tuple(item.model_dump(mode="json") for item in components),
            "evidence": tuple(item.model_dump(mode="json") for item in evidence_summaries),
            "timeline": tuple(item.model_dump(mode="json") for item in timeline),
            "completeness": completeness.value,
            "reasons": tuple(item.value for item in reasons),
        }
        digest = hashlib.sha256(_canonical(semantic).encode()).hexdigest()
        projection_id = f"diag_projection_{digest[:24]}"
        next_sequence = self._sequence + 1
        operation_evidence = self._projection_evidence(
            request=request,
            projection_id=projection_id,
            digest=digest,
            sequence=next_sequence,
            timestamp=timestamp,
        )
        self._runtime.append_evidence(operation_evidence)
        projection = AstraDiagnosticProjection(
            projection_id=projection_id,
            projection_request_id=request.projection_request_id,
            correlation_manifest_id=manifest.manifest_id,
            runtime_instance_id=self._runtime_instance_id,
            projection_kind=request.projection_kind,
            projection_version=DIAGNOSTIC_PROJECTION_VERSION,
            completeness=completeness,
            redaction_state="redacted" if redacted else "metadata_only",
            created_at=timestamp,
            runtime_state=_runtime_state(inputs.get("runtime_health")),
            authoritative_configuration_state=_configuration_state(inputs.get("runtime_health")),
            production_authorization_state="not_approved",
            component_states=components,
            evidence_summaries=evidence_summaries,
            correlation_manifest=manifest,
            timeline_entries=timeline,
            truncated=truncated,
            remaining_entries_unavailable=truncated,
            reason_codes=reasons,
            evidence_references=resolved_evidence_references + (operation_evidence.evidence_id,),
        )
        self._sequence = next_sequence
        return projection

    def health(self, *, observed_at: datetime | None = None) -> AstraDiagnosticProjectionHealth:
        timestamp = observed_at or datetime.now(timezone.utc)
        runtime_health = self._runtime.health(observed_at=timestamp)
        ready = getattr(self._runtime.state, "value", None) == "ready"
        registered = "diagnostic_projection" in tuple(
            item.value for item in self._runtime.registered_component_identifiers
        )
        structural = all(
            (
                ready,
                registered,
                runtime_health.configuration_valid,
                runtime_health.evidence_sink_available,
                self._authority_token is not None,
            )
        )
        return AstraDiagnosticProjectionHealth(
            runtime_instance_id=self._runtime_instance_id,
            runtime_state=getattr(self._runtime.state, "value", str(self._runtime.state)),
            runtime_health_outcome=runtime_health.health_outcome.value,
            projection_engine_registered=registered,
            projection_engine_available=ready,
            request_authority_available=ready and self._authority_token is not None,
            evidence_sink_available=runtime_health.evidence_sink_available,
            redaction_policy_valid=True,
            projection_contracts_valid=True,
            last_successful_projection_sequence=self._sequence or None,
            projection_health_outcome=(
                AstraDiagnosticProjectionHealthOutcome.STOPPED
                if not ready
                else AstraDiagnosticProjectionHealthOutcome.HEALTHY
                if structural
                else AstraDiagnosticProjectionHealthOutcome.DEGRADED
            ),
            observed_at=timestamp,
        )

    def _validate_request(self, request, timestamp):
        if not isinstance(request, AstraDiagnosticProjectionRequest):
            raise AstraDiagnosticProjectionError("Runtime-issued projection request required.")
        issued = self._requests.get(request.projection_request_id)
        if issued is not request or request.authority_token is not self._authority_token:
            raise AstraDiagnosticProjectionError("Projection request lacks exact Runtime-owned authority.")
        if request.runtime_instance_id != self._runtime_instance_id:
            raise AstraDiagnosticProjectionError("Foreign-runtime projection request.")
        if timestamp > request.expires_at:
            raise AstraDiagnosticProjectionError("Projection request expired.")

    def _validate_inputs(self, request):
        from app.modules.astra_ai.conversation_context import AstraConversationSnapshot
        from app.modules.astra_ai.intent_resolution import AstraIntentResolution
        from app.modules.astra_ai.planning import AstraProposedPlan
        from app.modules.astra_ai.read_access_authorization import AstraReadAuthorizationDecision
        from app.modules.astra_ai.runtime import AstraRuntimeHealthSnapshot

        expected = (
            ("runtime_health", request.runtime_health, AstraRuntimeHealthSnapshot),
            ("conversation_snapshot", request.conversation_snapshot, AstraConversationSnapshot),
            ("intent_resolution", request.intent_resolution, AstraIntentResolution),
            ("plan", request.plan, AstraProposedPlan),
            ("read_authorization_decision", request.read_authorization_decision, AstraReadAuthorizationDecision),
        )
        result = {}
        for name, value, contract in expected:
            if value is None:
                continue
            if not isinstance(value, contract):
                raise AstraDiagnosticProjectionError(f"Certified immutable {name} required.")
            runtime_id = _input_runtime_id(value)
            if runtime_id is not None and runtime_id != self._runtime_instance_id:
                raise AstraDiagnosticProjectionError(f"Foreign-runtime {name}.")
            if name == "conversation_snapshot":
                if request.projection_request_id not in self._conversation_validated_requests:
                    raise AstraDiagnosticProjectionError(
                        "Conversation snapshot lacks Runtime-owned validation."
                    )
            elif self._certified_outputs.get(id(value)) is not value:
                raise AstraDiagnosticProjectionError(
                    f"Exact Runtime-produced {name} is required."
                )
            result[name] = value
        self._validate_required_inputs(request, result)
        for snapshot in request.component_health_snapshots:
            if not isinstance(snapshot, _component_health_types()) or not snapshot.model_config.get(
                "frozen", False
            ):
                raise AstraDiagnosticProjectionError("Immutable certified component health snapshot required.")
            runtime_id = getattr(snapshot, "runtime_instance_id", None)
            if runtime_id and runtime_id != self._runtime_instance_id:
                raise AstraDiagnosticProjectionError("Foreign-runtime component health snapshot.")
            if self._certified_outputs.get(id(snapshot)) is not snapshot:
                raise AstraDiagnosticProjectionError("Exact Runtime-produced component health snapshot required.")
        return result

    def _validate_required_inputs(self, request, inputs):
        sections = set(request.requested_sections)
        required = {
            AstraDiagnosticSection.RUNTIME: "runtime_health",
            AstraDiagnosticSection.CONVERSATION: "conversation_snapshot",
            AstraDiagnosticSection.INTENT: "intent_resolution",
            AstraDiagnosticSection.PLANNING: "plan",
            AstraDiagnosticSection.READ_AUTHORIZATION: "read_authorization_decision",
        }
        if request.projection_kind is AstraDiagnosticProjectionKind.RUNTIME_SUMMARY:
            required = {AstraDiagnosticSection.RUNTIME: "runtime_health"}
        for section, name in required.items():
            if section in sections and name not in inputs:
                raise AstraDiagnosticProjectionError(f"Requested {section.value} snapshot is required.")
        if request.projection_kind is AstraDiagnosticProjectionKind.COMPONENT_HEALTH_SUMMARY:
            if not request.component_health_snapshots:
                raise AstraDiagnosticProjectionError("Requested component health snapshots are required.")
        if request.projection_kind is AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY and not request.evidence_references:
            raise AstraDiagnosticProjectionError("Evidence summary requires explicit evidence references.")

    def _declared_evidence_references(self, request):
        values = list(request.evidence_references)
        for value in (request.intent_resolution, request.plan, request.read_authorization_decision):
            values.extend(getattr(value, "evidence_references", ()))
        ordered = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return tuple(ordered)

    def _resolve_evidence(self, references, timestamp):
        stored = {item.evidence_id: item for item in self._runtime.retrieve_evidence()}
        summaries = []
        records = []
        missing = False
        redacted = False
        for reference in references:
            evidence = stored.get(reference)
            if evidence is None:
                missing = True
                summaries.append(_missing_evidence_summary(reference, timestamp))
                continue
            try:
                validated = BoundedEvidence.model_validate(evidence.model_dump(mode="python"))
            except Exception:
                summaries.append(_invalid_evidence_summary(reference, timestamp))
                missing = True
                continue
            if validated.evidence_id != reference:
                summaries.append(_invalid_evidence_summary(reference, timestamp))
                missing = True
                continue
            is_redacted = validated.redaction_status is RedactionStatus.REDACTED
            redacted = redacted or is_redacted
            summaries.append(
                AstraDiagnosticEvidenceSummary(
                    evidence_reference=reference,
                    evidence_type=validated.evidence_type.value,
                    source_system=validated.integrity.source_system,
                    provenance_reference=validated.integrity.provenance_reference,
                    recorded_digest_reference=validated.integrity.content_digest,
                    reference_status=AstraDiagnosticReferenceStatus.RESOLVED,
                    contract_status=AstraDiagnosticContractStatus.VALID,
                    provenance_status=AstraDiagnosticProvenanceStatus.VALID_STRUCTURAL,
                    digest_status=AstraDiagnosticDigestStatus.NOT_REPRODUCIBLE,
                    overall_integrity=AstraDiagnosticOverallIntegrity.RESOLVED_STRUCTURAL,
                    sensitivity_class=validated.sensitivity_class.value,
                    redaction_status=validated.redaction_status.value,
                    observed_at=timestamp,
                )
            )
            records.append(validated)
        return tuple(summaries), tuple(records), missing, redacted

    def _manifest(self, request, inputs, evidence_references, timestamp):
        links = []
        conversation = inputs.get("conversation_snapshot")
        intent = inputs.get("intent_resolution")
        plan = inputs.get("plan")
        read = inputs.get("read_authorization_decision")
        if conversation and conversation.current_turn:
            links.append(
                _link(
                    conversation.metadata.conversation_id,
                    conversation.current_turn.turn_id,
                    "conversation_current_turn",
                    AstraDiagnosticProofState.PROVEN,
                )
            )
        if intent:
            links.extend(
                (
                    _link(
                        intent.intent_id,
                        intent.conversation_id,
                        "intent_conversation",
                        AstraDiagnosticProofState.PROVEN,
                    ),
                    _link(
                        intent.intent_id,
                        intent.current_turn_reference,
                        "intent_current_turn",
                        AstraDiagnosticProofState.PROVEN,
                    ),
                )
            )
        if plan:
            links.append(
                _link(plan.plan_id, plan.conversation_id, "plan_conversation", AstraDiagnosticProofState.PROVEN)
            )
        if intent and plan:
            proof_state = (
                AstraDiagnosticProofState.CONFLICTING
                if intent.conversation_id != plan.conversation_id
                else AstraDiagnosticProofState.MISSING
            )
            reason = (
                AstraDiagnosticReasonCode.CONFLICTING_CERTIFIED_REFERENCES
                if proof_state is AstraDiagnosticProofState.CONFLICTING
                else AstraDiagnosticReasonCode.CERTIFIED_INTENT_PLAN_REFERENCE_ABSENT
            )
            links.append(
                _link(
                    intent.intent_id,
                    plan.plan_id,
                    "intent_plan",
                    proof_state,
                    reason,
                )
            )
        if read and intent:
            links.append(
                _link(
                    read.authorization_decision_id,
                    intent.intent_id,
                    "read_authorization_intent",
                    AstraDiagnosticProofState.MISSING,
                    AstraDiagnosticReasonCode.CORRELATION_REFERENCE_ABSENT,
                )
            )
        link_states = {item.proof_state for item in links}
        completeness = (
            AstraDiagnosticCompleteness.PARTIAL
            if link_states & {AstraDiagnosticProofState.MISSING, AstraDiagnosticProofState.CONFLICTING}
            else AstraDiagnosticCompleteness.COMPLETE
        )
        semantic = {
            "request": request.projection_request_id,
            "links": tuple(item.model_dump(mode="json") for item in links),
            "evidence": evidence_references,
        }
        return AstraDiagnosticCorrelationManifest(
            manifest_id=f"diag_manifest_{hashlib.sha256(_canonical(semantic).encode()).hexdigest()[:24]}",
            runtime_instance_id=self._runtime_instance_id,
            projection_request_id=request.projection_request_id,
            conversation_reference=request.conversation_reference,
            current_turn_reference=request.current_turn_reference,
            intent_reference=request.intent_reference,
            plan_reference=request.plan_reference,
            read_authorization_reference=request.read_authorization_reference,
            evidence_references=evidence_references,
            link_results=tuple(links),
            completeness=completeness,
            issued_at=timestamp,
            manifest_version=DIAGNOSTIC_PROJECTION_VERSION,
        )

    def _component_states(self, request, inputs):
        states = []
        runtime_health = inputs.get("runtime_health")
        if runtime_health:
            states.append(
                AstraDiagnosticComponentState(
                    component_name="runtime",
                    state=AstraDiagnosticStageState.AVAILABLE,
                    reference=runtime_health.runtime_identity.startup_instance_id,
                    reason_code=(
                        AstraDiagnosticReasonCode.AUTHORITATIVE_CONFIGURATION_DISABLED
                        if runtime_health.configuration_valid
                        else AstraDiagnosticReasonCode.DEPENDENCY_UNAVAILABLE
                    ),
                )
            )
        for section, name, reference in (
            (AstraDiagnosticSection.CONVERSATION, "conversation", request.conversation_reference),
            (AstraDiagnosticSection.INTENT, "intent", request.intent_reference),
            (AstraDiagnosticSection.PLANNING, "planning", request.plan_reference),
            (AstraDiagnosticSection.READ_AUTHORIZATION, "read_authorization", request.read_authorization_reference),
        ):
            if section not in request.requested_sections:
                states.append(
                    AstraDiagnosticComponentState(
                        component_name=name,
                        state=AstraDiagnosticStageState.NOT_APPLICABLE,
                        reason_code=AstraDiagnosticReasonCode.NOT_APPLICABLE_DUE_TO_PRIOR_STAGE,
                    )
                )
            elif reference is None:
                states.append(
                    AstraDiagnosticComponentState(
                        component_name=name,
                        state=AstraDiagnosticStageState.MISSING,
                        reason_code=AstraDiagnosticReasonCode.CORRELATION_REFERENCE_ABSENT,
                    )
                )
            else:
                value = inputs.get(
                    {
                        "conversation": "conversation_snapshot",
                        "intent": "intent_resolution",
                        "planning": "plan",
                        "read_authorization": "read_authorization_decision",
                    }[name]
                )
                state = AstraDiagnosticStageState.AVAILABLE
                reason = None
                if name == "intent" and getattr(value, "intent_status", None).value == "invalid":
                    state = AstraDiagnosticStageState.BLOCKED
                    reason = AstraDiagnosticReasonCode.GOVERNANCE_FAIL_CLOSED
                if name == "planning" and not getattr(value, "proposed_steps", ()):
                    state = AstraDiagnosticStageState.BLOCKED
                    reason = AstraDiagnosticReasonCode.PLANNING_NOT_ACTIONABLE
                states.append(
                    AstraDiagnosticComponentState(
                        component_name=name, state=state, reference=reference, reason_code=reason
                    )
                )
        for index, snapshot in enumerate(request.component_health_snapshots, start=1):
            health_value = getattr(getattr(snapshot, "health_outcome", None), "value", "unavailable")
            state = (
                AstraDiagnosticStageState.AVAILABLE
                if health_value == "healthy"
                else AstraDiagnosticStageState.UNAVAILABLE
                if health_value == "stopped"
                else AstraDiagnosticStageState.BLOCKED
            )
            states.append(
                AstraDiagnosticComponentState(
                    component_name=f"component_health_{index}",
                    state=state,
                    reference=_input_runtime_id(snapshot),
                    reason_code=(
                        None
                        if state is AstraDiagnosticStageState.AVAILABLE
                        else AstraDiagnosticReasonCode.DEPENDENCY_UNAVAILABLE
                    ),
                )
            )
        return tuple(states)

    def _timeline(self, request, inputs, evidence_records):
        candidates = []
        runtime_health = inputs.get("runtime_health")
        conversation = inputs.get("conversation_snapshot")
        intent = inputs.get("intent_resolution")
        plan = inputs.get("plan")
        read = inputs.get("read_authorization_decision")
        if runtime_health:
            candidates.append(("runtime", runtime_health.runtime_identity.startup_instance_id, runtime_health.health_timestamp))
        if conversation:
            candidates.append(
                ("conversation", conversation.metadata.conversation_id, conversation.metadata.last_activity_at)
            )
        if intent:
            candidates.append(("intent", intent.intent_id, intent.resolved_at))
        if plan:
            candidates.append(("planning", plan.plan_id, plan.created_at))
        if read:
            candidates.append(("read_authorization", read.authorization_decision_id, read.issued_at))
        for evidence in evidence_records:
            candidates.append(("evidence", evidence.evidence_id, evidence.timestamp))
        candidates.sort(key=lambda item: (item[2], item[1], item[0]))
        truncated = len(candidates) > request.maximum_timeline_entries
        candidates = candidates[: request.maximum_timeline_entries]
        return (
            tuple(
                AstraDiagnosticTimelineEntry(
                    sequence=index,
                    stage=stage,
                    state=AstraDiagnosticStageState.AVAILABLE,
                    reference=reference,
                    evidence_reference=reference if stage == "evidence" else None,
                    timestamp=timestamp,
                    redaction_state="metadata_only",
                )
                for index, (stage, reference, timestamp) in enumerate(candidates, start=1)
            ),
            truncated,
        )

    def _completeness(
        self, *, request, manifest, required_missing, optional_missing, redacted, truncated
    ):
        if required_missing:
            return AstraDiagnosticCompleteness.UNAVAILABLE
        if redacted:
            return AstraDiagnosticCompleteness.REDACTED
        if (
            optional_missing
            or truncated
            or manifest.completeness is AstraDiagnosticCompleteness.PARTIAL
        ):
            return AstraDiagnosticCompleteness.PARTIAL
        return AstraDiagnosticCompleteness.COMPLETE

    def _reason_codes(self, request, manifest, evidence_summaries, truncated):
        reasons = []
        for link in manifest.link_results:
            if link.reason_code and link.reason_code not in reasons:
                reasons.append(link.reason_code)
        for summary in evidence_summaries:
            if summary.reference_status is AstraDiagnosticReferenceStatus.MISSING:
                reasons.append(AstraDiagnosticReasonCode.EVIDENCE_REFERENCE_MISSING)
            elif summary.digest_status is AstraDiagnosticDigestStatus.NOT_REPRODUCIBLE:
                reasons.append(AstraDiagnosticReasonCode.EVIDENCE_DIGEST_NOT_REPRODUCIBLE)
        if truncated:
            reasons.append(AstraDiagnosticReasonCode.TIMELINE_TRUNCATED)
        if not reasons and request.projection_kind is AstraDiagnosticProjectionKind.RUNTIME_SUMMARY:
            reasons.append(AstraDiagnosticReasonCode.AUTHORITATIVE_CONFIGURATION_DISABLED)
        return tuple(dict.fromkeys(reasons))

    def _projection_evidence(self, *, request, projection_id, digest, sequence, timestamp):
        evidence_id = (
            "evd_diag_"
            + hashlib.sha256(f"{projection_id}:{sequence}".encode()).hexdigest()[:24]
        )
        return BoundedEvidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.AUDIT_INTEGRITY,
            requirement_references=(
                ConstitutionalRequirementReference(
                    constitutional_source="ASTRA-010",
                    requirement_id="AIR-CM-009",
                    requirement_version="1.0.0",
                ),
            ),
            actor_or_service_class=ActorOrServiceClass.COMPONENT,
            decision_or_operation_reference=projection_id,
            timestamp=timestamp,
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=EvidenceIntegrityMetadata(
                source_system="astra_ai:diagnostic_projection",
                provenance_reference=f"ASTRA-IMP-011:{DIAGNOSTIC_PROJECTION_VERSION}",
                content_digest=f"sha256:{digest}",
            ),
            correction=EvidenceCorrectionMetadata(evidence_version=DIAGNOSTIC_PROJECTION_VERSION),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )

    def _require_ready(self):
        if getattr(self._runtime.state, "value", None) != "ready":
            raise AstraDiagnosticProjectionError("Diagnostic projection requires ready Runtime.")


def _link(source, target, relationship, state, reason=None):
    return AstraDiagnosticLinkResult(
        source_reference=source,
        target_reference=target,
        relationship=relationship,
        proof_state=state,
        reason_code=reason,
    )


def _missing_evidence_summary(reference, timestamp):
    return AstraDiagnosticEvidenceSummary(
        evidence_reference=reference,
        reference_status=AstraDiagnosticReferenceStatus.MISSING,
        contract_status=AstraDiagnosticContractStatus.UNAVAILABLE,
        provenance_status=AstraDiagnosticProvenanceStatus.UNAVAILABLE,
        digest_status=AstraDiagnosticDigestStatus.UNAVAILABLE,
        overall_integrity=AstraDiagnosticOverallIntegrity.MISSING,
        observed_at=timestamp,
    )


def _invalid_evidence_summary(reference, timestamp):
    return AstraDiagnosticEvidenceSummary(
        evidence_reference=reference,
        reference_status=AstraDiagnosticReferenceStatus.RESOLVED,
        contract_status=AstraDiagnosticContractStatus.INVALID,
        provenance_status=AstraDiagnosticProvenanceStatus.UNAVAILABLE,
        digest_status=AstraDiagnosticDigestStatus.UNAVAILABLE,
        overall_integrity=AstraDiagnosticOverallIntegrity.INVALID,
        observed_at=timestamp,
    )


def _input_runtime_id(value):
    if hasattr(value, "runtime_instance_id"):
        return value.runtime_instance_id
    if hasattr(value, "runtime_instance_reference"):
        return value.runtime_instance_reference
    if hasattr(value, "runtime_identity"):
        return value.runtime_identity.startup_instance_id
    if hasattr(value, "metadata"):
        return value.metadata.runtime_instance_id
    return None


def _conversation_reference(value):
    return value.metadata.conversation_id if value is not None else None


def _turn_reference(value):
    return value.current_turn.turn_id if value is not None and value.current_turn is not None else None


def _runtime_state(value):
    return value.runtime_state.value if value is not None else None


def _configuration_state(value):
    if value is None:
        return None
    return "disabled" if value.configuration_valid else "unavailable"


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _component_health_types():
    from app.modules.astra_ai.capability_discovery import AstraCapabilityHealthSnapshot
    from app.modules.astra_ai.intent_resolution import AstraIntentHealthSnapshot
    from app.modules.astra_ai.planning import AstraPlanningHealthSnapshot
    from app.modules.astra_ai.read_access_authorization import AstraReadAuthorizationHealth

    return (
        AstraCapabilityHealthSnapshot,
        AstraIntentHealthSnapshot,
        AstraPlanningHealthSnapshot,
        AstraReadAuthorizationHealth,
        AstraDiagnosticProjectionHealth,
    )


def _aware(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraDiagnosticProjectionError("Timestamp must be timezone-aware.")
