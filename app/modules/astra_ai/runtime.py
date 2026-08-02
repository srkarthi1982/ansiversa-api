from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.activation import (
    AstraRuntimeActivationContract,
    AstraRuntimeActivationIssuer,
    AstraRuntimeActivationSnapshot,
    SUBSCRIPTION_MANAGER_APP_ID,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
    activation_digest,
    activation_snapshot,
    load_runtime_activation,
)
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
from app.modules.astra_ai.diagnostic_projection import (
    AstraDiagnosticProjection,
    AstraDiagnosticProjectionEngine,
    AstraDiagnosticProjectionHealth,
    AstraDiagnosticProjectionKind,
    AstraDiagnosticProjectionRequest,
    AstraDiagnosticRedactionPosture,
    AstraDiagnosticSection,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput, GovernanceEvaluationResult, evaluate_governance
from app.modules.astra_ai.intent_resolution import (
    AstraIntentHealthSnapshot,
    AstraIntentRequest,
    AstraIntentResolution,
    AstraIntentResolutionEngine,
)
from app.modules.astra_ai.metadata_activation_binding import (
    AstraGovernedMetadataContext,
    AstraGovernedMetadataContextIssuer,
)
from app.modules.astra_ai.planning import (
    AstraPlanningEngine,
    AstraPlanningHealthSnapshot,
    AstraPlanningRequest,
    AstraProposedPlan,
)
from app.modules.astra_ai.read_access_authorization import (
    AstraAuthorityProofIssuer,
    AstraReadAccessAuthorizationEngine,
    AstraReadAuthorizationDecision,
    AstraReadAuthorizationHealth,
    AstraReadAuthorizationRequest,
)
from app.modules.astra_ai.read_authority_binding import (
    AstraBoundReadAuthorization,
    AstraReadAuthorityBinding,
    AstraReadAuthorityCapabilitySummary,
    certified_subscription_manager_read_registry,
    create_runtime_read_authority_issuers,
)
from app.modules.astra_ai.read_execution import (
    AstraReadExecutionBridge,
    AstraReadExecutionRequest,
    AstraReadExecutionResult,
)


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
    PLANNING = "planning"
    INTENT_RESOLUTION = "intent_resolution"
    READ_ACCESS_AUTHORIZATION = "read_access_authorization"
    DIAGNOSTIC_PROJECTION = "diagnostic_projection"


AUTHORIZED_RUNTIME_COMPONENT_IDENTIFIERS = (
    AstraRuntimeComponentIdentifier.CONFIGURATION,
    AstraRuntimeComponentIdentifier.GOVERNANCE,
    AstraRuntimeComponentIdentifier.EVIDENCE_SINK,
    AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY,
    AstraRuntimeComponentIdentifier.PLANNING,
    AstraRuntimeComponentIdentifier.INTENT_RESOLUTION,
    AstraRuntimeComponentIdentifier.READ_ACCESS_AUTHORIZATION,
    AstraRuntimeComponentIdentifier.DIAGNOSTIC_PROJECTION,
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
    implementation_reference: str = Field(pattern=r"^ASTRA-IMP-0(?:0[1-9]|1[01])$")
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
    planning_available: bool
    intent_resolution_available: bool
    read_access_authorization_available: bool
    diagnostic_projection_available: bool
    registered_component_identifiers: tuple[AstraRuntimeComponentIdentifier, ...]
    startup_metadata: AstraRuntimeStartupMetadata | None = None
    activation: AstraRuntimeActivationSnapshot | None = None
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

    def internal_request_context(self) -> AstraCapabilityDiscoveryRequestContext:
        return self._runtime.internal_capability_discovery_context()


class AstraRuntimePlanningInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def propose(
        self,
        request: AstraPlanningRequest,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        requester_context: AstraCapabilityDiscoveryRequestContext,
    ) -> AstraProposedPlan:
        return self._runtime.propose_plan(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            requester_context=requester_context,
        )

    def health(self, *, observed_at: datetime | None = None) -> AstraPlanningHealthSnapshot:
        return self._runtime.planning_health(observed_at=observed_at)


class AstraRuntimeIntentResolutionInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def resolve(self, request: AstraIntentRequest, *, conversation_engine, conversation_snapshot, requester_context):
        return self._runtime.resolve_intent(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            requester_context=requester_context,
        )

    def health(self, *, observed_at=None) -> AstraIntentHealthSnapshot:
        return self._runtime.intent_resolution_health(observed_at=observed_at)


class AstraRuntimeReadAccessAuthorizationInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def authorize(
        self, request: AstraReadAuthorizationRequest, *, conversation_engine, conversation_snapshot, intent_resolution, plan=None
    ) -> AstraReadAuthorizationDecision:
        return self._runtime.authorize_read_access(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=plan,
        )

    def health(self, *, observed_at=None) -> AstraReadAuthorizationHealth:
        return self._runtime.read_access_authorization_health(observed_at=observed_at)


class AstraRuntimeReadAuthorityInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def capabilities(self) -> tuple[AstraReadAuthorityCapabilitySummary, ...]:
        return self._runtime.read_authority_capabilities()

    def authorize_subscription_manager_read(self, **values: Any) -> AstraBoundReadAuthorization:
        return self._runtime.authorize_subscription_manager_read(**values)


class AstraRuntimeReadExecutionInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def issue_request(self, **values: Any) -> AstraReadExecutionRequest:
        return self._runtime.issue_read_execution_request(**values)

    def execute(self, request: AstraReadExecutionRequest, *, db, authenticated_user) -> AstraReadExecutionResult:
        return self._runtime.execute_read(request, db=db, authenticated_user=authenticated_user)


class AstraRuntimeDiagnosticProjectionInterface:
    def __init__(self, runtime: AstraRuntime) -> None:
        self._runtime = runtime

    def issue_request(self, **values) -> AstraDiagnosticProjectionRequest:
        return self._runtime.issue_diagnostic_projection_request(**values)

    def project(
        self, request: AstraDiagnosticProjectionRequest, *, created_at: datetime | None = None
    ) -> AstraDiagnosticProjection:
        return self._runtime.create_diagnostic_projection(request, created_at=created_at)

    def health(self, *, observed_at=None) -> AstraDiagnosticProjectionHealth:
        return self._runtime.diagnostic_projection_health(observed_at=observed_at)


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
        self._activation: AstraRuntimeActivationContract | None = None
        self._activation_issuer: AstraRuntimeActivationIssuer | None = None
        self._metadata_context_issuer: AstraGovernedMetadataContextIssuer | None = None
        self._governance = None
        self._evidence_sink: InMemoryEvidenceSink | None = None
        self._capability_discovery: AstraCapabilityDiscoveryEngine | None = None
        self._planning: AstraPlanningEngine | None = None
        self._intent_resolution: AstraIntentResolutionEngine | None = None
        self._read_access_authorization: AstraReadAccessAuthorizationEngine | None = None
        self._read_authority_binding: AstraReadAuthorityBinding | None = None
        self._read_execution_bridge: AstraReadExecutionBridge | None = None
        self._diagnostic_projection: AstraDiagnosticProjectionEngine | None = None
        self._diagnostic_output_registration_authority = object()
        self._activation_issuer_authority = object()
        self._metadata_context_issuer_authority = object()
        self._read_issuer_authority = object()
        self._read_execution_registration_authority = object()
        self._read_execution_request_authority = object()
        self._read_authority_issuers: dict[str, AstraAuthorityProofIssuer] = {}
        self._registry = _ComponentRegistry()
        self._fault: AstraRuntimeFault | None = None
        self._startup_metadata: AstraRuntimeStartupMetadata | None = None
        self._governance_interface = AstraRuntimeGovernanceInterface(self)
        self._evidence_interface = AstraRuntimeEvidenceInterface(self)
        self._capability_discovery_interface = AstraRuntimeCapabilityDiscoveryInterface(self)
        self._planning_interface = AstraRuntimePlanningInterface(self)
        self._intent_resolution_interface = AstraRuntimeIntentResolutionInterface(self)
        self._read_access_authorization_interface = AstraRuntimeReadAccessAuthorizationInterface(self)
        self._read_authority_interface = AstraRuntimeReadAuthorityInterface(self)
        self._read_execution_interface = AstraRuntimeReadExecutionInterface(self)
        self._diagnostic_projection_interface = AstraRuntimeDiagnosticProjectionInterface(self)

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
    def activation(self) -> AstraRuntimeActivationSnapshot:
        self._require_ready_component(self._configuration, "configuration")
        return activation_snapshot(
            self._activation,
            runtime_instance_id=self._identity.startup_instance_id,
            environment_scope=self._configuration.configuration.environment_scope,
            observed_at=_utc_now(),
        )

    @property
    def governance(self) -> AstraRuntimeGovernanceInterface:
        return self._governance_interface

    @property
    def evidence_sink(self) -> AstraRuntimeEvidenceInterface:
        return self._evidence_interface

    @property
    def capability_discovery(self) -> AstraRuntimeCapabilityDiscoveryInterface:
        return self._capability_discovery_interface

    @property
    def planning(self) -> AstraRuntimePlanningInterface:
        return self._planning_interface

    @property
    def intent_resolution(self) -> AstraRuntimeIntentResolutionInterface:
        return self._intent_resolution_interface

    @property
    def read_access_authorization(self) -> AstraRuntimeReadAccessAuthorizationInterface:
        return self._read_access_authorization_interface

    @property
    def read_authority(self) -> AstraRuntimeReadAuthorityInterface:
        return self._read_authority_interface

    @property
    def read_execution(self) -> AstraRuntimeReadExecutionInterface:
        return self._read_execution_interface

    @property
    def diagnostic_projection(self) -> AstraRuntimeDiagnosticProjectionInterface:
        return self._diagnostic_projection_interface

    def evaluate_governance(self, input_contract: GovernanceEvaluationInput) -> GovernanceEvaluationResult:
        self._require_ready_component(self._governance, "governance")
        runtime_owned_input = input_contract.model_copy(
            update={
                "runtime_instance_id": self._identity.startup_instance_id,
                "activation_context": self._activation,
                "activation_reference": self._activation.activation_reference if self._activation else None,
                "activation_digest": f"sha256:{activation_digest(self._activation)}" if self._activation else None,
            }
        )
        return self._governance(runtime_owned_input)

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
        result = self._capability_discovery.health(observed_at=observed_at)
        self._register_diagnostic_output(result)
        return result

    def internal_capability_discovery_context(self) -> AstraCapabilityDiscoveryRequestContext:
        self._require_ready_component(self._capability_discovery, "capability discovery")
        return self._capability_discovery.internal_request_context()

    def propose_plan(
        self,
        request: AstraPlanningRequest,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        requester_context: AstraCapabilityDiscoveryRequestContext,
    ) -> AstraProposedPlan:
        self._require_ready_component(self._planning, "planning")
        result = self._planning.propose(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            requester_context=requester_context,
        )
        self._register_diagnostic_output(result)
        return result

    def planning_health(self, *, observed_at: datetime | None = None) -> AstraPlanningHealthSnapshot:
        self._require_ready_component(self._planning, "planning")
        result = self._planning.health(observed_at=observed_at)
        self._register_diagnostic_output(result)
        return result

    def resolve_intent(self, request: AstraIntentRequest, *, conversation_engine, conversation_snapshot, requester_context):
        self._require_ready_component(self._intent_resolution, "intent resolution")
        result = self._intent_resolution.resolve(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            requester_context=requester_context,
        )
        self._register_diagnostic_output(result)
        return result

    def issue_subscription_manager_governed_metadata_context(
        self,
        *,
        conversation_engine: Any,
        conversation_snapshot: Any,
        adapter_capability_id: str,
        requested_at: datetime,
    ) -> AstraGovernedMetadataContext:
        self._require_ready_component(self._metadata_context_issuer, "governed metadata context issuer")
        self._require_ready_component(self._activation, "runtime activation")
        self._validate_governed_metadata_conversation(conversation_engine, conversation_snapshot)
        current_turn = conversation_snapshot.current_turn
        if current_turn is None:
            raise AstraRuntimeError("Governed metadata context requires a current conversation turn.")
        capability = self._subscription_manager_capability_summary(adapter_capability_id)
        return self._metadata_context_issuer.issue(
            conversation_id=conversation_snapshot.metadata.conversation_id,
            current_turn_reference=current_turn.turn_id,
            request_reference=current_turn.request_reference,
            app_id=SUBSCRIPTION_MANAGER_APP_ID,
            capability_scope=SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
            capability_id=capability.adapter_capability_id,
            capability_version=capability.version,
            activation=self._activation,
            issued_at=requested_at,
            _runtime_authority=self._metadata_context_issuer_authority,
        )

    def validates_governed_metadata_context(
        self,
        context: Any,
        *,
        observed_at: datetime,
        conversation_id: str | None,
        current_turn_reference: str | None,
        request_reference: str | None,
        app_id: str | None,
        capability_scope: str | None,
        capability_id: str | None,
        capability_version: str | None,
    ) -> bool:
        if self._metadata_context_issuer is None or self._state is not AstraRuntimeState.READY:
            return False
        if None in (
            conversation_id,
            current_turn_reference,
            request_reference,
            app_id,
            capability_scope,
            capability_id,
            capability_version,
        ):
            return False
        return self._metadata_context_issuer.validates(
            context,
            observed_at=observed_at,
            conversation_id=conversation_id,
            current_turn_reference=current_turn_reference,
            request_reference=request_reference,
            app_id=app_id,
            capability_scope=capability_scope,
            capability_id=capability_id,
            capability_version=capability_version,
        )

    def intent_resolution_health(self, *, observed_at=None) -> AstraIntentHealthSnapshot:
        self._require_ready_component(self._intent_resolution, "intent resolution")
        result = self._intent_resolution.health(observed_at=observed_at)
        self._register_diagnostic_output(result)
        return result

    def authorize_read_access(
        self, request: AstraReadAuthorizationRequest, *, conversation_engine, conversation_snapshot, intent_resolution, plan=None
    ) -> AstraReadAuthorizationDecision:
        self._require_ready_component(self._read_access_authorization, "read access authorization")
        result = self._read_access_authorization.authorize(
            request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=plan,
        )
        self._register_diagnostic_output(result)
        if self._read_execution_bridge is not None:
            self._read_execution_bridge.register_read_authorization_decision(
                result,
                registration_authority=self._read_execution_registration_authority,
            )
        return result

    def read_access_authorization_health(self, *, observed_at=None) -> AstraReadAuthorizationHealth:
        self._require_ready_component(self._read_access_authorization, "read access authorization")
        result = self._read_access_authorization.health(observed_at=observed_at)
        self._register_diagnostic_output(result)
        return result

    def read_authority_capabilities(self) -> tuple[AstraReadAuthorityCapabilitySummary, ...]:
        self._require_ready_component(self._read_authority_binding, "read authority binding")
        return self._read_authority_binding.capabilities()

    def authorize_subscription_manager_read(self, **values: Any) -> AstraBoundReadAuthorization:
        self._require_ready_component(self._read_authority_binding, "read authority binding")
        return self._read_authority_binding.authorize_subscription_manager_read(**values)

    def issue_read_execution_request(self, **values: Any) -> AstraReadExecutionRequest:
        self._require_ready_component(self._read_execution_bridge, "read execution bridge")
        return self._read_execution_bridge.issue_request(**values)

    def execute_read(self, request: AstraReadExecutionRequest, *, db, authenticated_user) -> AstraReadExecutionResult:
        self._require_ready_component(self._read_execution_bridge, "read execution bridge")
        return self._read_execution_bridge.execute(request, db=db, authenticated_user=authenticated_user)

    def issue_diagnostic_projection_request(
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
        self._require_ready_component(self._diagnostic_projection, "diagnostic projection")
        return self._diagnostic_projection.issue_request(
            projection_request_id=projection_request_id,
            projection_kind=projection_kind,
            requested_sections=requested_sections,
            maximum_timeline_entries=maximum_timeline_entries,
            requested_redaction_posture=requested_redaction_posture,
            requested_at=requested_at,
            runtime_health=runtime_health,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=plan,
            read_authorization_decision=read_authorization_decision,
            evidence_references=evidence_references,
            component_health_snapshots=component_health_snapshots,
            conversation_engine=conversation_engine,
        )

    def create_diagnostic_projection(
        self, request: AstraDiagnosticProjectionRequest, *, created_at: datetime | None = None
    ) -> AstraDiagnosticProjection:
        self._require_ready_component(self._diagnostic_projection, "diagnostic projection")
        return self._diagnostic_projection.project(request, created_at=created_at)

    def diagnostic_projection_health(self, *, observed_at=None) -> AstraDiagnosticProjectionHealth:
        self._require_ready_component(self._diagnostic_projection, "diagnostic projection")
        return self._diagnostic_projection.health(observed_at=observed_at)

    def startup(self) -> AstraRuntimeHealthSnapshot:
        if self._state is not AstraRuntimeState.UNINITIALIZED:
            raise AstraRuntimeError("Runtime startup is allowed only from the uninitialized state.")

        self._transition_to(AstraRuntimeState.INITIALIZING)
        try:
            loaded_configuration = self._load_configuration()
            self._validate_configuration_boundary(loaded_configuration)
            startup_timestamp = loaded_configuration.provenance.loaded_at
            activation_issuer = self._create_activation_issuer()
            activation = self._load_activation(loaded_configuration, startup_timestamp, activation_issuer)
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
                certified_parent_reference="ASTRA-IMP-007 Certified / Approved",
                registered_at=startup_timestamp,
            )
            planning = self._create_planning_engine()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.PLANNING,
                component_type="AstraPlanningEngine",
                implementation_reference="ASTRA-IMP-008",
                certified_parent_reference="ASTRA-IMP-005/006/007 Certified / Approved",
                registered_at=startup_timestamp,
            )
            intent_resolution = self._create_intent_resolution_engine()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.INTENT_RESOLUTION,
                component_type="AstraIntentResolutionEngine",
                implementation_reference="ASTRA-IMP-009",
                certified_parent_reference="ASTRA-IMP-005 through ASTRA-IMP-008 Certified",
                registered_at=startup_timestamp,
            )
            read_authority_issuers = self._create_read_authority_issuers()
            read_access_authorization = self._create_read_access_authorization_engine(
                certified_issuers=read_authority_issuers,
            )
            read_authority_binding = self._create_read_authority_binding(read_access_authorization)
            read_execution_bridge = self._create_read_execution_bridge()
            metadata_context_issuer = self._create_governed_metadata_context_issuer()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.READ_ACCESS_AUTHORIZATION,
                component_type="AstraReadAccessAuthorizationEngine",
                implementation_reference="ASTRA-IMP-010",
                certified_parent_reference="ASTRA-IMP-001 through ASTRA-IMP-009 Certified",
                registered_at=startup_timestamp,
            )
            diagnostic_projection = self._create_diagnostic_projection_engine()
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.DIAGNOSTIC_PROJECTION,
                component_type="AstraDiagnosticProjectionEngine",
                implementation_reference="ASTRA-IMP-011",
                certified_parent_reference="ASTRA-IMP-001 through ASTRA-IMP-010 Certified",
                registered_at=startup_timestamp,
            )
            registry.seal()

            self._configuration = loaded_configuration
            self._activation = activation
            self._activation_issuer = activation_issuer
            self._metadata_context_issuer = metadata_context_issuer
            self._governance = evaluate_governance
            self._evidence_sink = evidence_sink
            self._capability_discovery = capability_discovery
            self._planning = planning
            self._intent_resolution = intent_resolution
            self._read_access_authorization = read_access_authorization
            self._read_authority_binding = read_authority_binding
            self._read_execution_bridge = read_execution_bridge
            self._diagnostic_projection = diagnostic_projection
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
        activation = (
            activation_snapshot(
                self._activation,
                runtime_instance_id=self._identity.startup_instance_id,
                environment_scope=self._configuration.configuration.environment_scope,
                observed_at=timestamp,
            )
            if self._configuration is not None
            else None
        )
        governance_available = self._governance is not None
        evidence_sink_available = self._evidence_sink is not None
        capability_discovery_available = self._capability_discovery is not None
        planning_available = self._planning is not None
        intent_resolution_available = self._intent_resolution is not None
        read_access_authorization_available = self._read_access_authorization is not None
        diagnostic_projection_available = self._diagnostic_projection is not None
        identifiers = self._registry.identifiers
        outcome = self._health_outcome(
            configuration_valid=configuration_valid,
            governance_available=governance_available,
            evidence_sink_available=evidence_sink_available,
            capability_discovery_available=capability_discovery_available,
            planning_available=planning_available,
            intent_resolution_available=intent_resolution_available,
            read_access_authorization_available=read_access_authorization_available,
            diagnostic_projection_available=diagnostic_projection_available,
            identifiers=identifiers,
        )
        result = AstraRuntimeHealthSnapshot(
            runtime_state=self._state,
            runtime_identity=self._identity,
            configuration_loaded=configuration_loaded,
            configuration_valid=configuration_valid,
            governance_available=governance_available,
            evidence_sink_available=evidence_sink_available,
            capability_discovery_available=capability_discovery_available,
            planning_available=planning_available,
            intent_resolution_available=intent_resolution_available,
            read_access_authorization_available=read_access_authorization_available,
            diagnostic_projection_available=diagnostic_projection_available,
            registered_component_identifiers=identifiers,
            startup_metadata=self._startup_metadata,
            activation=activation,
            environment_scope=self._startup_metadata.environment_scope if self._startup_metadata is not None else None,
            production_authorization_state=(
                self._startup_metadata.production_authorization_state if self._startup_metadata is not None else None
            ),
            health_outcome=outcome,
            fault=self._fault,
            health_timestamp=timestamp,
        )
        self._register_diagnostic_output(result)
        return result

    def _load_configuration(self) -> LoadedAstraConfiguration:
        return get_astra_configuration()

    def _load_activation(
        self,
        loaded_configuration: LoadedAstraConfiguration,
        loaded_at: datetime,
        activation_issuer: AstraRuntimeActivationIssuer,
    ) -> AstraRuntimeActivationContract | None:
        return load_runtime_activation(
            runtime_instance_id=self._identity.startup_instance_id,
            environment_scope=loaded_configuration.configuration.environment_scope,
            loaded_at=loaded_at,
            activation_issuer=activation_issuer,
            activation_issue_authority=self._activation_issuer_authority,
        )

    def _create_activation_issuer(self) -> AstraRuntimeActivationIssuer:
        return AstraRuntimeActivationIssuer(
            runtime_instance_id=self._identity.startup_instance_id,
            issuer_reference="runtime-activation:astra-runtime-act-001",
            _runtime_authority=self._activation_issuer_authority,
            _runtime_owner=self,
        )

    def _create_evidence_sink(self, loaded_configuration: LoadedAstraConfiguration) -> InMemoryEvidenceSink:
        return InMemoryEvidenceSink(
            capacity=self._evidence_sink_capacity,
            loaded_configuration=loaded_configuration,
        )

    def _create_capability_discovery_engine(self) -> AstraCapabilityDiscoveryEngine:
        return AstraCapabilityDiscoveryEngine(runtime=self)

    def _create_planning_engine(self) -> AstraPlanningEngine:
        return AstraPlanningEngine(runtime=self)

    def _create_intent_resolution_engine(self) -> AstraIntentResolutionEngine:
        return AstraIntentResolutionEngine(runtime=self)

    def _create_read_access_authorization_engine(
        self,
        *,
        certified_issuers: dict[str, AstraAuthorityProofIssuer] | None = None,
    ) -> AstraReadAccessAuthorizationEngine:
        return AstraReadAccessAuthorizationEngine(
            runtime=self,
            registry=certified_subscription_manager_read_registry(),
            certified_issuers=certified_issuers,
        )

    def _create_read_authority_binding(
        self,
        read_access_authorization: AstraReadAccessAuthorizationEngine,
    ) -> AstraReadAuthorityBinding:
        return AstraReadAuthorityBinding(
            runtime=self,
            read_access_authorization=read_access_authorization,
            read_capability_registry=certified_subscription_manager_read_registry(),
        )

    def _create_read_authority_issuers(self) -> dict[str, AstraAuthorityProofIssuer]:
        issuers = create_runtime_read_authority_issuers(
            runtime=self,
            issuer_authority=self._read_issuer_authority,
        )
        for proof_class, issuer in issuers.items():
            if proof_class in self._read_authority_issuers:
                raise AstraRuntimeError("Read authority issuer class is already registered.")
            self._read_authority_issuers[proof_class] = issuer
        return issuers

    def _create_read_execution_bridge(self) -> AstraReadExecutionBridge:
        return AstraReadExecutionBridge(
            runtime=self,
            registration_authority=self._read_execution_registration_authority,
            request_authority=self._read_execution_request_authority,
        )

    def _create_governed_metadata_context_issuer(self) -> AstraGovernedMetadataContextIssuer:
        return AstraGovernedMetadataContextIssuer(
            runtime_instance_id=self._identity.startup_instance_id,
            issuer_reference="runtime-metadata-context:astra-meta-act-bind-001",
            _runtime_authority=self._metadata_context_issuer_authority,
            _runtime_owner=self,
        )

    def _create_diagnostic_projection_engine(self) -> AstraDiagnosticProjectionEngine:
        return AstraDiagnosticProjectionEngine(
            runtime=self,
            registration_authority=self._diagnostic_output_registration_authority,
        )

    def _register_diagnostic_output(self, value: Any) -> None:
        if self._diagnostic_projection is not None and self._state is AstraRuntimeState.READY:
            self._diagnostic_projection._register_runtime_output(
                value,
                registration_authority=self._diagnostic_output_registration_authority,
            )

    def _issue_read_authority_issuer(
        self, proof_class: str, issuer_reference: str, *, capacity: int = 100
    ) -> AstraAuthorityProofIssuer:
        """Internal bridge reserved for a future certified authority component."""
        self._require_ready_component(self._read_access_authorization, "read access authorization")
        if proof_class in self._read_authority_issuers:
            raise AstraRuntimeError("Read authority issuer class is already registered.")
        issuer = AstraAuthorityProofIssuer(
            runtime_instance_id=self._identity.startup_instance_id,
            issuer_reference=issuer_reference,
            capacity=capacity,
            _runtime_authority=self._read_issuer_authority,
        )
        self._read_authority_issuers[proof_class] = issuer
        return issuer

    def _validates_read_authority_issuer(self, proof_class: str, issuer: Any) -> bool:
        return (
            self._state in {AstraRuntimeState.INITIALIZING, AstraRuntimeState.READY}
            and isinstance(issuer, AstraAuthorityProofIssuer)
            and issuer._runtime_authority is self._read_issuer_authority
            and self._read_authority_issuers.get(proof_class) is issuer
        )

    def _validates_activation_issuer(self, issuer: Any) -> bool:
        return (
            self._state is AstraRuntimeState.READY
            and isinstance(issuer, AstraRuntimeActivationIssuer)
            and issuer._runtime_authority is self._activation_issuer_authority
            and self._activation_issuer is issuer
            and self._activation is not None
        )

    def _validates_metadata_context_issuer(self, issuer: Any) -> bool:
        return (
            self._state is AstraRuntimeState.READY
            and isinstance(issuer, AstraGovernedMetadataContextIssuer)
            and issuer._runtime_authority is self._metadata_context_issuer_authority
            and self._metadata_context_issuer is issuer
            and self._activation is not None
        )

    def _subscription_manager_capability_summary(self, adapter_capability_id: str) -> AstraReadAuthorityCapabilitySummary:
        for capability in self.read_authority_capabilities():
            if (
                capability.owning_app_id == SUBSCRIPTION_MANAGER_APP_ID
                and capability.adapter_capability_id == adapter_capability_id
            ):
                return capability
        raise AstraRuntimeError("Governed metadata context requires a certified Subscription Manager capability.")

    def _validate_governed_metadata_conversation(self, conversation_engine: Any, conversation_snapshot: Any) -> None:
        from app.modules.astra_ai.conversation_context import (
            AstraConversationContextEngine,
            AstraConversationLifecycleState,
            AstraConversationSnapshot,
        )

        if not isinstance(conversation_engine, AstraConversationContextEngine):
            raise AstraRuntimeError("Governed metadata context requires certified Conversation Context.")
        if not isinstance(conversation_snapshot, AstraConversationSnapshot):
            raise AstraRuntimeError("Governed metadata context requires a certified conversation snapshot.")
        if conversation_snapshot.metadata.runtime_instance_id != self._identity.startup_instance_id:
            raise AstraRuntimeError("Governed metadata context conversation belongs to a foreign Runtime.")
        if conversation_snapshot.current_turn is None:
            raise AstraRuntimeError("Governed metadata context requires a current turn.")
        if conversation_snapshot.metadata.lifecycle_state is not AstraConversationLifecycleState.ACTIVE:
            raise AstraRuntimeError("Governed metadata context requires an active conversation.")
        try:
            owned_snapshot = conversation_engine.get_conversation(conversation_snapshot.metadata.conversation_id)
        except Exception as exc:
            raise AstraRuntimeError("Governed metadata context conversation is not Runtime-owned.") from exc
        if owned_snapshot != conversation_snapshot:
            raise AstraRuntimeError("Governed metadata context conversation snapshot is stale or fabricated.")

    def _transition_to(self, next_state: AstraRuntimeState) -> None:
        if next_state not in ALLOWED_RUNTIME_TRANSITIONS[self._state]:
            raise AstraRuntimeError("Runtime lifecycle transition is not authorized.")
        self._state = next_state

    def _clear_owned_components(self) -> None:
        if self._activation_issuer is not None:
            self._activation_issuer.invalidate()
        if self._metadata_context_issuer is not None:
            self._metadata_context_issuer.invalidate()
        self._configuration = None
        self._activation = None
        self._activation_issuer = None
        self._metadata_context_issuer = None
        self._governance = None
        self._evidence_sink = None
        self._capability_discovery = None
        self._planning = None
        self._intent_resolution = None
        self._read_access_authorization = None
        self._read_authority_binding = None
        self._read_execution_bridge = None
        self._diagnostic_projection = None
        self._read_authority_issuers = {}
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
        planning_available: bool,
        intent_resolution_available: bool,
        read_access_authorization_available: bool,
        diagnostic_projection_available: bool,
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
            and planning_available
            and intent_resolution_available
            and read_access_authorization_available
            and diagnostic_projection_available
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
