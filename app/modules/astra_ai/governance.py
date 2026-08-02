from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import IntEnum, StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.activation import (
    AstraRuntimeActivationContract,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
)
from app.modules.astra_ai.configuration import get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    ApprovalState,
    AuthorityClass,
    BoundedEvidence,
    ConstitutionalRequirementReference,
    DecisionReasonClass,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    FailurePosture,
    GovernanceDecision,
    GovernanceOutcome,
    MinimizationClass,
    ProductionAuthorizationState,
    RedactionStatus,
    RetentionClass,
    RuntimeUseState,
    SafetyClassification,
    SensitivityClass,
    assert_no_prohibited_contract_material,
    canonical_contract_json,
)


GOVERNANCE_KERNEL_VERSION = "1.0.0"


class ConstitutionalComplianceState(StrEnum):
    KNOWN_COMPLIANT = "known_compliant"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


class ConsentState(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"


class OwnerAuthorityStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DENIED = "denied"
    CONFLICT = "conflict"


class PrecedenceLevel(IntEnum):
    BINDING_CONSTRAINT = 1
    ACCEPTED_CONSTITUTION = 2
    PRODUCT_OWNER_GOVERNANCE = 3
    OWNING_SERVICE_TRUTH = 4
    SUBORDINATE_ARCHITECTURE = 5
    APPROVED_RUNTIME_POLICY = 6
    USER_INTENT = 7
    PROVIDER_OUTPUT_OR_INFERENCE = 8


class PolicyFactValue(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    UNKNOWN = "unknown"


class GovernancePolicyFact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    precedence_level: PrecedenceLevel
    fact_value: PolicyFactValue
    fact_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    summary: str = Field(min_length=4, max_length=180)

    @model_validator(mode="after")
    def validate_bounded_fact(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class GovernanceEvaluationInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    evaluation_id: str = Field(pattern=r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
    requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(min_length=1, max_length=20)
    requested_authority_class: AuthorityClass
    safety_classification: SafetyClassification
    approval_state: ApprovalState
    runtime_instance_id: str | None = Field(default=None, pattern=r"^astra_rt_[a-f0-9]{32}$")
    requested_app_id: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{2,80}$")
    requested_capability_scope: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{2,120}$")
    consent_state: ConsentState = ConsentState.NOT_REQUIRED
    configuration_id: str = Field(pattern=r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
    configuration_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    owner_authority_status: OwnerAuthorityStatus = OwnerAuthorityStatus.NOT_APPLICABLE
    policy_facts: tuple[GovernancePolicyFact, ...] = Field(default_factory=tuple, max_length=12)
    requested_failure_posture: FailurePosture = FailurePosture.FAIL_CLOSED
    constitutional_compliance: ConstitutionalComplianceState = ConstitutionalComplianceState.KNOWN_COMPLIANT
    production_authorization_state: ProductionAuthorizationState = ProductionAuthorizationState.NOT_APPROVED
    provider_use_requested: bool = False
    memory_use_requested: bool = False
    adaptation_use_requested: bool = False
    execution_handoff_requested: bool = False
    activation_context: AstraRuntimeActivationContract | None = Field(default=None, exclude=True)
    evaluation_timestamp: datetime
    evaluation_version: str = Field(default=GOVERNANCE_KERNEL_VERSION, pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode="after")
    def validate_bounded_input(self):
        if self.evaluation_timestamp.tzinfo is None or self.evaluation_timestamp.utcoffset() is None:
            raise ValueError("Governance evaluation timestamp must be timezone-aware.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class GovernanceEvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision: GovernanceDecision
    evidence: BoundedEvidence


class _PrecedenceResolution(StrEnum):
    NO_APPLICABLE_FACT = "no_applicable_fact"
    ALLOW = "allow"
    BLOCK = "block"
    UNRESOLVED = "unresolved"


def evaluate_governance(input_contract: GovernanceEvaluationInput) -> GovernanceEvaluationResult:
    loaded_configuration = get_astra_configuration()
    configuration = loaded_configuration.configuration
    outcome, reason_class, failure_posture = _evaluate_outcome(input_contract, configuration)
    decision = GovernanceDecision(
        decision_id=input_contract.evaluation_id,
        outcome=outcome,
        requirement_references=input_contract.requirement_references,
        safety_classification=input_contract.safety_classification,
        authority_class=input_contract.requested_authority_class,
        decision_reason_class=reason_class,
        required_approval_state=input_contract.approval_state,
        evidence_references=(_evidence_id(input_contract),),
        failure_posture=failure_posture,
        version_marker=input_contract.evaluation_version,
    )
    evidence = _build_decision_evidence(input_contract, decision, loaded_configuration.provenance.environment_scope)
    return GovernanceEvaluationResult(decision=decision, evidence=evidence)


def _evaluate_outcome(input_contract, configuration) -> tuple[GovernanceOutcome, DecisionReasonClass, FailurePosture]:
    if not configuration.fail_closed_default:
        return _fail_closed(DecisionReasonClass.FAIL_CLOSED_DEFAULT)
    if (
        input_contract.configuration_id != configuration.configuration_id
        or input_contract.configuration_version != configuration.configuration_version
    ):
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.constitutional_compliance is not ConstitutionalComplianceState.KNOWN_COMPLIANT:
        return _fail_closed(DecisionReasonClass.FAIL_CLOSED_DEFAULT)
    if input_contract.safety_classification in {SafetyClassification.UNKNOWN, SafetyClassification.PROHIBITED}:
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.approval_state in {ApprovalState.REQUIRED, ApprovalState.PENDING, ApprovalState.DENIED}:
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.consent_state in {ConsentState.REQUIRED, ConsentState.PENDING, ConsentState.DENIED}:
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.owner_authority_status in {
        OwnerAuthorityStatus.UNVERIFIED,
        OwnerAuthorityStatus.DENIED,
        OwnerAuthorityStatus.CONFLICT,
    }:
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.requested_authority_class is AuthorityClass.PRODUCTION_BOUNDARY:
        if input_contract.production_authorization_state is not ProductionAuthorizationState.APPROVED:
            return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.safety_classification in {SafetyClassification.PRIVATE_WRITE, SafetyClassification.HIGH_IMPACT}:
        if input_contract.approval_state is not ApprovalState.APPROVED:
            return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if _runtime_use_requested(input_contract) or _configuration_runtime_enabled(configuration):
        return _fail_closed(_runtime_reason(input_contract))
    precedence_resolution = _resolve_precedence(input_contract.policy_facts)
    if precedence_resolution in {_PrecedenceResolution.BLOCK, _PrecedenceResolution.UNRESOLVED}:
        return _fail_closed(DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)
    if input_contract.requested_authority_class in {AuthorityClass.EXECUTION_BOUNDARY, AuthorityClass.PRODUCTION_BOUNDARY}:
        return _fail_closed(DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY)
    if input_contract.safety_classification is SafetyClassification.EXTERNAL_EXPOSURE:
        return _non_allow(GovernanceOutcome.DEFER, DecisionReasonClass.PROVIDER_ELIGIBILITY, FailurePosture.DEFER)
    if not configuration.feature_enabled and not _activation_covers(input_contract):
        return _fail_closed(DecisionReasonClass.FAIL_CLOSED_DEFAULT)
    if input_contract.requested_authority_class in {AuthorityClass.READ_ONLY, AuthorityClass.ADVISORY}:
        if input_contract.safety_classification in {SafetyClassification.PUBLIC, SafetyClassification.PRIVATE_READ}:
            return GovernanceOutcome.ALLOW, DecisionReasonClass.LOCAL_SUFFICIENCY, input_contract.requested_failure_posture
    return _non_allow(GovernanceOutcome.CLARIFY, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE, FailurePosture.CLARIFY)


def _activation_covers(input_contract: GovernanceEvaluationInput) -> bool:
    activation = input_contract.activation_context
    if activation is None:
        return False
    if input_contract.requested_capability_scope != SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE:
        return False
    return activation.covers(
        runtime_instance_id=input_contract.runtime_instance_id,
        authority_class=input_contract.requested_authority_class,
        safety_classification=input_contract.safety_classification,
        app_id=input_contract.requested_app_id,
        capability_scope=input_contract.requested_capability_scope,
        production_authorization_state=input_contract.production_authorization_state,
        provider_requested=input_contract.provider_use_requested,
        memory_requested=input_contract.memory_use_requested,
        adaptation_requested=input_contract.adaptation_use_requested,
        execution_handoff_requested=input_contract.execution_handoff_requested,
        observed_at=input_contract.evaluation_timestamp,
    )


def _fail_closed(reason_class: DecisionReasonClass) -> tuple[GovernanceOutcome, DecisionReasonClass, FailurePosture]:
    return GovernanceOutcome.FAIL_CLOSED, reason_class, FailurePosture.FAIL_CLOSED


def _non_allow(
    outcome: GovernanceOutcome,
    reason_class: DecisionReasonClass,
    failure_posture: FailurePosture,
) -> tuple[GovernanceOutcome, DecisionReasonClass, FailurePosture]:
    return outcome, reason_class, failure_posture


def _runtime_use_requested(input_contract: GovernanceEvaluationInput) -> bool:
    return any(
        (
            input_contract.provider_use_requested,
            input_contract.memory_use_requested,
            input_contract.adaptation_use_requested,
            input_contract.execution_handoff_requested,
        )
    )


def _configuration_runtime_enabled(configuration) -> bool:
    return any(
        (
            configuration.provider_use is not RuntimeUseState.DISABLED,
            configuration.memory_use is not RuntimeUseState.DISABLED,
            configuration.adaptation_use is not RuntimeUseState.DISABLED,
            configuration.execution_handoff is not RuntimeUseState.DISABLED,
        )
    )


def _runtime_reason(input_contract: GovernanceEvaluationInput) -> DecisionReasonClass:
    if input_contract.provider_use_requested:
        return DecisionReasonClass.PROVIDER_ELIGIBILITY
    if input_contract.memory_use_requested:
        return DecisionReasonClass.MEMORY_RETRIEVAL_AUTHORIZATION
    if input_contract.adaptation_use_requested:
        return DecisionReasonClass.ADAPTATION_ACTIVATION
    return DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY


def _resolve_precedence(facts: tuple[GovernancePolicyFact, ...]) -> _PrecedenceResolution:
    if not facts:
        return _PrecedenceResolution.NO_APPLICABLE_FACT

    highest_level = min(fact.precedence_level for fact in facts)
    decisive_values = {fact.fact_value for fact in facts if fact.precedence_level == highest_level}
    if PolicyFactValue.UNKNOWN in decisive_values:
        return _PrecedenceResolution.UNRESOLVED
    if PolicyFactValue.ALLOW in decisive_values and PolicyFactValue.BLOCK in decisive_values:
        return _PrecedenceResolution.UNRESOLVED
    if PolicyFactValue.BLOCK in decisive_values:
        return _PrecedenceResolution.BLOCK
    if PolicyFactValue.ALLOW in decisive_values:
        return _PrecedenceResolution.ALLOW
    return _PrecedenceResolution.NO_APPLICABLE_FACT


def _build_decision_evidence(
    input_contract: GovernanceEvaluationInput,
    decision: GovernanceDecision,
    environment_scope,
) -> BoundedEvidence:
    payload_digest = hashlib.sha256(
        (
            _canonical_governance_input_json(input_contract)
            + canonical_contract_json(decision)
            + str(environment_scope)
        ).encode("utf-8")
    ).hexdigest()
    return BoundedEvidence(
        evidence_id=_evidence_id(input_contract),
        evidence_type=EvidenceType.GOVERNANCE_DECISION,
        requirement_references=input_contract.requirement_references,
        actor_or_service_class=ActorOrServiceClass.SERVICE,
        decision_or_operation_reference=decision.decision_id,
        timestamp=input_contract.evaluation_timestamp,
        sensitivity_class=SensitivityClass.INTERNAL,
        minimization_class=MinimizationClass.METADATA_ONLY,
        retention_class=RetentionClass.GOVERNANCE_RECORD,
        integrity=EvidenceIntegrityMetadata(
            source_system="astra_ai:governance",
            provenance_reference=f"{input_contract.configuration_id}:{input_contract.configuration_version}",
            content_digest=f"sha256:{payload_digest}",
        ),
        correction=EvidenceCorrectionMetadata(evidence_version=GOVERNANCE_KERNEL_VERSION),
        redaction_status=RedactionStatus.NOT_REQUIRED,
    )


def _evidence_id(input_contract: GovernanceEvaluationInput) -> str:
    digest = hashlib.sha256(
        f"{input_contract.evaluation_id}:{input_contract.evaluation_version}".encode("utf-8")
    ).hexdigest()[:24]
    return f"evd_gov_{digest}"


def _canonical_governance_input_json(input_contract: GovernanceEvaluationInput) -> str:
    payload = input_contract.model_dump(mode="json")
    payload["policy_facts"] = sorted(
        payload["policy_facts"],
        key=lambda fact: (
            fact["precedence_level"],
            fact["fact_value"],
            fact["fact_reference"],
            fact["summary"],
        ),
    )
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
