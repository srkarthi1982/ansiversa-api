from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

READ_ACCESS_AUTHORIZATION_VERSION = "1.0.0"
MAX_READ_CAPABILITIES = 100


class AstraReadAuthorizationError(ValueError):
    pass


class AstraReadPurpose(StrEnum):
    USER_REQUESTED_SUMMARY = "user_requested_summary"
    USER_REQUESTED_DETAIL = "user_requested_detail"
    USER_REQUESTED_LOOKUP = "user_requested_lookup"
    GOVERNED_REPORTING = "governed_reporting"
    GOVERNED_AGGREGATION = "governed_aggregation"
    OPERATIONAL_SUPPORT = "operational_support"
    COMPLIANCE_REVIEW = "compliance_review"
    UNSUPPORTED = "unsupported"


class AstraReadSensitivity(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class AstraReadDecisionStatus(StrEnum):
    AUTHORIZED_METADATA_ONLY = "authorized_metadata_only"
    CLARIFICATION_REQUIRED = "clarification_required"
    UNSUPPORTED = "unsupported"
    GOVERNANCE_BLOCKED = "governance_blocked"
    OWNER_ACCEPTANCE_REQUIRED = "owner_acceptance_required"
    SCOPE_DENIED = "scope_denied"
    MINIMIZATION_FAILED = "minimization_failed"
    DEFERRED = "deferred"
    REFUSED = "refused"
    INVALID = "invalid"


class AstraReadCheckResult(StrEnum):
    SATISFIED = "satisfied"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class AstraOwnerAcceptanceState(StrEnum):
    NOT_REQUESTED = "not_requested"
    REQUIRED = "required"
    PENDING = "pending"
    UNAVAILABLE = "unavailable"
    ACCEPTED = "accepted"


class AstraCrossAppPolicy(StrEnum):
    PROHIBITED = "prohibited"
    EXPLICIT_MULTI_OWNER_ACCEPTANCE = "explicit_multi_owner_acceptance"


class AstraReadCapabilityStatus(StrEnum):
    AVAILABLE = "available"
    DISABLED = "disabled"


class AstraReadHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AstraNamedReadCapability(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    read_capability_id: str = Field(pattern=r"^read_cap_[a-z0-9][a-z0-9_.-]{7,100}$")
    capability_name: str = Field(pattern=r"^[a-z][a-z0-9_]{2,80}$")
    owning_app_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,80}$")
    owning_module: str = Field(pattern=r"^[a-z][a-z0-9_.]{2,100}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: AstraReadCapabilityStatus
    description: str = Field(min_length=8, max_length=240)
    allowed_purposes: tuple[AstraReadPurpose, ...] = Field(min_length=1, max_length=8)
    sensitivity_classification: AstraReadSensitivity
    allowed_subject_scope: str = Field(pattern=r"^[a-z][a-z0-9_.:-]{2,80}$")
    allowed_tenant_scope: str = Field(pattern=r"^[a-z][a-z0-9_.:-]{2,80}$")
    allowed_record_scope: str = Field(pattern=r"^[a-z][a-z0-9_.:-]{2,80}$")
    allowed_field_references: tuple[str, ...] = Field(min_length=1, max_length=50)
    required_field_references: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    allowed_filter_references: tuple[str, ...] = Field(default_factory=tuple, max_length=30)
    allowed_aggregation_references: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    maximum_row_count: int = Field(ge=1, le=1000)
    maximum_time_range_days: int = Field(ge=1, le=3660)
    timeout_class: str = Field(pattern=r"^(short|standard|extended)$")
    cross_app_policy: AstraCrossAppPolicy = AstraCrossAppPolicy.PROHIBITED
    owner_service_acceptance_required: bool = True
    governance_requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(
        min_length=1, max_length=20
    )
    production_read_state: str = Field(default="not_approved", pattern=r"^not_approved$")

    @model_validator(mode="after")
    def validate_capability(self):
        for values, name in (
            (self.allowed_purposes, "purposes"),
            (self.allowed_field_references, "fields"),
            (self.required_field_references, "required fields"),
            (self.allowed_filter_references, "filters"),
            (self.allowed_aggregation_references, "aggregations"),
        ):
            if len(values) != len(set(values)):
                raise AstraReadAuthorizationError(f"Read capability {name} must be unique.")
        if not set(self.required_field_references).issubset(self.allowed_field_references):
            raise AstraReadAuthorizationError("Required fields must be allowed fields.")
        if AstraReadPurpose.UNSUPPORTED in self.allowed_purposes:
            raise AstraReadAuthorizationError("Unsupported purpose cannot authorize a read capability.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraAuthorityProof(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    proof_id: str = Field(pattern=r"^proof_[a-z0-9][a-z0-9_-]{7,120}$")
    proof_class: str = Field(pattern=r"^(principal|user|tenant|app|record|field|purpose|owner_acceptance)$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    issuer_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    subject_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    scope_references: tuple[str, ...] = Field(min_length=1, max_length=50)
    issued_at: datetime
    expires_at: datetime
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    @model_validator(mode="after")
    def validate_proof(self):
        _aware(self.issued_at)
        _aware(self.expires_at)
        if self.expires_at <= self.issued_at:
            raise AstraReadAuthorizationError("Authority proof expiration must follow issuance.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraAuthorityProofIssuer:
    """Bounded exact-object issuer for a future certified owning authority."""

    def __init__(self, *, runtime_instance_id: str, issuer_reference: str, capacity: int = 100) -> None:
        if capacity < 1 or capacity > 1000:
            raise AstraReadAuthorizationError("Proof issuer capacity is invalid.")
        self.runtime_instance_id = runtime_instance_id
        self.issuer_reference = issuer_reference
        self._capacity = capacity
        self._issued: dict[str, AstraAuthorityProof] = {}

    def issue(self, **values: Any) -> AstraAuthorityProof:
        if len(self._issued) >= self._capacity:
            raise AstraReadAuthorizationError("Proof issuer capacity reached.")
        proof = AstraAuthorityProof(
            runtime_instance_id=self.runtime_instance_id,
            issuer_reference=self.issuer_reference,
            **values,
        )
        if proof.proof_id in self._issued:
            raise AstraReadAuthorizationError("Duplicate proof identifier.")
        self._issued[proof.proof_id] = proof
        return proof

    def validates(self, proof: Any, *, observed_at: datetime) -> bool:
        return (
            isinstance(proof, AstraAuthorityProof)
            and proof.runtime_instance_id == self.runtime_instance_id
            and proof.issuer_reference == self.issuer_reference
            and proof.expires_at > observed_at
            and self._issued.get(proof.proof_id) is proof
        )


class AstraReadAuthorizationRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)
    authorization_request_id: str = Field(pattern=r"^read_req_[a-z0-9][a-z0-9_-]{7,120}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    current_turn_reference: str = Field(pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")
    intent_resolution_reference: str = Field(pattern=r"^intent_[a-f0-9]{24}$")
    plan_reference: str | None = Field(default=None, pattern=r"^plan_[a-f0-9]{24}$")
    read_capability_id: str
    authenticated_principal_reference: str
    requested_field_references: tuple[str, ...] = Field(min_length=1, max_length=50)
    requested_filter_references: tuple[str, ...] = Field(default_factory=tuple, max_length=30)
    requested_aggregation_references: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    requested_row_limit: int = Field(ge=1, le=1000)
    requested_time_range_days: int = Field(ge=1, le=3660)
    declared_purpose: AstraReadPurpose
    requester_authority_context: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    constitutional_requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(
        min_length=1, max_length=20
    )
    proofs: tuple[AstraAuthorityProof, ...] = Field(min_length=1, max_length=8, exclude=True)
    requested_at: datetime
    request_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode="after")
    def validate_request(self):
        _aware(self.requested_at)
        if len(self.requested_field_references) != len(set(self.requested_field_references)):
            raise AstraReadAuthorizationError("Requested fields must be unique.")
        if "*" in self.requested_field_references:
            raise AstraReadAuthorizationError("Wildcard fields are prohibited.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraReadAuthorizationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    authorization_decision_id: str
    authorization_request_id: str
    read_capability_id: str
    owning_app_id: str
    decision_status: AstraReadDecisionStatus
    governance_outcome: GovernanceOutcome
    purpose_result: AstraReadCheckResult
    principal_scope_result: AstraReadCheckResult
    tenant_scope_result: AstraReadCheckResult
    app_scope_result: AstraReadCheckResult
    record_scope_result: AstraReadCheckResult
    field_scope_result: AstraReadCheckResult
    minimization_result: AstraReadCheckResult
    row_limit_result: AstraReadCheckResult
    time_range_result: AstraReadCheckResult
    aggregation_result: AstraReadCheckResult
    cross_app_result: AstraReadCheckResult
    owner_acceptance_requirement: AstraOwnerAcceptanceState
    production_read_state: str = Field(default="not_approved", pattern=r"^not_approved$")
    evidence_references: tuple[str, ...]
    failure_posture: FailurePosture
    authorized_scope_summary: tuple[str, ...] = Field(max_length=50)
    database_connection_state: str = Field(default="not_authorized", pattern=r"^not_authorized$")
    sql_execution_state: str = Field(default="not_authorized", pattern=r"^not_authorized$")
    data_retrieval_state: str = Field(default="not_performed", pattern=r"^not_performed$")
    data_mutation_state: str = Field(default="prohibited", pattern=r"^prohibited$")
    schema_mutation_state: str = Field(default="prohibited", pattern=r"^prohibited$")
    issued_at: datetime
    version: str


class AstraReadAuthorizationHealth(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    runtime_instance_reference: str
    engine_registered: bool
    engine_available: bool
    configuration_valid: bool
    governance_available: bool
    evidence_sink_available: bool
    conversation_dependency_available: bool
    intent_dependency_available: bool
    planning_dependency_available: bool
    read_capability_registry_valid: bool
    principal_proof_issuer_available: bool
    tenant_proof_issuer_available: bool
    app_scope_issuer_available: bool
    owner_acceptance_issuer_available: bool
    last_successful_authorization_sequence: int | None
    health_outcome: AstraReadHealthOutcome
    observed_at: datetime


class AstraNamedReadCapabilityRegistry:
    def __init__(self, capabilities: tuple[AstraNamedReadCapability, ...] = ()) -> None:
        if len(capabilities) > MAX_READ_CAPABILITIES:
            raise AstraReadAuthorizationError("Read capability registry capacity exceeded.")
        items: dict[str, AstraNamedReadCapability] = {}
        for item in sorted(capabilities, key=lambda value: value.read_capability_id):
            if item.read_capability_id in items:
                raise AstraReadAuthorizationError("Duplicate read capability identifier.")
            items[item.read_capability_id] = item
        self._items: Mapping[str, AstraNamedReadCapability] = MappingProxyType(items)
        self._sealed = True

    @property
    def capabilities(self) -> tuple[AstraNamedReadCapability, ...]:
        return tuple(self._items.values())

    def get(self, capability_id: str) -> AstraNamedReadCapability:
        try:
            return self._items[capability_id]
        except KeyError as exc:
            raise AstraReadAuthorizationError("Unknown read capability identifier.") from exc

    @property
    def valid(self) -> bool:
        return self._sealed and len(self._items) <= MAX_READ_CAPABILITIES


class AstraReadAccessAuthorizationEngine:
    REQUIRED_PROOFS = ("principal", "user", "tenant", "app", "record", "field", "purpose")

    def __init__(self, *, runtime: Any, registry: AstraNamedReadCapabilityRegistry | None = None) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._registry = registry or AstraNamedReadCapabilityRegistry()
        self._issuers: dict[str, AstraAuthorityProofIssuer] = {}
        self._sequence = 0

    def bind_certified_issuer(self, proof_class: str, issuer: AstraAuthorityProofIssuer) -> None:
        self._require_ready()
        if proof_class not in (*self.REQUIRED_PROOFS, "owner_acceptance"):
            raise AstraReadAuthorizationError("Unknown proof issuer class.")
        if issuer.runtime_instance_id != self._runtime_instance_id:
            raise AstraReadAuthorizationError("Foreign-runtime proof issuer.")
        if proof_class in self._issuers:
            raise AstraReadAuthorizationError("Proof issuer already bound.")
        self._issuers[proof_class] = issuer

    def authorize(
        self,
        request: AstraReadAuthorizationRequest,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        intent_resolution: Any,
        plan: Any | None = None,
    ) -> AstraReadAuthorizationDecision:
        self._require_ready()
        if not isinstance(request, AstraReadAuthorizationRequest):
            raise AstraReadAuthorizationError("Validated read authorization request required.")
        if request.runtime_instance_id != self._runtime_instance_id:
            raise AstraReadAuthorizationError("Foreign-runtime authorization request.")
        self._validate_upstream(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=plan,
        )
        capability = self._registry.get(request.read_capability_id)
        proofs = {proof.proof_class: proof for proof in request.proofs}
        if len(proofs) != len(request.proofs):
            raise AstraReadAuthorizationError("Duplicate authority proof class.")
        for proof_class in self.REQUIRED_PROOFS:
            issuer = self._issuers.get(proof_class)
            proof = proofs.get(proof_class)
            if issuer is None or proof is None or not issuer.validates(proof, observed_at=request.requested_at):
                raise AstraReadAuthorizationError(f"Authoritative {proof_class} proof is unavailable or invalid.")
        self._validate_proof_scopes(request, capability, proofs)

        governance = self._runtime.evaluate_governance(
            GovernanceEvaluationInput(
                evaluation_id=f"READ-AUTH-GOV-{self._sequence + 1:03d}",
                requirement_references=request.constitutional_requirement_references,
                requested_authority_class=AuthorityClass.ADVISORY,
                safety_classification=SafetyClassification.SENSITIVE,
                approval_state=ApprovalState.REQUIRED,
                configuration_id=ASTRA_CONFIGURATION_ID,
                configuration_version=ASTRA_CONFIGURATION_VERSION,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                evaluation_timestamp=request.requested_at,
            )
        )
        self._runtime.append_evidence(governance.evidence)
        outcome = governance.decision.outcome
        status = _governance_status(outcome)
        checks = self._evaluate_scope(request, capability)
        if outcome is GovernanceOutcome.ALLOW:
            status = AstraReadDecisionStatus.OWNER_ACCEPTANCE_REQUIRED
            if AstraReadCheckResult.DENIED in checks:
                status = AstraReadDecisionStatus.MINIMIZATION_FAILED
            elif capability.owner_service_acceptance_required:
                owner_issuer = self._issuers.get("owner_acceptance")
                owner_proof = proofs.get("owner_acceptance")
                if (
                    owner_issuer
                    and owner_proof
                    and owner_issuer.validates(owner_proof, observed_at=request.requested_at)
                    and capability.read_capability_id in owner_proof.scope_references
                ):
                    status = AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY
        return self._release(request, capability, governance, status, checks)

    def _validate_proof_scopes(self, request, capability, proofs):
        required_scopes = {
            "principal": {request.authenticated_principal_reference},
            "user": {capability.allowed_subject_scope},
            "tenant": {capability.allowed_tenant_scope},
            "app": {capability.owning_app_id},
            "record": {capability.allowed_record_scope},
            "field": set(request.requested_field_references),
            "purpose": {request.declared_purpose.value},
        }
        for proof_class, expected in required_scopes.items():
            if not expected.issubset(proofs[proof_class].scope_references):
                raise AstraReadAuthorizationError(
                    f"Authoritative {proof_class} proof does not cover requested scope."
                )

    def _validate_upstream(self, request, *, conversation_engine, conversation_snapshot, intent_resolution, plan):
        from app.modules.astra_ai.conversation_context import (
            AstraConversationContextEngine,
            AstraConversationLifecycleState,
            AstraConversationSnapshot,
        )
        from app.modules.astra_ai.intent_resolution import AstraIntentResolution, AstraIntentStatus
        from app.modules.astra_ai.planning import AstraProposedPlan

        if not isinstance(conversation_engine, AstraConversationContextEngine) or not isinstance(
            conversation_snapshot, AstraConversationSnapshot
        ):
            raise AstraReadAuthorizationError("Certified conversation dependency required.")
        try:
            owned = conversation_engine.get_conversation(request.conversation_id)
        except Exception as exc:
            raise AstraReadAuthorizationError("Conversation is not owned by the supplied engine.") from exc
        if (
            owned != conversation_snapshot
            or owned.metadata.runtime_instance_id != self._runtime_instance_id
            or owned.metadata.lifecycle_state is not AstraConversationLifecycleState.ACTIVE
            or owned.current_turn is None
            or owned.current_turn.turn_id != request.current_turn_reference
        ):
            raise AstraReadAuthorizationError("Conversation ownership or current-turn freshness failed.")
        if (
            not isinstance(intent_resolution, AstraIntentResolution)
            or intent_resolution.runtime_instance_id != self._runtime_instance_id
            or intent_resolution.intent_id != request.intent_resolution_reference
            or intent_resolution.conversation_id != request.conversation_id
            or intent_resolution.current_turn_reference != request.current_turn_reference
            or intent_resolution.intent_status is not AstraIntentStatus.RESOLVED
        ):
            raise AstraReadAuthorizationError("Certified resolved intent reference required.")
        stored_evidence = {item.evidence_id for item in self._runtime.retrieve_evidence()}
        if not set(intent_resolution.evidence_references).issubset(stored_evidence):
            raise AstraReadAuthorizationError("Intent evidence references do not resolve.")
        if request.plan_reference is None:
            if plan is not None:
                raise AstraReadAuthorizationError("Unexpected planning object.")
        elif (
            not isinstance(plan, AstraProposedPlan)
            or plan.plan_id != request.plan_reference
            or plan.runtime_instance_id != self._runtime_instance_id
            or plan.conversation_id != request.conversation_id
            or not set(plan.evidence_references).issubset(stored_evidence)
        ):
            raise AstraReadAuthorizationError("Certified same-runtime plan reference required.")

    def health(self, *, observed_at: datetime | None = None) -> AstraReadAuthorizationHealth:
        timestamp = observed_at or datetime.now(timezone.utc)
        runtime_health = self._runtime.health(observed_at=timestamp)
        ready = getattr(self._runtime.state, "value", None) == "ready"
        issuer_ready = all(name in self._issuers for name in self.REQUIRED_PROOFS)
        all_ready = issuer_ready and "owner_acceptance" in self._issuers
        return AstraReadAuthorizationHealth(
            runtime_instance_reference=self._runtime_instance_id,
            engine_registered="read_access_authorization"
            in tuple(item.value for item in self._runtime.registered_component_identifiers),
            engine_available=ready,
            configuration_valid=runtime_health.configuration_valid,
            governance_available=runtime_health.governance_available,
            evidence_sink_available=runtime_health.evidence_sink_available,
            conversation_dependency_available=runtime_health.intent_resolution_available,
            intent_dependency_available=runtime_health.intent_resolution_available,
            planning_dependency_available=runtime_health.planning_available,
            read_capability_registry_valid=self._registry.valid,
            principal_proof_issuer_available="principal" in self._issuers,
            tenant_proof_issuer_available="tenant" in self._issuers,
            app_scope_issuer_available="app" in self._issuers,
            owner_acceptance_issuer_available="owner_acceptance" in self._issuers,
            last_successful_authorization_sequence=self._sequence or None,
            health_outcome=(
                AstraReadHealthOutcome.STOPPED
                if not ready
                else AstraReadHealthOutcome.HEALTHY
                if all_ready
                else AstraReadHealthOutcome.DEGRADED
            ),
            observed_at=timestamp,
        )

    def _evaluate_scope(self, request, capability):
        fields = set(request.requested_field_references)
        allowed = set(capability.allowed_field_references)
        required = set(capability.required_field_references)
        return (
            AstraReadCheckResult.SATISFIED
            if request.declared_purpose in capability.allowed_purposes
            else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED if fields.issubset(allowed) else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED if required.issubset(fields) else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED
            if request.requested_row_limit <= capability.maximum_row_count
            else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED
            if request.requested_time_range_days <= capability.maximum_time_range_days
            else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED
            if set(request.requested_aggregation_references).issubset(capability.allowed_aggregation_references)
            else AstraReadCheckResult.DENIED,
            AstraReadCheckResult.SATISFIED
            if capability.cross_app_policy is AstraCrossAppPolicy.PROHIBITED
            else AstraReadCheckResult.UNAVAILABLE,
        )

    def _release(self, request, capability, governance, status, checks):
        semantic = {
            "request": request.model_dump(mode="json", exclude={"proofs", "requested_at"}),
            "capability": capability.model_dump(mode="json"),
            "status": status.value,
            "governance": governance.decision.outcome.value,
            "checks": tuple(item.value for item in checks),
        }
        digest = hashlib.sha256(_canonical(semantic).encode()).hexdigest()
        decision_id = f"read_auth_{digest[:24]}"
        next_sequence = self._sequence + 1
        evidence_id = f"evd_read_auth_{hashlib.sha256(f'{decision_id}:{next_sequence}'.encode()).hexdigest()[:20]}"
        evidence = BoundedEvidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.GOVERNANCE_DECISION,
            requirement_references=request.constitutional_requirement_references,
            actor_or_service_class=ActorOrServiceClass.COMPONENT,
            decision_or_operation_reference=decision_id,
            timestamp=request.requested_at,
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=EvidenceIntegrityMetadata(
                source_system="astra_ai:read_access_authorization",
                provenance_reference=f"ASTRA-IMP-010:{READ_ACCESS_AUTHORIZATION_VERSION}",
                content_digest=f"sha256:{digest}",
            ),
            correction=EvidenceCorrectionMetadata(evidence_version=READ_ACCESS_AUTHORIZATION_VERSION),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )
        self._runtime.append_evidence(evidence)
        purpose, fields, required, rows, time_range, aggregation, cross_app = checks
        decision = AstraReadAuthorizationDecision(
            authorization_decision_id=decision_id,
            authorization_request_id=request.authorization_request_id,
            read_capability_id=capability.read_capability_id,
            owning_app_id=capability.owning_app_id,
            decision_status=status,
            governance_outcome=governance.decision.outcome,
            purpose_result=purpose,
            principal_scope_result=AstraReadCheckResult.SATISFIED,
            tenant_scope_result=AstraReadCheckResult.SATISFIED,
            app_scope_result=AstraReadCheckResult.SATISFIED,
            record_scope_result=AstraReadCheckResult.SATISFIED,
            field_scope_result=fields,
            minimization_result=required,
            row_limit_result=rows,
            time_range_result=time_range,
            aggregation_result=aggregation,
            cross_app_result=cross_app,
            owner_acceptance_requirement=(
                AstraOwnerAcceptanceState.ACCEPTED
                if status is AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY
                else AstraOwnerAcceptanceState.REQUIRED
            ),
            evidence_references=(governance.evidence.evidence_id, evidence_id),
            failure_posture=governance.decision.failure_posture,
            authorized_scope_summary=tuple(sorted(request.requested_field_references)),
            issued_at=request.requested_at,
            version=READ_ACCESS_AUTHORIZATION_VERSION,
        )
        self._sequence = next_sequence
        return decision

    def _require_ready(self):
        if getattr(self._runtime.state, "value", None) != "ready":
            raise AstraReadAuthorizationError("Read authorization requires ready Runtime.")


def _governance_status(outcome: GovernanceOutcome) -> AstraReadDecisionStatus:
    return {
        GovernanceOutcome.ALLOW: AstraReadDecisionStatus.OWNER_ACCEPTANCE_REQUIRED,
        GovernanceOutcome.CLARIFY: AstraReadDecisionStatus.CLARIFICATION_REQUIRED,
        GovernanceOutcome.DEFER: AstraReadDecisionStatus.DEFERRED,
        GovernanceOutcome.REFUSE: AstraReadDecisionStatus.REFUSED,
        GovernanceOutcome.CONTAIN: AstraReadDecisionStatus.GOVERNANCE_BLOCKED,
        GovernanceOutcome.FAIL_CLOSED: AstraReadDecisionStatus.INVALID,
    }[outcome]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraReadAuthorizationError("Timestamp must be timezone-aware.")
