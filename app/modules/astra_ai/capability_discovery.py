from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION
from app.modules.astra_ai.constitutional_contracts import (
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    GovernanceOutcome,
    ProductionAuthorizationState,
    SafetyClassification,
    assert_no_prohibited_contract_material,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput


CAPABILITY_DISCOVERY_ENGINE_VERSION = "1.0.0"
CAPABILITY_DISCOVERY_IMPLEMENTATION_REFERENCE = "ASTRA-IMP-007"


class AstraCapabilityDiscoveryError(ValueError):
    """Raised when capability discovery violates its metadata-only contract."""


class AstraCapabilityType(StrEnum):
    PLATFORM_METADATA = "platform_metadata"
    CONVERSATION_CONTEXT = "conversation_context"
    GOVERNANCE_METADATA = "governance_metadata"
    EVIDENCE_METADATA = "evidence_metadata"


class AstraCapabilityStatus(StrEnum):
    AVAILABLE = "available"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class AstraCapabilityVisibility(StrEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    INTERNAL = "internal"


class AstraCapabilityExecutionAuthority(StrEnum):
    NONE = "none"
    METADATA_ONLY = "metadata_only"
    OWNER_SERVICE_REQUIRED = "owner_service_required"


class AstraCapabilityHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AstraCapabilityMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str = Field(pattern=r"^cap_[a-z0-9][a-z0-9_-]{7,120}$")
    capability_name: str = Field(min_length=4, max_length=120)
    capability_type: AstraCapabilityType
    owning_module: str = Field(pattern=r"^[a-z][a-z0-9_.:-]{2,160}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: AstraCapabilityStatus
    visibility: AstraCapabilityVisibility
    governance_reference: ConstitutionalRequirementReference
    execution_authority: AstraCapabilityExecutionAuthority
    description: str = Field(min_length=12, max_length=240)

    @model_validator(mode="after")
    def validate_capability_metadata(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraCapabilityDiscoveryResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    discovered_at: datetime
    capabilities: tuple[AstraCapabilityMetadata, ...] = Field(default_factory=tuple, max_length=200)
    governance_outcome: GovernanceOutcome
    evidence_reference: str = Field(pattern=r"^evd_[a-z0-9][a-z0-9_-]{7,120}$")
    discovery_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode="after")
    def validate_discovery_result(self):
        _ensure_timezone_aware(self.discovered_at, "Capability discovery timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraCapabilityHealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    registry_loaded: bool
    capability_count: int = Field(ge=0)
    duplicate_free: bool
    registry_valid: bool
    health_outcome: AstraCapabilityHealthOutcome
    observed_at: datetime

    @model_validator(mode="after")
    def validate_health_snapshot(self):
        _ensure_timezone_aware(self.observed_at, "Capability health timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraCapabilityRegistry:
    def __init__(self, capabilities: tuple[AstraCapabilityMetadata, ...] = ()) -> None:
        self._capabilities: dict[str, AstraCapabilityMetadata] = {}
        for capability in sorted(capabilities, key=lambda item: item.capability_id):
            self._register(capability)
        self._sealed = True

    def get(self, capability_id: str) -> AstraCapabilityMetadata:
        try:
            return deepcopy(self._capabilities[capability_id])
        except KeyError as exc:
            raise AstraCapabilityDiscoveryError("Unknown capability identifier.") from exc

    def discover(
        self,
        *,
        visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
    ) -> tuple[AstraCapabilityMetadata, ...]:
        capabilities = []
        for capability in self._capabilities.values():
            if visibility is not None and capability.visibility is not visibility:
                continue
            if not include_disabled and capability.status is AstraCapabilityStatus.DISABLED:
                continue
            if not include_deprecated and capability.status is AstraCapabilityStatus.DEPRECATED:
                continue
            capabilities.append(capability)
        return tuple(deepcopy(sorted(capabilities, key=lambda item: item.capability_id)))

    @property
    def capability_count(self) -> int:
        return len(self._capabilities)

    @property
    def duplicate_free(self) -> bool:
        return len(self._capabilities) == len(set(self._capabilities))

    @property
    def is_valid(self) -> bool:
        return self._sealed and self.duplicate_free

    def _register(self, capability: AstraCapabilityMetadata) -> None:
        if capability.capability_id in self._capabilities:
            raise AstraCapabilityDiscoveryError("Capability registry rejects duplicate capability identifiers.")
        self._capabilities[capability.capability_id] = capability


class AstraCapabilityDiscoveryEngine:
    def __init__(
        self,
        *,
        runtime: Any,
        capabilities: tuple[AstraCapabilityMetadata, ...] | None = None,
    ) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._registry = AstraCapabilityRegistry(capabilities or default_capabilities())
        self._operation_sequence = 0

    @property
    def registry(self) -> AstraCapabilityRegistry:
        return deepcopy(self._registry)

    def discover_capabilities(
        self,
        *,
        visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        timestamp = discovered_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Capability discovery timestamp")
        self._require_runtime_ready()
        capabilities = self._registry.discover(
            visibility=visibility,
            include_disabled=include_disabled,
            include_deprecated=include_deprecated,
        )
        governance = self._emit_governance_evidence("CAP-DISC", timestamp)
        return AstraCapabilityDiscoveryResult(
            runtime_instance_id=self._runtime_instance_id,
            discovered_at=timestamp,
            capabilities=capabilities,
            governance_outcome=governance.decision.outcome,
            evidence_reference=governance.evidence.evidence_id,
            discovery_version=CAPABILITY_DISCOVERY_ENGINE_VERSION,
        )

    def get_capability(self, capability_id: str, *, discovered_at: datetime | None = None) -> AstraCapabilityMetadata:
        timestamp = discovered_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Capability lookup timestamp")
        self._require_runtime_ready()
        capability = self._registry.get(capability_id)
        self._emit_governance_evidence("CAP-LOOKUP", timestamp)
        return capability

    def discover_for_conversation(
        self,
        *,
        conversation_snapshot: Any,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        runtime_instance_id = conversation_snapshot.metadata.runtime_instance_id
        if runtime_instance_id != self._runtime_instance_id:
            raise AstraCapabilityDiscoveryError("Conversation is not owned by the capability discovery runtime.")
        return self.discover_capabilities(discovered_at=discovered_at)

    def health(self, *, observed_at: datetime | None = None) -> AstraCapabilityHealthSnapshot:
        timestamp = observed_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Capability health timestamp")
        ready = self._is_runtime_ready()
        valid = self._registry.is_valid
        return AstraCapabilityHealthSnapshot(
            runtime_instance_id=self._runtime_instance_id,
            registry_loaded=True,
            capability_count=self._registry.capability_count,
            duplicate_free=self._registry.duplicate_free,
            registry_valid=valid,
            health_outcome=(
                AstraCapabilityHealthOutcome.HEALTHY
                if ready and valid
                else AstraCapabilityHealthOutcome.STOPPED
                if not ready
                else AstraCapabilityHealthOutcome.DEGRADED
            ),
            observed_at=timestamp,
        )

    def _emit_governance_evidence(self, operation_prefix: str, timestamp: datetime):
        operation_sequence = self._operation_sequence + 1
        result = self._runtime.evaluate_governance(
            GovernanceEvaluationInput(
                evaluation_id=f"{operation_prefix}-{operation_sequence:03d}",
                requirement_references=(
                    ConstitutionalRequirementReference(
                        constitutional_source="ASTRA-004",
                        requirement_id="AIR-CAP-001",
                        requirement_version="1.0.0",
                    ),
                ),
                requested_authority_class=AuthorityClass.READ_ONLY,
                safety_classification=SafetyClassification.PUBLIC,
                approval_state=ApprovalState.NOT_REQUIRED,
                configuration_id=ASTRA_CONFIGURATION_ID,
                configuration_version=ASTRA_CONFIGURATION_VERSION,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                evaluation_timestamp=timestamp,
            )
        )
        self._runtime.append_evidence(result.evidence)
        self._operation_sequence = operation_sequence
        return result

    def _require_runtime_ready(self) -> None:
        if not self._is_runtime_ready():
            raise AstraCapabilityDiscoveryError("Capability Discovery Engine requires a ready AstraRuntime owner.")

    def _is_runtime_ready(self) -> bool:
        return getattr(getattr(self._runtime, "state", None), "value", None) == "ready"


def default_capabilities() -> tuple[AstraCapabilityMetadata, ...]:
    requirement = ConstitutionalRequirementReference(
        constitutional_source="ASTRA-004",
        requirement_id="AIR-CAP-001",
        requirement_version="1.0.0",
    )
    return (
        AstraCapabilityMetadata(
            capability_id="cap_conversation_context_0001",
            capability_name="Conversation Context Metadata",
            capability_type=AstraCapabilityType.CONVERSATION_CONTEXT,
            owning_module="app.modules.astra_ai.conversation_context",
            version="1.0.0",
            status=AstraCapabilityStatus.AVAILABLE,
            visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=requirement,
            execution_authority=AstraCapabilityExecutionAuthority.METADATA_ONLY,
            description="Bounded runtime-owned conversation context metadata discovery.",
        ),
        AstraCapabilityMetadata(
            capability_id="cap_evidence_metadata_0001",
            capability_name="Evidence Metadata Receive",
            capability_type=AstraCapabilityType.EVIDENCE_METADATA,
            owning_module="app.modules.astra_ai.evidence_sink",
            version="1.0.0",
            status=AstraCapabilityStatus.AVAILABLE,
            visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=requirement,
            execution_authority=AstraCapabilityExecutionAuthority.METADATA_ONLY,
            description="Bounded in-memory evidence metadata receive and retrieval awareness.",
        ),
        AstraCapabilityMetadata(
            capability_id="cap_governance_metadata_0001",
            capability_name="Governance Decision Metadata",
            capability_type=AstraCapabilityType.GOVERNANCE_METADATA,
            owning_module="app.modules.astra_ai.governance",
            version="1.0.0",
            status=AstraCapabilityStatus.AVAILABLE,
            visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=requirement,
            execution_authority=AstraCapabilityExecutionAuthority.METADATA_ONLY,
            description="Deterministic governance decision metadata awareness.",
        ),
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone_aware(timestamp: datetime, field_name: str) -> None:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise AstraCapabilityDiscoveryError(f"{field_name} must be timezone-aware.")
