from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.configuration import LoadedAstraConfiguration, get_astra_configuration
from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryEngine,
    AstraCapabilityDiscoveryRequestContext,
    AstraCapabilityDiscoveryResult,
    AstraCapabilityHealthSnapshot,
    AstraCapabilityMetadata,
    AstraCapabilityVisibility,
)
from app.modules.astra_ai.constitutional_contracts import (
    AuditEvidenceBehavior,
    BoundedEvidence,
    EnvironmentScope,
    ProductionAuthorizationState,
    RuntimeUseState,
    assert_no_prohibited_contract_material,
)
from app.modules.astra_ai.evidence_sink import DEFAULT_EVIDENCE_SINK_CAPACITY, InMemoryEvidenceSink
from app.modules.astra_ai.governance import GovernanceEvaluationInput, GovernanceEvaluationResult, evaluate_governance


ASTRA_RUNTIME_ID = "ASTRA-RUNTIME-005"
ASTRA_RUNTIME_NAME = "Astra Runtime Core"
ASTRA_RUNTIME_VERSION = "1.0.0"
ASTRA_CONSTITUTIONAL_BASELINE = "ASTRA-001-through-ASTRA-010:accepted-frozen"
ASTRA_RUNTIME_IMPLEMENTATION_PHASE = "ASTRA-IMP-005"
ASTRA_RUNTIME_IMPLEMENTATION_REVISION = "1.0.0"


class AstraRuntimeError(ValueError):
    """Raised when the minimal Astra runtime cannot satisfy its lifecycle contract."""


class AstraRuntimeState(StrEnum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAULTED = "faulted"


class AstraRuntimeHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    INITIALIZING = "initializing"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    FAULTED = "faulted"


class AstraRuntimeFaultClassification(StrEnum):
    STARTUP_FAILURE = "startup_failure"
    SHUTDOWN_FAILURE = "shutdown_failure"
    COMPONENT_REGISTRATION_FAILURE = "component_registration_failure"


class AstraRuntimeRecoverability(StrEnum):
    SAFE_SHUTDOWN_AVAILABLE = "safe_shutdown_available"
    NEW_INSTANCE_REQUIRED = "new_instance_required"


class AstraRuntimeComponentIdentifier(StrEnum):
    CONFIGURATION = "configuration"
    GOVERNANCE = "governance"
    EVIDENCE_SINK = "evidence_sink"
    CAPABILITY_DISCOVERY = "capability_discovery"


AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS = (
    AstraRuntimeComponentIdentifier.CONFIGURATION,
    AstraRuntimeComponentIdentifier.GOVERNANCE,
    AstraRuntimeComponentIdentifier.EVIDENCE_SINK,
    AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY,
)

ALLOWED_RUNTIME_TRANSITIONS = {
    AstraRuntimeState.UNINITIALIZED: (AstraRuntimeState.INITIALIZING,),
    AstraRuntimeState.INITIALIZING: (AstraRuntimeState.READY, AstraRuntimeState.FAULTED),
    AstraRuntimeState.READY: (AstraRuntimeState.STOPPING,),
    AstraRuntimeState.STOPPING: (AstraRuntimeState.STOPPED, AstraRuntimeState.FAULTED),
    AstraRuntimeState.FAULTED: (AstraRuntimeState.STOPPING,),
    AstraRuntimeState.STOPPED: (),
}


class AstraRuntimeIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_id: str = Field(pattern=r"^[A-Z][A-Z0-9-]{2,80}$")
    runtime_name: str = Field(min_length=4, max_length=80)
    runtime_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    constitutional_baseline: str = Field(min_length=12, max_length=120)
    implementation_phase: str = Field(pattern=r"^ASTRA-IMP-005$")
    implementation_revision: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    startup_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    created_at: datetime

    @model_validator(mode="after")
    def validate_runtime_identity(self):
        _ensure_timezone_aware(self.created_at, "Runtime creation timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraRuntimeStartupMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    configuration_id: str = Field(pattern=r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
    configuration_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    startup_at: datetime
    environment_scope: EnvironmentScope
    production_authorization_state: ProductionAuthorizationState

    @model_validator(mode="after")
    def validate_startup_metadata(self):
        _ensure_timezone_aware(self.startup_at, "Runtime startup timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraRuntimeFault(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: AstraRuntimeFaultClassification
    lifecycle_stage: AstraRuntimeState
    safe_summary: str = Field(min_length=8, max_length=180)
    fault_timestamp: datetime
    relevant_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    recoverability: AstraRuntimeRecoverability

    @model_validator(mode="after")
    def validate_fault(self):
        _ensure_timezone_aware(self.fault_timestamp, "Runtime fault timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraRuntimeComponentRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_identifier: AstraRuntimeComponentIdentifier
    component_type: str = Field(min_length=4, max_length=80)
    registered_at: datetime
    implementation_reference: str = Field(pattern=r"^ASTRA-IMP-00[1-7]$")
    certified_parent_reference: str = Field(min_length=8, max_length=80)

    @model_validator(mode="after")
    def validate_registration(self):
        _ensure_timezone_aware(self.registered_at, "Runtime component registration timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraRuntimeHealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_state: AstraRuntimeState
    runtime_identity: AstraRuntimeIdentity
    configuration_loaded: bool
    configuration_valid: bool
    governance_available: bool
    evidence_sink_available: bool
    capability_discovery_available: bool
    registered_component_identifiers: tuple[AstraRuntimeComponentIdentifier, ...]
    startup_metadata: AstraRuntimeStartupMetadata | None = None
    environment_scope: EnvironmentScope | None = None
    production_authorization_state: ProductionAuthorizationState | None = None
    health_outcome: AstraRuntimeHealthOutcome
    fault: AstraRuntimeFault | None = None
    health_timestamp: datetime

    @model_validator(mode="after")
    def validate_health(self):
        _ensure_timezone_aware(self.health_timestamp, "Runtime health timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class _ComponentRegistry:
    def __init__(self) -> None:
        self._registrations: dict[AstraRuntimeComponentIdentifier, AstraRuntimeComponentRegistration] = {}
        self._sealed = False

    def register(
        self,
        *,
        component_identifier: AstraRuntimeComponentIdentifier,
        component_type: str,
        implementation_reference: str,
        certified_parent_reference: str,
        registered_at: datetime,
    ) -> None:
        if self._sealed:
            raise AstraRuntimeError("Runtime component registry is sealed.")
        if component_identifier not in AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS:
            raise AstraRuntimeError("Runtime component registry rejects unauthorized component identifiers.")
        if component_identifier in self._registrations:
            raise AstraRuntimeError("Runtime component registry rejects duplicate component identifiers.")
        self._registrations[component_identifier] = AstraRuntimeComponentRegistration(
            component_identifier=component_identifier,
            component_type=component_type,
            registered_at=registered_at,
            implementation_reference=implementation_reference,
            certified_parent_reference=certified_parent_reference,
        )

    def seal(self) -> None:
        self.validate_complete()
        self._sealed = True

    def validate_complete(self) -> None:
        if self.identifiers != AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS:
            raise AstraRuntimeError("Runtime component registry must contain exactly the authorized foundation components.")

    @property
    def identifiers(self) -> tuple[AstraRuntimeComponentIdentifier, ...]:
        return tuple(identifier for identifier in AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS if identifier in self._registrations)

    def registrations(self) -> tuple[AstraRuntimeComponentRegistration, ...]:
        return tuple(deepcopy(self._registrations[identifier]) for identifier in self.identifiers)


class AstraRuntimeGovernanceInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def evaluate(self, input_contract: GovernanceEvaluationInput) -> GovernanceEvaluationResult:
        return self._runtime.evaluate_governance(input_contract)


class AstraRuntimeEvidenceInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def append(self, evidence: BoundedEvidence) -> BoundedEvidence:
        return self._runtime.append_evidence(evidence)

    def retrieve(self) -> tuple[BoundedEvidence, ...]:
        return self._runtime.retrieve_evidence()

    def count(self) -> int:
        return self._runtime.evidence_count()


class AstraRuntimeCapabilityDiscoveryInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def discover(
        self,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        requested_visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        return self._runtime.discover_capabilities(
            request_context=request_context,
            requested_visibility=requested_visibility,
            include_disabled=include_disabled,
            include_deprecated=include_deprecated,
            discovered_at=discovered_at,
        )

    def get(
        self,
        capability_id: str,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityMetadata:
        return self._runtime.get_capability(
            capability_id,
            request_context=request_context,
            discovered_at=discovered_at,
        )

    def discover_for_conversation(
        self,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        return self._runtime.discover_capabilities_for_conversation(
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            request_context=request_context,
            discovered_at=discovered_at,
        )

    def health(self, *, observed_at: datetime | None = None) -> AstraCapabilityHealthSnapshot:
        return self._runtime.capability_discovery_health(observed_at=observed_at)


class AstraRuntime:
    """Minimal internal owner for certified Astra foundations.

    The runtime owns component lifecycle only. It does not converse, plan,
    retrieve memory, call providers, execute tools, expose APIs, persist data,
    or authorize production behavior.
    """

    def __init__(
        self,
        *,
        created_at: datetime | None = None,
        startup_instance_id: str | None = None,
        evidence_sink_capacity: int = DEFAULT_EVIDENCE_SINK_CAPACITY,
    ) -> None:
        timestamp = created_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Runtime creation timestamp")
        self._identity = AstraRuntimeIdentity(
            runtime_id=ASTRA_RUNTIME_ID,
            runtime_name=ASTRA_RUNTIME_NAME,
            runtime_version=ASTRA_RUNTIME_VERSION,
            constitutional_baseline=ASTRA_CONSTITUTIONAL_BASELINE,
            implementation_phase=ASTRA_RUNTIME_IMPLEMENTATION_PHASE,
            implementation_revision=ASTRA_RUNTIME_IMPLEMENTATION_REVISION,
            startup_instance_id=startup_instance_id or f"astra_rt_{uuid4().hex}",
            created_at=timestamp,
        )
        self._state = AstraRuntimeState.UNINITIALIZED
        self._evidence_sink_capacity = evidence_sink_capacity
        self._configuration: LoadedAstraConfiguration | None = None
        self._governance = None
        self._evidence_sink: InMemoryEvidenceSink | None = None
        self._capability_discovery: AstraCapabilityDiscoveryEngine | None = None
        self._registry = _ComponentRegistry()
        self._fault: AstraRuntimeFault | None = None
        self._startup_metadata: AstraRuntimeStartupMetadata | None = None
        self._governance_interface = AstraRuntimeGovernanceInterface(self)
        self._evidence_interface = AstraRuntimeEvidenceInterface(self)
        self._capability_discovery_interface = AstraRuntimeCapabilityDiscoveryInterface(self)

    @property
    def identity(self) -> AstraRuntimeIdentity:
        return self._identity

    @property
    def state(self) -> AstraRuntimeState:
        return self._state

    @property
    def registered_component_identifiers(self) -> tuple[AstraRuntimeComponentIdentifier, ...]:
        return self._registry.identifiers

    @property
    def component_registrations(self) -> tuple[AstraRuntimeComponentRegistration, ...]:
        return self._registry.registrations()

    @property
    def configuration(self) -> LoadedAstraConfiguration:
        self._require_ready_component(self._configuration, "configuration")
        return deepcopy(self._configuration)

    @property
    def governance(self) -> AstraRuntimeGovernanceInterface:
        return self._governance_interface

    @property
    def evidence_sink(self) -> AstraRuntimeEvidenceInterface:
        return self._evidence_interface

    @property
    def capability_discovery(self) -> AstraRuntimeCapabilityDiscoveryInterface:
        return self._capability_discovery_interface

    def evaluate_governance(self, input_contract: GovernanceEvaluationInput) -> GovernanceEvaluationResult:
        self._require_ready_component(self._governance, "governance")
        return self._governance(input_contract)

    def append_evidence(self, evidence: BoundedEvidence) -> BoundedEvidence:
        self._require_ready_component(self._evidence_sink, "evidence sink")
        return self._evidence_sink.append(evidence)

    def retrieve_evidence(self) -> tuple[BoundedEvidence, ...]:
        self._require_ready_component(self._evidence_sink, "evidence sink")
        return self._evidence_sink.retrieve()

    def evidence_count(self) -> int:
        self._require_ready_component(self._evidence_sink, "evidence sink")
        return self._evidence_sink.count()

    def discover_capabilities(
        self,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        requested_visibility: AstraCapabilityVisibility | None = None,
        include_disabled: bool = False,
        include_deprecated: bool = False,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        self._require_ready_component(self._capability_discovery, "capability discovery")
        return self._capability_discovery.discover_capabilities(
            request_context=request_context,
            requested_visibility=requested_visibility,
            include_disabled=include_disabled,
            include_deprecated=include_deprecated,
            discovered_at=discovered_at,
        )

    def get_capability(
        self,
        capability_id: str,
        *,
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityMetadata:
        self._require_ready_component(self._capability_discovery, "capability discovery")
        return self._capability_discovery.get_capability(
            capability_id,
            request_context=request_context,
            discovered_at=discovered_at,
        )

    def discover_capabilities_for_conversation(
        self,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        request_context: AstraCapabilityDiscoveryRequestContext,
        discovered_at: datetime | None = None,
    ) -> AstraCapabilityDiscoveryResult:
        self._require_ready_component(self._capability_discovery, "capability discovery")
        return self._capability_discovery.discover_for_conversation(
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            request_context=request_context,
            discovered_at=discovered_at,
        )

    def capability_discovery_health(self, *, observed_at: datetime | None = None) -> AstraCapabilityHealthSnapshot:
        self._require_ready_component(self._capability_discovery, "capability discovery")
        return self._capability_discovery.health(observed_at=observed_at)

    def startup(self) -> AstraRuntimeHealthSnapshot:
        if self._state is not AstraRuntimeState.UNINITIALIZED:
            raise AstraRuntimeError("Runtime startup is allowed only from the uninitialized state.")

        self._transition_to(AstraRuntimeState.INITIALIZING)
        try:
            loaded_configuration = self._load_configuration()
            self._validate_configuration_boundary(loaded_configuration)
            startup_timestamp = loaded_configuration.provenance.loaded_at
            registry = _ComponentRegistry()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.CONFIGURATION,
                component_type="LoadedAstraConfiguration",
                implementation_reference="ASTRA-IMP-002",
                certified_parent_reference="ASTRA-IMP-002 Certified / Approved",
                registered_at=startup_timestamp,
            )
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.GOVERNANCE,
                component_type="MinimalGovernanceKernel",
                implementation_reference="ASTRA-IMP-003",
                certified_parent_reference="ASTRA-IMP-003 Certified / Approved",
                registered_at=startup_timestamp,
            )
            evidence_sink = self._create_evidence_sink(loaded_configuration)
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.EVIDENCE_SINK,
                component_type="InMemoryEvidenceSink",
                implementation_reference="ASTRA-IMP-004",
                certified_parent_reference="ASTRA-IMP-004 Certified / Approved",
                registered_at=startup_timestamp,
            )
            capability_discovery = self._create_capability_discovery_engine()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY,
                component_type="AstraCapabilityDiscoveryEngine",
                implementation_reference="ASTRA-IMP-007",
                certified_parent_reference="ASTRA-IMP-007 Implemented / Pending Certification",
                registered_at=startup_timestamp,
            )
            registry.seal()

            self._configuration = loaded_configuration
            self._governance = evaluate_governance
            self._evidence_sink = evidence_sink
            self._capability_discovery = capability_discovery
            self._registry = registry
            self._startup_metadata = self._startup_metadata_from_configuration(loaded_configuration)
            self._fault = None
            self._transition_to(AstraRuntimeState.READY)
        except Exception:
            self._clear_owned_components()
            self._fault = self._bounded_fault(
                classification=AstraRuntimeFaultClassification.STARTUP_FAILURE,
                stage=AstraRuntimeState.INITIALIZING,
                summary="Runtime startup failed before readiness.",
                reference="astra-runtime:startup",
                recoverability=AstraRuntimeRecoverability.NEW_INSTANCE_REQUIRED,
            )
            self._transition_to(AstraRuntimeState.FAULTED)
            raise AstraRuntimeError("Runtime startup failed closed.") from None

        return self.health()

    def shutdown(self) -> AstraRuntimeHealthSnapshot:
        if self._state not in {AstraRuntimeState.READY, AstraRuntimeState.FAULTED}:
            raise AstraRuntimeError("Runtime shutdown is allowed only from ready or faulted states.")

        try:
            self._transition_to(AstraRuntimeState.STOPPING)
            self._clear_owned_components()
            self._transition_to(AstraRuntimeState.STOPPED)
        except Exception:
            self._fault = self._bounded_fault(
                classification=AstraRuntimeFaultClassification.SHUTDOWN_FAILURE,
                stage=AstraRuntimeState.STOPPING,
                summary="Runtime shutdown failed before stopped state.",
                reference="astra-runtime:shutdown",
                recoverability=AstraRuntimeRecoverability.NEW_INSTANCE_REQUIRED,
            )
            self._transition_to(AstraRuntimeState.FAULTED)
            raise AstraRuntimeError("Runtime shutdown failed closed.") from None

        return self.health()

    def health(self, *, observed_at: datetime | None = None) -> AstraRuntimeHealthSnapshot:
        timestamp = observed_at or _utc_now()
        _ensure_timezone_aware(timestamp, "Runtime health timestamp")
        configuration_loaded = self._configuration is not None
        configuration_valid = configuration_loaded and self._is_configuration_valid(self._configuration)
        governance_available = self._governance is not None
        evidence_sink_available = self._evidence_sink is not None
        capability_discovery_available = self._capability_discovery is not None
        identifiers = self._registry.identifiers
        outcome = self._health_outcome(
            configuration_valid=configuration_valid,
            governance_available=governance_available,
            evidence_sink_available=evidence_sink_available,
            capability_discovery_available=capability_discovery_available,
            identifiers=identifiers,
        )
        return AstraRuntimeHealthSnapshot(
            runtime_state=self._state,
            runtime_identity=self._identity,
            configuration_loaded=configuration_loaded,
            configuration_valid=configuration_valid,
            governance_available=governance_available,
            evidence_sink_available=evidence_sink_available,
            capability_discovery_available=capability_discovery_available,
            registered_component_identifiers=identifiers,
            startup_metadata=self._startup_metadata,
            environment_scope=self._startup_metadata.environment_scope if self._startup_metadata is not None else None,
            production_authorization_state=(
                self._startup_metadata.production_authorization_state if self._startup_metadata is not None else None
            ),
            health_outcome=outcome,
            fault=self._fault,
            health_timestamp=timestamp,
        )

    def _load_configuration(self) -> LoadedAstraConfiguration:
        return get_astra_configuration()

    def _create_evidence_sink(self, loaded_configuration: LoadedAstraConfiguration) -> InMemoryEvidenceSink:
        return InMemoryEvidenceSink(
            capacity=self._evidence_sink_capacity,
            loaded_configuration=loaded_configuration,
        )

    def _create_capability_discovery_engine(self) -> AstraCapabilityDiscoveryEngine:
        return AstraCapabilityDiscoveryEngine(runtime=self)

    def _transition_to(self, next_state: AstraRuntimeState) -> None:
        if next_state not in ALLOWED_RUNTIME_TRANSITIONS[self._state]:
            raise AstraRuntimeError("Runtime lifecycle transition is not authorized.")
        self._state = next_state

    def _clear_owned_components(self) -> None:
        self._configuration = None
        self._governance = None
        self._evidence_sink = None
        self._capability_discovery = None
        self._registry = _ComponentRegistry()
        self._startup_metadata = None

    def _validate_configuration_boundary(self, loaded_configuration: LoadedAstraConfiguration) -> None:
        if not self._is_configuration_valid(loaded_configuration):
            raise AstraRuntimeError("Runtime rejected invalid Astra configuration.")

    def _is_configuration_valid(self, loaded_configuration: LoadedAstraConfiguration | None) -> bool:
        if loaded_configuration is None:
            return False
        configuration = loaded_configuration.configuration
        return all(
            (
                not configuration.feature_enabled,
                configuration.production_authorization_state is ProductionAuthorizationState.NOT_APPROVED,
                configuration.provider_use is RuntimeUseState.DISABLED,
                configuration.memory_use is RuntimeUseState.DISABLED,
                configuration.adaptation_use is RuntimeUseState.DISABLED,
                configuration.execution_handoff is RuntimeUseState.DISABLED,
                configuration.audit_evidence_behavior is AuditEvidenceBehavior.METADATA_ONLY,
                configuration.fail_closed_default,
            )
        )

    def _require_ready_component(self, component, component_name: str) -> None:
        if self._state is not AstraRuntimeState.READY or component is None:
            raise AstraRuntimeError(f"Runtime {component_name} access requires ready state.")

    def _startup_metadata_from_configuration(
        self,
        loaded_configuration: LoadedAstraConfiguration,
    ) -> AstraRuntimeStartupMetadata:
        configuration = loaded_configuration.configuration
        return AstraRuntimeStartupMetadata(
            configuration_id=configuration.configuration_id,
            configuration_version=configuration.configuration_version,
            startup_at=loaded_configuration.provenance.loaded_at,
            environment_scope=configuration.environment_scope,
            production_authorization_state=configuration.production_authorization_state,
        )

    def _health_outcome(
        self,
        *,
        configuration_valid: bool,
        governance_available: bool,
        evidence_sink_available: bool,
        capability_discovery_available: bool,
        identifiers: tuple[AstraRuntimeComponentIdentifier, ...],
    ) -> AstraRuntimeHealthOutcome:
        if self._state is AstraRuntimeState.FAULTED:
            return AstraRuntimeHealthOutcome.FAULTED
        if self._state is AstraRuntimeState.INITIALIZING:
            return AstraRuntimeHealthOutcome.INITIALIZING
        if self._state in {AstraRuntimeState.UNINITIALIZED, AstraRuntimeState.STOPPING, AstraRuntimeState.STOPPED}:
            return AstraRuntimeHealthOutcome.STOPPED
        if (
            self._state is AstraRuntimeState.READY
            and configuration_valid
            and governance_available
            and evidence_sink_available
            and capability_discovery_available
            and identifiers == AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS
        ):
            return AstraRuntimeHealthOutcome.HEALTHY
        return AstraRuntimeHealthOutcome.DEGRADED

    def _bounded_fault(
        self,
        *,
        classification: AstraRuntimeFaultClassification,
        stage: AstraRuntimeState,
        summary: str,
        reference: str,
        recoverability: AstraRuntimeRecoverability,
    ) -> AstraRuntimeFault:
        return AstraRuntimeFault(
            classification=classification,
            lifecycle_stage=stage,
            safe_summary=summary,
            fault_timestamp=_utc_now(),
            relevant_reference=reference,
            recoverability=recoverability,
        )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone_aware(timestamp: datetime, field_name: str) -> None:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise AstraRuntimeError(f"{field_name} must be timezone-aware.")
