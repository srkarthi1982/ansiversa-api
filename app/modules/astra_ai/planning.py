from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryRequestContext,
    AstraCapabilityExecutionAuthority,
    AstraCapabilityMetadata,
    AstraCapabilityStatus,
)
from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION
from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    ApprovalState,
    AuthorityClass,
    BoundedEvidence,
    ConstitutionalRequirementReference,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    FailurePosture,
    GovernanceOutcome,
    MinimizationClass,
    ProductionAuthorizationState,
    RedactionStatus,
    RetentionClass,
    SafetyClassification,
    SensitivityClass,
    assert_no_prohibited_contract_material,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput


PLANNING_ENGINE_VERSION = "1.0.0"
PLANNING_IMPLEMENTATION_REFERENCE = "ASTRA-IMP-008"
MAXIMUM_PLANNING_STEPS = 20


class AstraPlanningError(ValueError):
    """Raised when a governed proposal cannot be safely formed."""


class AstraRequestedCompletionPosture(StrEnum):
    PROPOSAL_ONLY = "proposal_only"
    CLARIFICATION_ACCEPTABLE = "clarification_acceptable"
    DEFER_ACCEPTABLE = "defer_acceptable"


class AstraPlanStatus(StrEnum):
    PROPOSED = "proposed"
    GOVERNANCE_BLOCKED = "governance_blocked"
    CLARIFICATION_REQUIRED = "clarification_required"
    DEFERRED = "deferred"
    REFUSED = "refused"
    CONTAINED = "contained"
    INVALID = "invalid"


class AstraPlanStepStatus(StrEnum):
    PROPOSED = "proposed"
    BLOCKED = "blocked"
    CLARIFICATION_REQUIRED = "clarification_required"
    DEFERRED = "deferred"
    REFUSED = "refused"


class AstraExecutionAuthorizationState(StrEnum):
    NOT_AUTHORIZED = "not_authorized"


class AstraOwnerAcceptanceState(StrEnum):
    REQUIRED = "required"
    NOT_ACCEPTED = "not_accepted"


class AstraPlanningHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AstraRequestedPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(pattern=r"^step_[a-z0-9][a-z0-9_-]{7,120}$")
    sequence_number: int = Field(ge=1, le=MAXIMUM_PLANNING_STEPS)
    capability_id: str = Field(pattern=r"^cap_[a-z0-9][a-z0-9_-]{7,120}$")
    objective_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    input_reference: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    dependency_step_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=MAXIMUM_PLANNING_STEPS)
    authority_class: AuthorityClass = AuthorityClass.ADVISORY
    safety_classification: SafetyClassification = SafetyClassification.PUBLIC
    approval_state: ApprovalState = ApprovalState.NOT_REQUIRED

    @model_validator(mode="after")
    def validate_metadata_only(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraPlanningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    planning_request_id: str = Field(pattern=r"^planning_req_[a-z0-9][a-z0-9_-]{7,120}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    request_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    objective_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    requester_context_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    constitutional_requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(
        min_length=1, max_length=20
    )
    maximum_step_count: int = Field(ge=1, le=MAXIMUM_PLANNING_STEPS)
    requested_steps: tuple[AstraRequestedPlanStep, ...] = Field(min_length=1, max_length=MAXIMUM_PLANNING_STEPS)
    requested_completion_posture: AstraRequestedCompletionPosture
    planning_timestamp: datetime
    planning_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode="after")
    def validate_bounded_request(self):
        _ensure_timezone_aware(self.planning_timestamp, "Planning timestamp")
        if len(self.requested_steps) > self.maximum_step_count:
            raise AstraPlanningError("Requested steps exceed the bounded maximum step count.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraProposedPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str
    sequence_number: int
    capability_id: str
    capability_version: str
    owning_module: str
    objective_reference: str
    input_reference: str | None = None
    dependency_step_ids: tuple[str, ...]
    authority_class: AuthorityClass
    safety_classification: SafetyClassification
    approval_state: ApprovalState
    owner_acceptance_requirement: AstraOwnerAcceptanceState
    execution_authorization_state: AstraExecutionAuthorizationState
    production_authorization_state: ProductionAuthorizationState
    step_status: AstraPlanStepStatus

    @model_validator(mode="after")
    def validate_non_executable(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraProposedPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_id: str = Field(pattern=r"^plan_[a-f0-9]{24}$")
    planning_request_id: str
    runtime_instance_id: str
    conversation_id: str
    conversation_version: str
    plan_version: str
    created_at: datetime
    plan_status: AstraPlanStatus
    governance_outcome: GovernanceOutcome
    governance_decision_reference: str
    constitutional_requirement_references: tuple[ConstitutionalRequirementReference, ...]
    proposed_steps: tuple[AstraProposedPlanStep, ...]
    evidence_references: tuple[str, ...]
    approval_requirement: ApprovalState
    execution_authorization_state: AstraExecutionAuthorizationState
    production_authorization_state: ProductionAuthorizationState
    owning_service_acceptance_state: AstraOwnerAcceptanceState
    failure_posture: FailurePosture
    provenance_reference: str

    @model_validator(mode="after")
    def validate_plan_boundary(self):
        _ensure_timezone_aware(self.created_at, "Plan creation timestamp")
        if self.governance_outcome is not GovernanceOutcome.ALLOW and self.proposed_steps:
            raise AstraPlanningError("Non-allow plans cannot release actionable proposed steps.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraPlanningHealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_instance_id: str
    engine_registered: bool
    engine_available: bool
    configuration_valid: bool
    capability_discovery_available: bool
    conversation_context_dependency_available: bool
    governance_available: bool
    evidence_sink_available: bool
    last_successful_planning_sequence: int | None = None
    health_outcome: AstraPlanningHealthOutcome
    observed_at: datetime


class AstraPlanningEngine:
    """Deterministic metadata-only proposal builder. It has no execution surface."""

    def __init__(self, *, runtime: Any) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._conversation_context_engine: Any | None = None
        self._operation_sequence = 0

    def propose(
        self,
        request: AstraPlanningRequest,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        requester_context: AstraCapabilityDiscoveryRequestContext,
    ) -> AstraProposedPlan:
        self._require_runtime_ready()
        self._validate_request(request)
        self._validate_conversation(conversation_engine, conversation_snapshot, request)
        self._validate_graph(request)

        discovery = self._runtime.discover_capabilities_for_conversation(
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            request_context=requester_context,
            discovered_at=request.planning_timestamp,
        )
        if discovery.governance_outcome is not GovernanceOutcome.ALLOW:
            return self._blocked_plan(
                request,
                conversation_snapshot,
                discovery.governance_outcome,
                (discovery.evidence_reference,),
                conversation_engine=conversation_engine,
            )

        metadata_by_id = {item.capability_id: item for item in discovery.capabilities}
        requested_ids = tuple(step.capability_id for step in request.requested_steps)
        if len(requested_ids) != len(set(requested_ids)):
            raise AstraPlanningError("Duplicate requested capabilities are not permitted.")
        capabilities = []
        for capability_id in requested_ids:
            capability = metadata_by_id.get(capability_id)
            if capability is None:
                raise AstraPlanningError("Unknown, ineligible, or non-discoverable capability.")
            self._validate_capability(capability)
            capabilities.append(capability)

        governance = self._evaluate_plan_governance(request)
        self._runtime.append_evidence(governance.evidence)
        if governance.decision.outcome is not GovernanceOutcome.ALLOW:
            return self._blocked_plan(
                request,
                conversation_snapshot,
                governance.decision.outcome,
                (discovery.evidence_reference, governance.evidence.evidence_id),
                governance.decision.decision_id,
                governance.decision.failure_posture,
                conversation_engine,
            )

        steps = tuple(
            self._build_step(requested, capability)
            for requested, capability in zip(request.requested_steps, capabilities, strict=True)
        )
        plan = self._prepare_plan(
            request=request,
            snapshot=conversation_snapshot,
            outcome=governance.decision.outcome,
            decision_reference=governance.decision.decision_id,
            failure_posture=governance.decision.failure_posture,
            steps=steps,
            prior_evidence=(discovery.evidence_reference, governance.evidence.evidence_id),
        )
        return self._append_evidence_then_release(plan, request, conversation_engine)

    def health(self, *, observed_at: datetime | None = None) -> AstraPlanningHealthSnapshot:
        timestamp = observed_at or _utc_now()
        runtime_health = self._runtime.health(observed_at=timestamp)
        available = getattr(getattr(self._runtime, "state", None), "value", None) == "ready"
        conversation_available = self._conversation_dependency_available()
        dependencies_available = all(
            (
                runtime_health.configuration_valid,
                runtime_health.capability_discovery_available,
                conversation_available,
                runtime_health.governance_available,
                runtime_health.evidence_sink_available,
            )
        )
        if not available:
            outcome = AstraPlanningHealthOutcome.STOPPED
        elif dependencies_available:
            outcome = AstraPlanningHealthOutcome.HEALTHY
        else:
            outcome = AstraPlanningHealthOutcome.DEGRADED
        return AstraPlanningHealthSnapshot(
            runtime_instance_id=self._runtime_instance_id,
            engine_registered="planning" in tuple(item.value for item in self._runtime.registered_component_identifiers),
            engine_available=available,
            configuration_valid=runtime_health.configuration_valid,
            capability_discovery_available=runtime_health.capability_discovery_available,
            conversation_context_dependency_available=conversation_available,
            governance_available=runtime_health.governance_available,
            evidence_sink_available=runtime_health.evidence_sink_available,
            last_successful_planning_sequence=self._operation_sequence or None,
            health_outcome=outcome,
            observed_at=timestamp,
        )

    def _blocked_plan(
        self,
        request: AstraPlanningRequest,
        snapshot: AstraConversationSnapshot,
        outcome: GovernanceOutcome,
        evidence_references: tuple[str, ...],
        decision_reference: str = "CAP-DISC-GOVERNANCE",
        failure_posture: FailurePosture = FailurePosture.FAIL_CLOSED,
        conversation_engine: Any | None = None,
    ) -> AstraProposedPlan:
        plan = self._prepare_plan(
            request=request,
            snapshot=snapshot,
            outcome=outcome,
            decision_reference=decision_reference,
            failure_posture=failure_posture,
            steps=(),
            prior_evidence=evidence_references,
        )
        return self._append_evidence_then_release(plan, request, conversation_engine)

    def _prepare_plan(self, *, request, snapshot, outcome, decision_reference, failure_posture, steps, prior_evidence):
        semantic = {
            "request": request.model_dump(mode="json", exclude={"planning_timestamp"}),
            "conversation": snapshot.metadata.model_dump(mode="json", exclude={"created_at", "last_activity_at"}),
            "capabilities": [step.model_dump(mode="json") for step in steps],
            "outcome": outcome.value,
        }
        plan_id = f"plan_{hashlib.sha256(_canonical(semantic).encode()).hexdigest()[:24]}"
        approval = (
            ApprovalState.REQUIRED
            if any(
                step.approval_state is not ApprovalState.NOT_REQUIRED
                or step.safety_classification in {SafetyClassification.PRIVATE_WRITE, SafetyClassification.HIGH_IMPACT}
                for step in steps
            )
            else ApprovalState.NOT_REQUIRED
        )
        return AstraProposedPlan(
            plan_id=plan_id,
            planning_request_id=request.planning_request_id,
            runtime_instance_id=self._runtime_instance_id,
            conversation_id=snapshot.metadata.conversation_id,
            conversation_version=snapshot.metadata.conversation_version,
            plan_version=PLANNING_ENGINE_VERSION,
            created_at=request.planning_timestamp,
            plan_status=_status_for(outcome),
            governance_outcome=outcome,
            governance_decision_reference=decision_reference,
            constitutional_requirement_references=request.constitutional_requirement_references,
            proposed_steps=steps,
            evidence_references=prior_evidence,
            approval_requirement=approval,
            execution_authorization_state=AstraExecutionAuthorizationState.NOT_AUTHORIZED,
            production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
            owning_service_acceptance_state=AstraOwnerAcceptanceState.NOT_ACCEPTED,
            failure_posture=failure_posture,
            provenance_reference=f"{PLANNING_IMPLEMENTATION_REFERENCE}:{PLANNING_ENGINE_VERSION}",
        )

    def _append_evidence_then_release(self, plan, request, conversation_engine):
        next_sequence = self._operation_sequence + 1
        digest = hashlib.sha256(
            _canonical(
                {
                    "planning_request_reference": request.request_reference,
                    "plan_reference": plan.plan_id,
                    "governance_decision_reference": plan.governance_decision_reference,
                    "capability_references": [step.capability_id for step in plan.proposed_steps],
                    "requirements": [item.model_dump(mode="json") for item in plan.constitutional_requirement_references],
                    "step_count": len(plan.proposed_steps),
                    "plan_status": plan.plan_status.value,
                    "approval_requirement": plan.approval_requirement.value,
                    "execution_authorization_state": plan.execution_authorization_state.value,
                    "production_authorization_state": plan.production_authorization_state.value,
                    "provenance": plan.provenance_reference,
                }
            ).encode()
        ).hexdigest()
        evidence_id = f"evd_plan_{hashlib.sha256(f'{plan.plan_id}:{next_sequence}'.encode()).hexdigest()[:24]}"
        evidence = BoundedEvidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.GOVERNANCE_DECISION,
            requirement_references=plan.constitutional_requirement_references,
            actor_or_service_class=ActorOrServiceClass.COMPONENT,
            decision_or_operation_reference=plan.plan_id,
            timestamp=plan.created_at,
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=EvidenceIntegrityMetadata(
                source_system="astra_ai:planning",
                provenance_reference=plan.provenance_reference,
                content_digest=f"sha256:{digest}",
            ),
            correction=EvidenceCorrectionMetadata(evidence_version=PLANNING_ENGINE_VERSION),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )
        self._runtime.append_evidence(evidence)
        self._conversation_context_engine = conversation_engine
        self._operation_sequence = next_sequence
        return plan.model_copy(update={"evidence_references": plan.evidence_references + (evidence_id,)})

    def _evaluate_plan_governance(self, request):
        safety = max(
            (step.safety_classification for step in request.requested_steps),
            key=lambda value: _safety_rank(value),
        )
        authority = max(
            (step.authority_class for step in request.requested_steps),
            key=lambda value: _authority_rank(value),
        )
        approval = (
            ApprovalState.REQUIRED
            if any(
                step.approval_state is not ApprovalState.NOT_REQUIRED
                or step.safety_classification in {SafetyClassification.PRIVATE_WRITE, SafetyClassification.HIGH_IMPACT}
                for step in request.requested_steps
            )
            else ApprovalState.NOT_REQUIRED
        )
        sequence = self._operation_sequence + 1
        return self._runtime.evaluate_governance(
            GovernanceEvaluationInput(
                evaluation_id=f"PLAN-GOV-{sequence:03d}",
                requirement_references=request.constitutional_requirement_references,
                requested_authority_class=authority,
                safety_classification=safety,
                approval_state=approval,
                configuration_id=ASTRA_CONFIGURATION_ID,
                configuration_version=ASTRA_CONFIGURATION_VERSION,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                evaluation_timestamp=request.planning_timestamp,
            )
        )

    def _validate_request(self, request):
        if not isinstance(request, AstraPlanningRequest):
            raise AstraPlanningError("Planning requires a validated AstraPlanningRequest.")
        if request.runtime_instance_id != self._runtime_instance_id:
            raise AstraPlanningError("Planning request belongs to a foreign runtime.")

    def _validate_conversation(self, engine, snapshot, request):
        from app.modules.astra_ai.conversation_context import (
            AstraConversationContextEngine,
            AstraConversationLifecycleState,
            AstraConversationSnapshot,
        )

        if not isinstance(engine, AstraConversationContextEngine) or not isinstance(snapshot, AstraConversationSnapshot):
            raise AstraPlanningError("Planning requires the certified Conversation Context Engine and snapshot.")
        if snapshot.metadata.runtime_instance_id != self._runtime_instance_id:
            raise AstraPlanningError("Conversation belongs to a foreign runtime.")
        if snapshot.metadata.conversation_id != request.conversation_id:
            raise AstraPlanningError("Planning request conversation reference does not match the snapshot.")
        try:
            owned = engine.get_conversation(snapshot.metadata.conversation_id)
        except Exception as exc:
            raise AstraPlanningError("Conversation is not owned by the provided engine.") from exc
        if owned != snapshot:
            raise AstraPlanningError("Conversation snapshot is stale or fabricated.")
        if owned.metadata.lifecycle_state in {
            AstraConversationLifecycleState.CLOSED,
            AstraConversationLifecycleState.FAULTED,
        }:
            raise AstraPlanningError("Conversation lifecycle state is not eligible for planning.")
    def _conversation_dependency_available(self) -> bool:
        from app.modules.astra_ai.conversation_context import AstraConversationContextEngine

        engine = self._conversation_context_engine
        return (
            isinstance(engine, AstraConversationContextEngine)
            and getattr(engine, "_runtime", None) is self._runtime
            and getattr(getattr(self._runtime, "state", None), "value", None) == "ready"
            and getattr(getattr(engine, "_runtime", None), "identity", None) is not None
            and engine._runtime.identity.startup_instance_id == self._runtime_instance_id
        )

    def _validate_graph(self, request):
        steps = request.requested_steps
        if tuple(step.sequence_number for step in steps) != tuple(range(1, len(steps) + 1)):
            raise AstraPlanningError("Step sequence numbers must start at one and remain contiguous.")
        identifiers = tuple(step.step_id for step in steps)
        if len(identifiers) != len(set(identifiers)):
            raise AstraPlanningError("Duplicate step identifiers are not permitted.")
        positions = {identifier: index for index, identifier in enumerate(identifiers, start=1)}
        for step in steps:
            if len(step.dependency_step_ids) != len(set(step.dependency_step_ids)):
                raise AstraPlanningError("Duplicate dependency identifiers are not permitted.")
            for dependency in step.dependency_step_ids:
                if dependency == step.step_id:
                    raise AstraPlanningError("Self-dependency is not permitted.")
                if dependency not in positions:
                    raise AstraPlanningError("Dependency identifier does not reference a requested step.")
                if positions[dependency] >= step.sequence_number:
                    raise AstraPlanningError("Dependencies must reference earlier steps only.")

    def _validate_capability(self, capability: AstraCapabilityMetadata):
        if capability.status is not AstraCapabilityStatus.AVAILABLE:
            raise AstraPlanningError("Disabled or deprecated capabilities cannot be proposed.")
        if capability.execution_authority is not AstraCapabilityExecutionAuthority.METADATA_ONLY:
            raise AstraPlanningError("Capability execution authority cannot be established as metadata-only.")

    def _build_step(self, requested, capability):
        return AstraProposedPlanStep(
            step_id=requested.step_id,
            sequence_number=requested.sequence_number,
            capability_id=capability.capability_id,
            capability_version=capability.version,
            owning_module=capability.owning_module,
            objective_reference=requested.objective_reference,
            input_reference=requested.input_reference,
            dependency_step_ids=requested.dependency_step_ids,
            authority_class=requested.authority_class,
            safety_classification=requested.safety_classification,
            approval_state=requested.approval_state,
            owner_acceptance_requirement=AstraOwnerAcceptanceState.REQUIRED,
            execution_authorization_state=AstraExecutionAuthorizationState.NOT_AUTHORIZED,
            production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
            step_status=AstraPlanStepStatus.PROPOSED,
        )

    def _require_runtime_ready(self):
        if getattr(getattr(self._runtime, "state", None), "value", None) != "ready":
            raise AstraPlanningError("Planning Engine requires a ready AstraRuntime owner.")


def _status_for(outcome: GovernanceOutcome) -> AstraPlanStatus:
    return {
        GovernanceOutcome.ALLOW: AstraPlanStatus.PROPOSED,
        GovernanceOutcome.CLARIFY: AstraPlanStatus.CLARIFICATION_REQUIRED,
        GovernanceOutcome.DEFER: AstraPlanStatus.DEFERRED,
        GovernanceOutcome.REFUSE: AstraPlanStatus.REFUSED,
        GovernanceOutcome.CONTAIN: AstraPlanStatus.CONTAINED,
        GovernanceOutcome.FAIL_CLOSED: AstraPlanStatus.GOVERNANCE_BLOCKED,
    }[outcome]


def _safety_rank(value: SafetyClassification) -> int:
    order = tuple(SafetyClassification)
    return order.index(value)


def _authority_rank(value: AuthorityClass) -> int:
    order = tuple(AuthorityClass)
    return order.index(value)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone_aware(timestamp: datetime, field_name: str) -> None:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise AstraPlanningError(f"{field_name} must be timezone-aware.")
