from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from typing import TYPE_CHECKING, Any

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


if TYPE_CHECKING:
    from app.modules.astra_ai.conversation_context import AstraConversationContextEngine, AstraConversationSnapshot


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


class AstraCapabilityRequesterClass(StrEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    INTERNAL_RUNTIME = "internal_runtime"


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


class AstraCapabilityDiscoveryRequestContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    requester_class: AstraCapabilityRequesterClass
    authenticated: bool
    runtime_instance_id: str | None = Field(default=None, pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str | None = Field(default=None, pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    maximum_visibility: AstraCapabilityVisibility
    governance_reference: ConstitutionalRequirementReference
    governance_app_id: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{2,80}$")
    governance_capability_scope: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{2,120}$")
    governance_capability_id: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{2,120}$")
    authority_token: Any | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_request_context(self):
        if self.requester_class is AstraCapabilityRequesterClass.PUBLIC:
            if self.authenticated:
                raise AstraCapabilityDiscoveryError("Public discovery context cannot assert authentication.")
            if self.maximum_visibility is not AstraCapabilityVisibility.PUBLIC:
                raise AstraCapabilityDiscoveryError("Public discovery context is limited to public visibility.")
            if self.runtime_instance_id is not None:
                raise AstraCapabilityDiscoveryError("Public discovery context cannot assert runtime ownership.")
        if self.requester_class is AstraCapabilityRequesterClass.AUTHENTICATED:
            raise AstraCapabilityDiscoveryError(
                "Authenticated discovery context requires an authoritative issuer outside ASTRA-IMP-007 scope."
            )
        if self.requester_class is AstraCapabilityRequesterClass.INTERNAL_RUNTIME:
            if not self.authenticated or self.runtime_instance_id is None or self.authority_token is None:
                raise AstraCapabilityDiscoveryError("Internal runtime discovery context requires trusted runtime ownership.")
        context_values = (
            self.governance_app_id,
            self.governance_capability_scope,
            self.governance_capability_id,
        )
        if any(value is not None for value in context_values):
            if self.requester_class is not AstraCapabilityRequesterClass.INTERNAL_RUNTIME:
                raise AstraCapabilityDiscoveryError("Governed discovery context requires internal runtime ownership.")
            if any(value is None for value in context_values):
                raise AstraCapabilityDiscoveryError("Governed discovery context must bind app, scope, and capability.")
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
        allowed_visibilities: tuple[AstraCapabilityVisibility, ...],
        requested_visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
    ) -> tuple[AstraCapabilityMetadata, ...]:
        capabilities = []
        for capability in self._capabilities.values():
            if capability.visibility not in allowed_visibilities:
                continue
            if requested_visibility is not None and capability.visibility is not requested_visibility:
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
        self._internal_authority_token = object()
        self._operation_sequence = 0

    @property
    def registry(self) -> AstraCapabilityRegistry:
        return deepcopy(self._registry)

    def discover_capabilities(
        self,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        requested_visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        timestamp = discovered_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Capability discovery timestamp")
        self._require_runtime_ready()
        self._validate_request_context(request_context, requested_visibility)
        governance = self._emit_governance_evidence("CAP-DISC", timestamp, request_context=request_context)
        capabilities = ()
        if governance.decision.outcome is GovernanceOutcome.ALLOW:
            capabilities = self._registry.discover(
                allowed_visibilities=_allowed_visibilities(request_context.maximum_visibility),
                requested_visibility=requested_visibility,
                include_disabled=include_disabled,
                include_deprecated=include_deprecated,
            )
        return AstraCapabilityDiscoveryResult(
            runtime_instance_id=self._runtime_instance_id,
            discovered_at=timestamp,
            capabilities=capabilities,
            governance_outcome=governance.decision.outcome,
            evidence_reference=governance.evidence.evidence_id,
            discovery_version=CAPABILITY_DISCOVERY_ENGINE_VERSION,
        )

    def get_capability(
        self,
        capability_id: str,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityMetadata:
        timestamp = discovered_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Capability lookup timestamp")
        self._require_runtime_ready()
        self._validate_request_context(request_context)
        governance = self._emit_governance_evidence("CAP-LOOKUP", timestamp, request_context=request_context)
        if governance.decision.outcome is not GovernanceOutcome.ALLOW:
            raise AstraCapabilityDiscoveryError("Capability lookup denied by governance outcome.")
        capability = self._registry.get(capability_id)
        if capability.visibility not in _allowed_visibilities(request_context.maximum_visibility):
            raise AstraCapabilityDiscoveryError("Capability visibility exceeds requester context.")
        return capability

    def discover_for_conversation(
        self,
        *,
        conversation_engine: "AstraConversationContextEngine",
        conversation_snapshot: "AstraConversationSnapshot",
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        self._validate_conversation_ownership(conversation_engine, conversation_snapshot)
        context = request_context.model_copy(
            update={"conversation_id": conversation_snapshot.metadata.conversation_id}
        )
        self._validate_request_context(context)
        return self.discover_capabilities(request_context=context, discovered_at=discovered_at)

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

    def internal_request_context(self) -> AstraCapabilityDiscoveryRequestContext:
        return AstraCapabilityDiscoveryRequestContext(
            requester_class=AstraCapabilityRequesterClass.INTERNAL_RUNTIME,
            authenticated=True,
            runtime_instance_id=self._runtime_instance_id,
            maximum_visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=_capability_requirement_reference(),
            authority_token=self._internal_authority_token,
        )

    def _emit_governance_evidence(
        self,
        operation_prefix: str,
        timestamp: datetime,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
    ):
        operation_sequence = self._operation_sequence + 1
        governed_context = request_context.governance_app_id is not None
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
                safety_classification=(
                    SafetyClassification.PRIVATE_READ
                    if governed_context
                    else SafetyClassification.PUBLIC
                ),
                approval_state=ApprovalState.NOT_REQUIRED,
                configuration_id=ASTRA_CONFIGURATION_ID,
                configuration_version=ASTRA_CONFIGURATION_VERSION,
                requested_app_id=request_context.governance_app_id,
                requested_capability_scope=request_context.governance_capability_scope,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                evaluation_timestamp=timestamp,
            )
        )
        self._runtime.append_evidence(result.evidence)
        self._operation_sequence = operation_sequence
        return result

    def _validate_request_context(
        self,
        request_context: AstraCapabilityDiscoveryRequestContext,
        requested_visibility: AstraCapabilityVisibility | None = None,
    ) -> None:
        if request_context.requester_class is AstraCapabilityRequesterClass.INTERNAL_RUNTIME:
            if request_context.runtime_instance_id != self._runtime_instance_id:
                raise AstraCapabilityDiscoveryError("Internal discovery context is not owned by this runtime.")
            if request_context.authority_token is not self._internal_authority_token:
                raise AstraCapabilityDiscoveryError("Internal discovery context was not issued by this runtime.")
        if request_context.requester_class is AstraCapabilityRequesterClass.AUTHENTICATED:
            raise AstraCapabilityDiscoveryError("Authenticated discovery context has no authorized issuer in ASTRA-IMP-007.")
        if requested_visibility is not None and requested_visibility not in _allowed_visibilities(request_context.maximum_visibility):
            raise AstraCapabilityDiscoveryError("Requested visibility exceeds requester context.")

    def _validate_conversation_ownership(
        self,
        conversation_engine: "AstraConversationContextEngine",
        conversation_snapshot: "AstraConversationSnapshot",
    ) -> None:
        from app.modules.astra_ai.conversation_context import (
            AstraConversationContextEngine,
            AstraConversationLifecycleState,
            AstraConversationSnapshot,
        )

        if not isinstance(conversation_engine, AstraConversationContextEngine):
            raise AstraCapabilityDiscoveryError("Conversation discovery requires a certified Conversation Context Engine.")
        if not isinstance(conversation_snapshot, AstraConversationSnapshot):
            raise AstraCapabilityDiscoveryError("Conversation discovery requires a certified conversation snapshot.")
        if conversation_snapshot.metadata.runtime_instance_id != self._runtime_instance_id:
            raise AstraCapabilityDiscoveryError("Conversation is not owned by the capability discovery runtime.")
        try:
            owned_snapshot = conversation_engine.get_conversation(conversation_snapshot.metadata.conversation_id)
        except Exception as exc:
            raise AstraCapabilityDiscoveryError("Conversation snapshot is not owned by the provided engine.") from exc
        if owned_snapshot != conversation_snapshot:
            raise AstraCapabilityDiscoveryError("Conversation snapshot is stale or not owned by the provided engine.")
        if owned_snapshot.metadata.lifecycle_state in {
            AstraConversationLifecycleState.CLOSED,
            AstraConversationLifecycleState.FAULTED,
        }:
            raise AstraCapabilityDiscoveryError("Conversation state is not eligible for capability discovery.")

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


def authenticated_discovery_context() -> AstraCapabilityDiscoveryRequestContext:
    raise AstraCapabilityDiscoveryError(
        "Authenticated discovery context requires an authoritative issuer outside ASTRA-IMP-007 scope."
    )


def public_discovery_context() -> AstraCapabilityDiscoveryRequestContext:
    return AstraCapabilityDiscoveryRequestContext(
        requester_class=AstraCapabilityRequesterClass.PUBLIC,
        authenticated=False,
        maximum_visibility=AstraCapabilityVisibility.PUBLIC,
        governance_reference=_capability_requirement_reference(),
    )


def _capability_requirement_reference() -> ConstitutionalRequirementReference:
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-004",
        requirement_id="AIR-CAP-001",
        requirement_version="1.0.0",
    )


def _allowed_visibilities(maximum_visibility: AstraCapabilityVisibility) -> tuple[AstraCapabilityVisibility, ...]:
    if maximum_visibility is AstraCapabilityVisibility.PUBLIC:
        return (AstraCapabilityVisibility.PUBLIC,)
    if maximum_visibility is AstraCapabilityVisibility.AUTHENTICATED:
        return (AstraCapabilityVisibility.PUBLIC, AstraCapabilityVisibility.AUTHENTICATED)
    return (
        AstraCapabilityVisibility.PUBLIC,
        AstraCapabilityVisibility.AUTHENTICATED,
        AstraCapabilityVisibility.INTERNAL,
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone_aware(timestamp: datetime, field_name: str) -> None:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise AstraCapabilityDiscoveryError(f"{field_name} must be timezone-aware.")
