from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


IDENTIFIER_PATTERN = r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$"
REQUIREMENT_ID_PATTERN = r"^[A-Z]{2,5}-[A-Z]{2,5}-\d{3}$"
VERSION_PATTERN = r"^\d+\.\d+\.\d+$"
EVIDENCE_ID_PATTERN = r"^evd_[a-z0-9][a-z0-9_-]{7,120}$"
REFERENCE_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$"
COMPONENT_PATTERN = r"^[A-Za-z][A-Za-z0-9 _:/-]{2,120}$"


SECRET_PATTERNS = (
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"(api[_-]?key|token|password|secret|credential)\s*[:=]", re.IGNORECASE),
    re.compile(r"(postgres(?:ql)?|mysql|libsql)://", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bhidden[_ -]?reasoning\b", re.IGNORECASE),
    re.compile(r"\braw[_ -]?prompt\b", re.IGNORECASE),
    re.compile(r"\bfull[_ -]?private[_ -]?payload\b", re.IGNORECASE),
    re.compile(r"\bunrelated[_ -]?user[_ -]?data\b", re.IGNORECASE),
)


class ContractValidationError(ValueError):
    """Raised when a Stage 0 Astra constitutional contract violates governance."""


class ConstitutionalCoverageState(StrEnum):
    MAPPED = "mapped"
    DEFERRED = "deferred"
    NOT_APPLICABLE = "not_applicable"
    AMENDMENT_REQUIRED = "amendment_required"


class GovernanceOutcome(StrEnum):
    ALLOW = "allow"
    CLARIFY = "clarify"
    REFUSE = "refuse"
    DEFER = "defer"
    CONTAIN = "contain"
    FAIL_CLOSED = "fail_closed"


class SafetyClassification(StrEnum):
    PUBLIC = "public"
    PRIVATE_READ = "private_read"
    PRIVATE_WRITE = "private_write"
    HIGH_IMPACT = "high_impact"
    CROSS_OWNER = "cross_owner"
    EXTERNAL_EXPOSURE = "external_exposure"
    CONSTITUTIONAL = "constitutional"
    PROHIBITED = "prohibited"
    UNKNOWN = "unknown"


class AuthorityClass(StrEnum):
    ADVISORY = "advisory"
    READ_ONLY = "read_only"
    APPROVAL_REQUIRED = "approval_required"
    EXECUTION_BOUNDARY = "execution_boundary"
    PRODUCTION_BOUNDARY = "production_boundary"
    CONSTITUTIONAL = "constitutional"


class DecisionReasonClass(StrEnum):
    LOCAL_SUFFICIENCY = "local_sufficiency"
    CONTEXT_MINIMIZATION = "context_minimization"
    PLAN_VERSION_BOUNDARY = "plan_version_boundary"
    EXECUTION_AUTHORITY_BOUNDARY = "execution_authority_boundary"
    PROVIDER_ELIGIBILITY = "provider_eligibility"
    PROVIDER_ADVISORY_RESPONSE = "provider_advisory_response"
    MEMORY_OWNERSHIP = "memory_ownership"
    MEMORY_RETRIEVAL_AUTHORIZATION = "memory_retrieval_authorization"
    ADAPTATION_ACTIVATION = "adaptation_activation"
    CONSTITUTIONAL_PRECEDENCE = "constitutional_precedence"
    AUDIT_INTEGRITY = "audit_integrity"
    FAIL_CLOSED_DEFAULT = "fail_closed_default"


class ApprovalState(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class FailurePosture(StrEnum):
    FAIL_CLOSED = "fail_closed"
    REFUSE = "refuse"
    CLARIFY = "clarify"
    DEFER = "defer"
    CONTAIN = "contain"
    NO_OP = "no_op"


class EvidenceType(StrEnum):
    CONTRACT_VALIDATION = "contract_validation"
    GOVERNANCE_DECISION = "governance_decision"
    CONTEXT_MINIMIZATION = "context_minimization"
    CONFIGURATION_VALIDATION = "configuration_validation"
    PROVIDER_BOUNDARY = "provider_boundary"
    MEMORY_BOUNDARY = "memory_boundary"
    ADAPTATION_BOUNDARY = "adaptation_boundary"
    AUDIT_INTEGRITY = "audit_integrity"


class ActorOrServiceClass(StrEnum):
    USER = "user"
    SERVICE = "service"
    COMPONENT = "component"
    SYSTEM = "system"
    PRODUCT_OWNER = "product_owner"
    ASTRA_REVIEW = "astra_review"
    CODEX = "codex"


class SensitivityClass(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class MinimizationClass(StrEnum):
    METADATA_ONLY = "metadata_only"
    REDACTED_REFERENCE = "redacted_reference"
    SUMMARY_ONLY = "summary_only"
    NO_PAYLOAD = "no_payload"


class RetentionClass(StrEnum):
    TRANSIENT = "transient"
    SHORT_TERM = "short_term"
    GOVERNANCE_RECORD = "governance_record"
    LEGAL_HOLD = "legal_hold"
    DELETE_ELIGIBLE = "delete_eligible"


class CorrectionPrivacyTreatment(StrEnum):
    METADATA_ONLY = "metadata_only"
    REDACTED_REFERENCE = "redacted_reference"
    PRIVACY_MINIMIZED = "privacy_minimized"
    DELETE_ELIGIBLE = "delete_eligible"


class RedactionStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REDACTED = "redacted"
    REFERENCE_ONLY = "reference_only"


class EnvironmentScope(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    QA = "qa"
    STAGING = "staging"
    PRODUCTION = "production"


class ImplementationPhase(StrEnum):
    ASTRA_IMP_001 = "astra_imp_001"


class ProductionAuthorizationState(StrEnum):
    NOT_REQUESTED = "not_requested"
    NOT_APPROVED = "not_approved"
    APPROVED = "approved"


class RuntimeUseState(StrEnum):
    DISABLED = "disabled"


class AuditEvidenceBehavior(StrEnum):
    METADATA_ONLY = "metadata_only"
    DISABLED = "disabled"


class ConstitutionalRequirementReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constitutional_source: str = Field(pattern=r"^ASTRA-(?:00[1-9]|010|IR-001)$")
    requirement_id: str = Field(pattern=REQUIREMENT_ID_PATTERN)
    requirement_version: str = Field(default="1.0.0", pattern=VERSION_PATTERN)


class ConstitutionalRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constitutional_source: str = Field(pattern=r"^ASTRA-(?:00[1-9]|010|IR-001)$")
    requirement_id: str = Field(pattern=REQUIREMENT_ID_PATTERN)
    requirement_version: str = Field(pattern=VERSION_PATTERN)
    requirement_summary: str = Field(min_length=8, max_length=280)
    accountable_component: str = Field(pattern=COMPONENT_PATTERN)
    coverage_state: ConstitutionalCoverageState

    def reference(self) -> ConstitutionalRequirementReference:
        return ConstitutionalRequirementReference(
            constitutional_source=self.constitutional_source,
            requirement_id=self.requirement_id,
            requirement_version=self.requirement_version,
        )


class GovernanceDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str = Field(pattern=IDENTIFIER_PATTERN)
    outcome: GovernanceOutcome
    requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(min_length=1, max_length=20)
    safety_classification: SafetyClassification
    authority_class: AuthorityClass
    decision_reason_class: DecisionReasonClass
    required_approval_state: ApprovalState
    evidence_references: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    failure_posture: FailurePosture
    version_marker: str = Field(pattern=VERSION_PATTERN)

    @field_validator("evidence_references")
    @classmethod
    def validate_evidence_references(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            if not re.fullmatch(EVIDENCE_ID_PATTERN, value):
                raise ContractValidationError("Evidence references must use stable evidence identifiers.")
        return values

    @model_validator(mode="after")
    def validate_authorization_consistency(self) -> Self:
        if self.outcome is GovernanceOutcome.ALLOW and self.required_approval_state in {
            ApprovalState.REQUIRED,
            ApprovalState.PENDING,
            ApprovalState.DENIED,
        }:
            raise ContractValidationError("Allow decisions cannot bypass required, pending, or denied approval.")
        if self.outcome is GovernanceOutcome.FAIL_CLOSED and self.failure_posture is not FailurePosture.FAIL_CLOSED:
            raise ContractValidationError("Fail-closed decisions must carry a fail-closed posture.")
        if self.safety_classification is SafetyClassification.PROHIBITED and self.outcome is GovernanceOutcome.ALLOW:
            raise ContractValidationError("Prohibited safety classifications cannot be allowed.")
        if self.safety_classification is SafetyClassification.UNKNOWN and self.outcome is GovernanceOutcome.ALLOW:
            raise ContractValidationError("Unknown safety classifications cannot be allowed.")
        if (
            self.safety_classification in {SafetyClassification.PRIVATE_WRITE, SafetyClassification.HIGH_IMPACT}
            and self.outcome is GovernanceOutcome.ALLOW
            and self.required_approval_state is not ApprovalState.APPROVED
        ):
            raise ContractValidationError("Private-write and high-impact allow decisions require explicit approval.")
        if (
            self.authority_class is AuthorityClass.PRODUCTION_BOUNDARY
            and self.required_approval_state is not ApprovalState.APPROVED
            and self.outcome is GovernanceOutcome.ALLOW
        ):
            raise ContractValidationError("Production boundary allow decisions require explicit approval.")
        return self


class EvidenceIntegrityMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_system: str = Field(pattern=REFERENCE_PATTERN)
    provenance_reference: str = Field(pattern=REFERENCE_PATTERN)
    content_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    signature_reference: str | None = Field(default=None, pattern=REFERENCE_PATTERN)

    @model_validator(mode="after")
    def validate_safe_metadata(self) -> Self:
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class EvidenceCorrectionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_version: str = Field(pattern=VERSION_PATTERN)
    supersedes_evidence_id: str | None = Field(default=None, pattern=EVIDENCE_ID_PATTERN)
    correction_reason: str | None = Field(default=None, max_length=240)
    correcting_actor_or_service_class: ActorOrServiceClass | None = None
    correction_timestamp: datetime | None = None
    replacement_reference: str | None = Field(default=None, pattern=REFERENCE_PATTERN)
    retention_treatment: RetentionClass | None = None
    privacy_treatment: CorrectionPrivacyTreatment | None = None

    @model_validator(mode="after")
    def validate_correction_reference(self) -> Self:
        correction_fields = (
            self.correction_reason,
            self.correcting_actor_or_service_class,
            self.correction_timestamp,
            self.replacement_reference,
            self.retention_treatment,
            self.privacy_treatment,
        )
        has_correction_metadata = any(value is not None for value in correction_fields)
        if self.supersedes_evidence_id is None and has_correction_metadata:
            raise ContractValidationError("Evidence correction metadata requires a superseded evidence identifier.")
        if self.supersedes_evidence_id is not None:
            if any(value is None for value in correction_fields):
                raise ContractValidationError("Evidence correction requires reason, authority, timestamp, replacement, retention, and privacy metadata.")
            if self.correction_timestamp is None or self.correction_timestamp.tzinfo is None or self.correction_timestamp.utcoffset() is None:
                raise ContractValidationError("Evidence correction timestamps must be timezone-aware.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class BoundedEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(pattern=EVIDENCE_ID_PATTERN)
    evidence_type: EvidenceType
    requirement_references: tuple[ConstitutionalRequirementReference, ...] = Field(min_length=1, max_length=20)
    actor_or_service_class: ActorOrServiceClass
    decision_or_operation_reference: str = Field(pattern=REFERENCE_PATTERN)
    timestamp: datetime
    sensitivity_class: SensitivityClass
    minimization_class: MinimizationClass
    retention_class: RetentionClass
    integrity: EvidenceIntegrityMetadata
    correction: EvidenceCorrectionMetadata
    redaction_status: RedactionStatus

    @model_validator(mode="after")
    def validate_evidence_minimization(self) -> Self:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ContractValidationError("Evidence timestamps must be timezone-aware.")
        if (
            self.sensitivity_class is SensitivityClass.RESTRICTED
            and self.minimization_class is not MinimizationClass.NO_PAYLOAD
            and self.redaction_status is not RedactionStatus.REDACTED
        ):
            raise ContractValidationError("Restricted evidence must be redacted or carry no payload.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraConfigurationContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    configuration_id: str = Field(pattern=IDENTIFIER_PATTERN)
    feature_enabled: bool = False
    environment_scope: EnvironmentScope
    implementation_phase: ImplementationPhase = ImplementationPhase.ASTRA_IMP_001
    production_authorization_state: ProductionAuthorizationState = ProductionAuthorizationState.NOT_APPROVED
    provider_use: RuntimeUseState = RuntimeUseState.DISABLED
    memory_use: RuntimeUseState = RuntimeUseState.DISABLED
    adaptation_use: RuntimeUseState = RuntimeUseState.DISABLED
    execution_handoff: RuntimeUseState = RuntimeUseState.DISABLED
    audit_evidence_behavior: AuditEvidenceBehavior = AuditEvidenceBehavior.METADATA_ONLY
    fail_closed_default: bool = True
    configuration_version: str = Field(pattern=VERSION_PATTERN)

    @model_validator(mode="after")
    def validate_stage_zero_configuration(self) -> Self:
        if self.feature_enabled:
            raise ContractValidationError("ASTRA-IMP-001 configuration must remain disabled by default.")
        if self.production_authorization_state is ProductionAuthorizationState.APPROVED:
            raise ContractValidationError("ASTRA-IMP-001 cannot record production authorization.")
        if not self.fail_closed_default:
            raise ContractValidationError("ASTRA-IMP-001 configuration must fail closed by default.")
        if self.environment_scope is EnvironmentScope.PRODUCTION and self.production_authorization_state is not (
            ProductionAuthorizationState.NOT_APPROVED
        ):
            raise ContractValidationError("Production scope requires an explicit not-approved state in Stage 0.")
        return self


def canonical_contract_json(contract: BaseModel) -> str:
    return json.dumps(
        contract.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )


def utc_now_for_evidence() -> datetime:
    return datetime.now(timezone.utc)


def assert_no_prohibited_contract_material(value: Any) -> None:
    payload = json.dumps(value, default=str, sort_keys=True)
    for pattern in SECRET_PATTERNS:
        if pattern.search(payload):
            raise ContractValidationError("Contract contains prohibited secret, prompt, reasoning, or private payload material.")
