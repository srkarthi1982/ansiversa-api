from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.activation import (
    SUBSCRIPTION_MANAGER_APP_ID,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
)
from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryRequestContext,
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


INTENT_RESOLUTION_VERSION = "1.0.0"


class AstraIntentResolutionError(ValueError):
    pass


class AstraIntentCategory(StrEnum):
    INFORMATION_REQUEST = "information_request"
    CAPABILITY_LOOKUP = "capability_lookup"
    PLANNING_REQUEST = "planning_request"
    CLARIFICATION_RESPONSE = "clarification_response"
    UNSUPPORTED_REQUEST = "unsupported_request"
    ADMINISTRATIVE_REQUEST = "administrative_request"
    SYSTEM_REQUEST = "system_request"


class AstraIntentStatus(StrEnum):
    RESOLVED = "resolved"
    CLARIFICATION_REQUIRED = "clarification_required"
    UNSUPPORTED = "unsupported"
    GOVERNANCE_BLOCKED = "governance_blocked"
    DEFERRED = "deferred"
    REFUSED = "refused"
    INVALID = "invalid"


class AstraIntentConfidence(StrEnum):
    RULE_MATCHED = "rule_matched"
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


class AstraIntentHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AstraDeclaredIntentParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{1,60}$")
    value_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")


class AstraIntentRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)
    intent_request_id: str = Field(pattern=r"^intent_req_[a-z0-9][a-z0-9_-]{7,120}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    current_turn_reference: str = Field(pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")
    request_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    declared_action: str = Field(pattern=r"^[a-z][a-z0-9_]{1,60}$")
    declared_subject: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{1,100}$")
    declared_target: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{1,100}$")
    declared_parameters: tuple[AstraDeclaredIntentParameter, ...] = Field(default_factory=tuple, max_length=12)
    declared_intent_binding: Any = Field(exclude=True)
    constitutional_requirements: tuple[ConstitutionalRequirementReference, ...] = Field(min_length=1, max_length=20)
    timestamp: datetime
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode="after")
    def validate_request(self):
        _aware(self.timestamp)
        names = tuple(item.name for item in self.declared_parameters)
        if len(names) != len(set(names)):
            raise AstraIntentResolutionError("Declared parameter names must be unique.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraIntentResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    intent_id: str = Field(pattern=r"^intent_[a-f0-9]{24}$")
    intent_request_id: str
    runtime_instance_id: str
    conversation_id: str
    current_turn_reference: str
    intent_status: AstraIntentStatus
    intent_confidence: AstraIntentConfidence
    intent_category: AstraIntentCategory
    resolved_capability_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    clarification_required: bool
    planning_eligible: bool
    governance_outcome: GovernanceOutcome
    governance_decision_reference: str
    evidence_references: tuple[str, ...]
    execution_authorization_state: str = Field(default="not_authorized", pattern=r"^not_authorized$")
    production_authorization_state: ProductionAuthorizationState = ProductionAuthorizationState.NOT_APPROVED
    failure_posture: FailurePosture
    resolved_at: datetime
    version: str

    @model_validator(mode="after")
    def validate_resolution(self):
        _aware(self.resolved_at)
        if self.intent_status is not AstraIntentStatus.RESOLVED and self.planning_eligible:
            raise AstraIntentResolutionError("Only resolved intent may be planning eligible.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraIntentHealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    runtime_instance_id: str
    engine_registered: bool
    engine_available: bool
    configuration_valid: bool
    conversation_dependency_available: bool
    capability_discovery_available: bool
    governance_available: bool
    planning_dependency_available: bool
    evidence_sink_available: bool
    last_successful_resolution_sequence: int | None = None
    health_outcome: AstraIntentHealthOutcome
    observed_at: datetime


_ACTION_RULES = {
    "get_information": (AstraIntentCategory.INFORMATION_REQUEST, False),
    "lookup_capability": (AstraIntentCategory.CAPABILITY_LOOKUP, False),
    "request_plan": (AstraIntentCategory.PLANNING_REQUEST, True),
    "clarify": (AstraIntentCategory.CLARIFICATION_RESPONSE, False),
    "administer": (AstraIntentCategory.ADMINISTRATIVE_REQUEST, False),
    "system_request": (AstraIntentCategory.SYSTEM_REQUEST, False),
}


class AstraIntentResolutionEngine:
    def __init__(self, *, runtime: Any) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._conversation_engine: Any | None = None
        self._sequence = 0

    def resolve(self, request, *, conversation_engine, conversation_snapshot, requester_context):
        self._require_ready()
        if not isinstance(request, AstraIntentRequest):
            raise AstraIntentResolutionError("Intent resolution requires a validated request.")
        self._validate_conversation(request, conversation_engine, conversation_snapshot)
        self._validate_declared_intent_binding(request, conversation_engine, conversation_snapshot)
        discovery = self._runtime.discover_capabilities_for_conversation(
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            request_context=requester_context,
            discovered_at=request.timestamp,
        )
        if discovery.governance_outcome is not GovernanceOutcome.ALLOW:
            return self._release(
                request,
                _status(discovery.governance_outcome),
                AstraIntentConfidence.AMBIGUOUS,
                AstraIntentCategory.UNSUPPORTED_REQUEST,
                (),
                discovery.governance_outcome,
                "CAP-DISC-GOVERNANCE",
                FailurePosture.FAIL_CLOSED,
                (discovery.evidence_reference,),
                conversation_engine,
            )

        category, planning_candidate, confidence = self._match(request)
        capabilities = self._match_capabilities(request, discovery.capabilities)
        if category in {AstraIntentCategory.CAPABILITY_LOOKUP, AstraIntentCategory.PLANNING_REQUEST} and not capabilities:
            category = AstraIntentCategory.UNSUPPORTED_REQUEST
            planning_candidate = False
            confidence = AstraIntentConfidence.UNSUPPORTED

        subscription_private_read = _subscription_private_read_intent(request)
        governance = self._runtime.evaluate_governance(
            GovernanceEvaluationInput(
                evaluation_id=f"INTENT-GOV-{self._sequence + 1:03d}",
                requirement_references=request.constitutional_requirements,
                requested_authority_class=AuthorityClass.ADVISORY,
                safety_classification=(
                    SafetyClassification.PRIVATE_READ
                    if subscription_private_read
                    else SafetyClassification.PUBLIC
                ),
                approval_state=ApprovalState.NOT_REQUIRED,
                configuration_id=ASTRA_CONFIGURATION_ID,
                configuration_version=ASTRA_CONFIGURATION_VERSION,
                requested_app_id=SUBSCRIPTION_MANAGER_APP_ID if subscription_private_read else None,
                requested_capability_scope=(
                    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE if subscription_private_read else None
                ),
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                evaluation_timestamp=request.timestamp,
            )
        )
        self._runtime.append_evidence(governance.evidence)
        outcome = governance.decision.outcome
        if outcome is GovernanceOutcome.ALLOW:
            status = (
                AstraIntentStatus.UNSUPPORTED
                if confidence is AstraIntentConfidence.UNSUPPORTED
                else AstraIntentStatus.CLARIFICATION_REQUIRED
                if confidence in {AstraIntentConfidence.AMBIGUOUS, AstraIntentConfidence.PARTIAL_MATCH}
                else AstraIntentStatus.RESOLVED
            )
        else:
            status = _status(outcome)
            capabilities = ()
            planning_candidate = False
        return self._release(
            request,
            status,
            confidence,
            category,
            tuple(item.capability_id for item in capabilities),
            outcome,
            governance.decision.decision_id,
            governance.decision.failure_posture,
            (discovery.evidence_reference, governance.evidence.evidence_id),
            conversation_engine,
            planning_candidate and status is AstraIntentStatus.RESOLVED,
        )

    def health(self, *, observed_at=None):
        timestamp = observed_at or datetime.now(timezone.utc)
        runtime_health = self._runtime.health(observed_at=timestamp)
        ready = getattr(self._runtime.state, "value", None) == "ready"
        conversation = self._valid_bound_conversation()
        planning = runtime_health.planning_available
        dependencies = all(
            (
                runtime_health.configuration_valid,
                conversation,
                runtime_health.capability_discovery_available,
                runtime_health.governance_available,
                planning,
                runtime_health.evidence_sink_available,
            )
        )
        outcome = (
            AstraIntentHealthOutcome.STOPPED
            if not ready
            else AstraIntentHealthOutcome.HEALTHY
            if dependencies
            else AstraIntentHealthOutcome.DEGRADED
        )
        return AstraIntentHealthSnapshot(
            runtime_instance_id=self._runtime_instance_id,
            engine_registered="intent_resolution"
            in tuple(item.value for item in self._runtime.registered_component_identifiers),
            engine_available=ready,
            configuration_valid=runtime_health.configuration_valid,
            conversation_dependency_available=conversation,
            capability_discovery_available=runtime_health.capability_discovery_available,
            governance_available=runtime_health.governance_available,
            planning_dependency_available=planning,
            evidence_sink_available=runtime_health.evidence_sink_available,
            last_successful_resolution_sequence=self._sequence or None,
            health_outcome=outcome,
            observed_at=timestamp,
        )

    def _match(self, request):
        rule = _ACTION_RULES.get(request.declared_action)
        if rule is None:
            return AstraIntentCategory.UNSUPPORTED_REQUEST, False, AstraIntentConfidence.UNSUPPORTED
        category, planning = rule
        if request.declared_action == "clarify":
            return category, planning, AstraIntentConfidence.PARTIAL_MATCH
        if request.declared_subject is None:
            return category, False, AstraIntentConfidence.AMBIGUOUS
        return category, planning, AstraIntentConfidence.EXACT_MATCH

    def _match_capabilities(self, request, capabilities):
        if request.declared_target is None:
            return ()
        return tuple(
            item
            for item in capabilities
            if item.status is AstraCapabilityStatus.AVAILABLE and item.capability_id == request.declared_target
        )

    def _validate_conversation(self, request, engine, snapshot):
        from app.modules.astra_ai.conversation_context import (
            AstraConversationContextEngine,
            AstraConversationLifecycleState,
            AstraConversationSnapshot,
        )

        if not isinstance(engine, AstraConversationContextEngine) or not isinstance(snapshot, AstraConversationSnapshot):
            raise AstraIntentResolutionError("Certified conversation dependency required.")
        if request.runtime_instance_id != self._runtime_instance_id:
            raise AstraIntentResolutionError("Intent request belongs to a foreign runtime.")
        if snapshot.metadata.runtime_instance_id != self._runtime_instance_id:
            raise AstraIntentResolutionError("Conversation belongs to a foreign runtime.")
        if request.conversation_id != snapshot.metadata.conversation_id or snapshot.current_turn is None:
            raise AstraIntentResolutionError("Current conversation turn is required.")
        if request.current_turn_reference != snapshot.current_turn.turn_id:
            raise AstraIntentResolutionError("Current turn reference does not match.")
        if request.request_reference != snapshot.current_turn.request_reference:
            raise AstraIntentResolutionError("Request reference does not match the certified current turn.")
        try:
            owned = engine.get_conversation(request.conversation_id)
        except Exception as exc:
            raise AstraIntentResolutionError("Conversation is not owned by the engine.") from exc
        if owned != snapshot:
            raise AstraIntentResolutionError("Conversation snapshot is stale or fabricated.")
        if owned.metadata.lifecycle_state is not AstraConversationLifecycleState.ACTIVE:
            raise AstraIntentResolutionError("Intent resolution requires an active conversation.")

    def _validate_declared_intent_binding(self, request, engine, snapshot):
        from app.modules.astra_ai.conversation_context import AstraDeclaredIntentBinding

        binding = request.declared_intent_binding
        if not isinstance(binding, AstraDeclaredIntentBinding):
            raise AstraIntentResolutionError("Owner-issued declared intent binding is required.")
        if not engine.validates_declared_intent_binding(binding):
            raise AstraIntentResolutionError("Declared intent binding was not issued by this conversation engine.")
        expected_identity = (
            self._runtime_instance_id,
            snapshot.metadata.conversation_id,
            snapshot.current_turn.turn_id,
            snapshot.current_turn.request_reference,
        )
        actual_identity = (
            binding.runtime_instance_id,
            binding.conversation_id,
            binding.current_turn_reference,
            binding.request_reference,
        )
        if actual_identity != expected_identity:
            raise AstraIntentResolutionError("Declared intent binding is stale or belongs to another turn.")
        request_signal = (
            request.declared_action,
            request.declared_subject,
            request.declared_target,
            tuple((item.name, item.value_reference) for item in request.declared_parameters),
        )
        bound_signal = (
            binding.declared_action,
            binding.declared_subject,
            binding.declared_target,
            tuple((item.name, item.value_reference) for item in binding.declared_parameters),
        )
        if request_signal != bound_signal:
            raise AstraIntentResolutionError("Declared intent fields do not match the owner-issued binding.")

    def _release(
        self,
        request,
        status,
        confidence,
        category,
        capability_ids,
        outcome,
        decision_reference,
        failure_posture,
        prior_evidence,
        conversation_engine,
        planning_eligible=False,
    ):
        semantic = {
            "request": request.model_dump(mode="json", exclude={"timestamp"}),
            "status": status.value,
            "confidence": confidence.value,
            "category": category.value,
            "capabilities": capability_ids,
            "outcome": outcome.value,
        }
        intent_id = f"intent_{hashlib.sha256(_canonical(semantic).encode()).hexdigest()[:24]}"
        next_sequence = self._sequence + 1
        evidence_id = f"evd_intent_{hashlib.sha256(f'{intent_id}:{next_sequence}'.encode()).hexdigest()[:24]}"
        digest = hashlib.sha256(_canonical(semantic).encode()).hexdigest()
        evidence = BoundedEvidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.GOVERNANCE_DECISION,
            requirement_references=request.constitutional_requirements,
            actor_or_service_class=ActorOrServiceClass.COMPONENT,
            decision_or_operation_reference=intent_id,
            timestamp=request.timestamp,
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=EvidenceIntegrityMetadata(
                source_system="astra_ai:intent_resolution",
                provenance_reference=f"ASTRA-IMP-009:{INTENT_RESOLUTION_VERSION}",
                content_digest=f"sha256:{digest}",
            ),
            correction=EvidenceCorrectionMetadata(evidence_version=INTENT_RESOLUTION_VERSION),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )
        self._runtime.append_evidence(evidence)
        resolution = AstraIntentResolution(
            intent_id=intent_id,
            intent_request_id=request.intent_request_id,
            runtime_instance_id=self._runtime_instance_id,
            conversation_id=request.conversation_id,
            current_turn_reference=request.current_turn_reference,
            intent_status=status,
            intent_confidence=confidence,
            intent_category=category,
            resolved_capability_ids=capability_ids,
            clarification_required=status is AstraIntentStatus.CLARIFICATION_REQUIRED,
            planning_eligible=planning_eligible,
            governance_outcome=outcome,
            governance_decision_reference=decision_reference,
            evidence_references=prior_evidence + (evidence_id,),
            failure_posture=failure_posture,
            resolved_at=request.timestamp,
            version=INTENT_RESOLUTION_VERSION,
        )
        self._conversation_engine = conversation_engine
        self._sequence = next_sequence
        return resolution

    def _valid_bound_conversation(self):
        from app.modules.astra_ai.conversation_context import AstraConversationContextEngine

        engine = self._conversation_engine
        return (
            isinstance(engine, AstraConversationContextEngine)
            and getattr(engine, "_runtime", None) is self._runtime
            and getattr(self._runtime.state, "value", None) == "ready"
        )

    def _require_ready(self):
        if getattr(self._runtime.state, "value", None) != "ready":
            raise AstraIntentResolutionError("Intent Resolution Engine requires a ready runtime.")


def _status(outcome):
    return {
        GovernanceOutcome.ALLOW: AstraIntentStatus.RESOLVED,
        GovernanceOutcome.CLARIFY: AstraIntentStatus.CLARIFICATION_REQUIRED,
        GovernanceOutcome.DEFER: AstraIntentStatus.DEFERRED,
        GovernanceOutcome.REFUSE: AstraIntentStatus.REFUSED,
        GovernanceOutcome.CONTAIN: AstraIntentStatus.GOVERNANCE_BLOCKED,
        GovernanceOutcome.FAIL_CLOSED: AstraIntentStatus.INVALID,
    }[outcome]


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _aware(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraIntentResolutionError("Intent timestamp must be timezone-aware.")


def _subscription_private_read_intent(request: AstraIntentRequest) -> bool:
    subject = request.declared_subject or ""
    return (
        request.declared_action == "get_information"
        and subject in {"subscription", "subscriptions", "subscription_manager"}
    )
