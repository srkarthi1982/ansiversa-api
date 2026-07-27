from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION
from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    ProductionAuthorizationState,
    SafetyClassification,
    assert_no_prohibited_contract_material,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeHealthOutcome, AstraRuntimeState


CONVERSATION_CONTEXT_ENGINE_VERSION = "1.0.0"
CONVERSATION_CONTEXT_IMPLEMENTATION_REFERENCE = "ASTRA-IMP-006"
DEFAULT_SHORT_CONTEXT_LIMIT = 8
MAXIMUM_DECLARED_INTENT_BINDINGS = 200


class AstraConversationContextError(ValueError):
    """Raised when conversation context cannot satisfy its bounded lifecycle contract."""


class AstraConversationLifecycleState(StrEnum):
    CREATED = "created"
    ACTIVE = "active"
    IDLE = "idle"
    CLOSING = "closing"
    CLOSED = "closed"
    FAULTED = "faulted"


class AstraConversationHealthOutcome(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAULTED = "faulted"


class AstraConversationTurnKind(StrEnum):
    USER_REQUEST = "user_request"
    SYSTEM_CONTEXT = "system_context"
    CLARIFICATION = "clarification"


class AstraConversationHistoryKind(StrEnum):
    TURN_RECORDED = "turn_recorded"
    STATE_TRANSITION = "state_transition"
    CONTEXT_REFRESH = "context_refresh"


ALLOWED_CONVERSATION_TRANSITIONS = {
    AstraConversationLifecycleState.CREATED: (
        AstraConversationLifecycleState.ACTIVE,
        AstraConversationLifecycleState.CLOSING,
        AstraConversationLifecycleState.FAULTED,
    ),
    AstraConversationLifecycleState.ACTIVE: (
        AstraConversationLifecycleState.IDLE,
        AstraConversationLifecycleState.CLOSING,
        AstraConversationLifecycleState.FAULTED,
    ),
    AstraConversationLifecycleState.IDLE: (
        AstraConversationLifecycleState.ACTIVE,
        AstraConversationLifecycleState.CLOSING,
        AstraConversationLifecycleState.FAULTED,
    ),
    AstraConversationLifecycleState.CLOSING: (
        AstraConversationLifecycleState.CLOSED,
        AstraConversationLifecycleState.FAULTED,
    ),
    AstraConversationLifecycleState.CLOSED: (),
    AstraConversationLifecycleState.FAULTED: (AstraConversationLifecycleState.CLOSING,),
}


class _ConversationOwnershipToken:
    def __init__(self, runtime_instance_id: str) -> None:
        self.runtime_instance_id = runtime_instance_id


class _DeclaredIntentAuthorityToken:
    pass


class AstraBoundDeclaredIntentParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z][a-z0-9_]{1,60}$")
    value_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")


class AstraDeclaredIntentBinding(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    binding_id: str = Field(pattern=r"^intent_binding_[0-9]{8}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    current_turn_reference: str = Field(pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")
    request_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    declared_action: str = Field(pattern=r"^[a-z][a-z0-9_]{1,60}$")
    declared_subject: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{1,100}$")
    declared_target: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.:-]{1,100}$")
    declared_parameters: tuple[AstraBoundDeclaredIntentParameter, ...] = Field(default_factory=tuple, max_length=12)
    authority_token: Any = Field(exclude=True)

    @model_validator(mode="after")
    def validate_binding(self):
        names = tuple(item.name for item in self.declared_parameters)
        if len(names) != len(set(names)):
            raise AstraConversationContextError("Declared intent binding parameter names must be unique.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraConversationMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    created_at: datetime
    last_activity_at: datetime
    conversation_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    implementation_reference: str = Field(pattern=r"^ASTRA-IMP-006$")
    lifecycle_state: AstraConversationLifecycleState

    @model_validator(mode="after")
    def validate_metadata(self):
        _ensure_timezone_aware(self.created_at, "Conversation creation timestamp")
        _ensure_timezone_aware(self.last_activity_at, "Conversation last activity timestamp")
        if self.last_activity_at < self.created_at:
            raise AstraConversationContextError("Conversation activity cannot precede creation.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraCurrentTurnContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    turn_id: str = Field(pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")
    received_at: datetime
    request_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    turn_kind: AstraConversationTurnKind
    route_reference: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    context_references: tuple[str, ...] = Field(default_factory=tuple, max_length=12)

    @model_validator(mode="after")
    def validate_turn(self):
        _ensure_timezone_aware(self.received_at, "Conversation turn timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraShortContextEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_id: str = Field(pattern=r"^ctx_[a-z0-9][a-z0-9_-]{7,120}$")
    recorded_at: datetime
    history_kind: AstraConversationHistoryKind
    summary_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    lifecycle_state: AstraConversationLifecycleState
    turn_id: str | None = Field(default=None, pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")

    @model_validator(mode="after")
    def validate_entry(self):
        _ensure_timezone_aware(self.recorded_at, "Conversation history timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraConversationHealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    runtime_state: AstraRuntimeState
    runtime_health_outcome: AstraRuntimeHealthOutcome
    conversation_count: int = Field(ge=0)
    active_count: int = Field(ge=0)
    idle_count: int = Field(ge=0)
    closed_count: int = Field(ge=0)
    faulted_count: int = Field(ge=0)
    short_context_limit: int = Field(ge=1, le=50)
    health_outcome: AstraConversationHealthOutcome
    observed_at: datetime

    @model_validator(mode="after")
    def validate_health(self):
        _ensure_timezone_aware(self.observed_at, "Conversation health timestamp")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class AstraConversationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metadata: AstraConversationMetadata
    current_turn: AstraCurrentTurnContext | None = None
    short_context: tuple[AstraShortContextEntry, ...] = Field(default_factory=tuple, max_length=50)

    @model_validator(mode="after")
    def validate_snapshot(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class _PreparedConversationMutation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metadata: AstraConversationMetadata
    current_turn: AstraCurrentTurnContext | None = None
    history: tuple[AstraShortContextEntry, ...] = Field(default_factory=tuple, max_length=50)

    @model_validator(mode="after")
    def validate_prepared_mutation(self):
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


class _AstraConversationSession:
    def __init__(
        self,
        *,
        metadata: AstraConversationMetadata,
        short_context_limit: int,
        ownership_token: _ConversationOwnershipToken,
    ) -> None:
        if ownership_token.runtime_instance_id != metadata.runtime_instance_id:
            raise AstraConversationContextError("Conversation ownership token does not match runtime identity.")
        if short_context_limit < 1 or short_context_limit > 50:
            raise AstraConversationContextError("Short-context limit must be between one and fifty entries.")
        self._metadata = metadata
        self._current_turn: AstraCurrentTurnContext | None = None
        self._short_context_limit = short_context_limit
        self._history: list[AstraShortContextEntry] = []

    @property
    def metadata(self) -> AstraConversationMetadata:
        return self._metadata

    @property
    def current_turn(self) -> AstraCurrentTurnContext | None:
        return deepcopy(self._current_turn)

    @property
    def short_context(self) -> tuple[AstraShortContextEntry, ...]:
        return tuple(deepcopy(self._history))

    def snapshot(self) -> AstraConversationSnapshot:
        return AstraConversationSnapshot(
            metadata=self._metadata,
            current_turn=deepcopy(self._current_turn),
            short_context=tuple(deepcopy(self._history)),
        )

    def prepare_transition(
        self,
        next_state: AstraConversationLifecycleState,
        *,
        transitioned_at: datetime,
        summary_reference: str,
        entry_id: str,
    ) -> _PreparedConversationMutation:
        if next_state not in ALLOWED_CONVERSATION_TRANSITIONS[self._metadata.lifecycle_state]:
            raise AstraConversationContextError("Conversation lifecycle transition is not authorized.")
        if transitioned_at < self._metadata.last_activity_at:
            raise AstraConversationContextError("Conversation lifecycle timestamps must be monotonic.")
        metadata = AstraConversationMetadata(
            **{
                **self._metadata.model_dump(),
                "lifecycle_state": next_state,
                "last_activity_at": transitioned_at,
            }
        )
        history = self._bounded_history_with(
            AstraShortContextEntry(
                entry_id=entry_id,
                recorded_at=transitioned_at,
                history_kind=AstraConversationHistoryKind.STATE_TRANSITION,
                summary_reference=summary_reference,
                lifecycle_state=next_state,
            )
        )
        return _PreparedConversationMutation(
            metadata=metadata,
            current_turn=self._current_turn,
            history=history,
        )

    def prepare_current_turn(
        self,
        turn: AstraCurrentTurnContext,
        *,
        history_entry_id: str,
        summary_reference: str,
    ) -> _PreparedConversationMutation:
        if self._metadata.lifecycle_state in {
            AstraConversationLifecycleState.CLOSING,
            AstraConversationLifecycleState.CLOSED,
            AstraConversationLifecycleState.FAULTED,
        }:
            raise AstraConversationContextError("Conversation cannot record turns after closing, closed, or faulted state.")
        if turn.received_at < self._metadata.last_activity_at:
            raise AstraConversationContextError("Conversation turn timestamps must be monotonic.")
        metadata = AstraConversationMetadata(
            **{
                **self._metadata.model_dump(),
                "lifecycle_state": AstraConversationLifecycleState.ACTIVE,
                "last_activity_at": turn.received_at,
            }
        )
        history = self._bounded_history_with(
            AstraShortContextEntry(
                entry_id=history_entry_id,
                recorded_at=turn.received_at,
                history_kind=AstraConversationHistoryKind.TURN_RECORDED,
                summary_reference=summary_reference,
                lifecycle_state=metadata.lifecycle_state,
                turn_id=turn.turn_id,
            )
        )
        return _PreparedConversationMutation(
            metadata=metadata,
            current_turn=turn,
            history=history,
        )

    def commit(self, mutation: _PreparedConversationMutation) -> AstraConversationSnapshot:
        self._metadata = mutation.metadata
        self._current_turn = deepcopy(mutation.current_turn)
        self._history = list(deepcopy(mutation.history))
        return self.snapshot()

    def _bounded_history_with(self, entry: AstraShortContextEntry) -> tuple[AstraShortContextEntry, ...]:
        history = [*self._history, entry]
        overflow = len(history) - self._short_context_limit
        if overflow > 0:
            del history[:overflow]
        return tuple(history)


class AstraConversationContextEngine:
    def __init__(self, *, runtime: AstraRuntime, short_context_limit: int = DEFAULT_SHORT_CONTEXT_LIMIT) -> None:
        self._require_ready_runtime(runtime)
        if short_context_limit < 1 or short_context_limit > 50:
            raise AstraConversationContextError("Short-context limit must be between one and fifty entries.")
        self._runtime = runtime
        self._short_context_limit = short_context_limit
        self._ownership_token = _ConversationOwnershipToken(runtime.identity.startup_instance_id)
        self._declared_intent_authority_token = _DeclaredIntentAuthorityToken()
        self._declared_intent_bindings: dict[str, AstraDeclaredIntentBinding] = {}
        self._declared_intent_binding_sequence = 0
        self._conversations: dict[str, _AstraConversationSession] = {}
        self._operation_sequence = 0

    def create_conversation(
        self,
        *,
        conversation_id: str,
        created_at: datetime,
    ) -> AstraConversationSnapshot:
        self._require_runtime_ready()
        if conversation_id in self._conversations:
            raise AstraConversationContextError("Conversation identifier already exists for this runtime.")
        metadata = AstraConversationMetadata(
            conversation_id=conversation_id,
            runtime_instance_id=self._runtime.identity.startup_instance_id,
            created_at=created_at,
            last_activity_at=created_at,
            conversation_version=CONVERSATION_CONTEXT_ENGINE_VERSION,
            implementation_reference=CONVERSATION_CONTEXT_IMPLEMENTATION_REFERENCE,
            lifecycle_state=AstraConversationLifecycleState.CREATED,
        )
        session = _AstraConversationSession(
            metadata=metadata,
            short_context_limit=self._short_context_limit,
            ownership_token=self._ownership_token,
        )
        self._emit_governance_evidence("CONV-CREATE", created_at)
        self._conversations[conversation_id] = session
        return session.snapshot()

    def get_conversation(self, conversation_id: str) -> AstraConversationSnapshot:
        self._require_runtime_ready()
        return self._conversation(conversation_id).snapshot()

    def issue_declared_intent_binding(
        self,
        *,
        conversation_snapshot: AstraConversationSnapshot,
        declared_action: str,
        declared_subject: str | None = None,
        declared_target: str | None = None,
        declared_parameters: tuple[AstraBoundDeclaredIntentParameter, ...] = (),
    ) -> AstraDeclaredIntentBinding:
        self._require_runtime_ready()
        owned = self.get_conversation(conversation_snapshot.metadata.conversation_id)
        if owned != conversation_snapshot:
            raise AstraConversationContextError("Declared intent binding requires the current owned snapshot.")
        if owned.current_turn is None:
            raise AstraConversationContextError("Declared intent binding requires a current turn.")
        if owned.metadata.lifecycle_state is not AstraConversationLifecycleState.ACTIVE:
            raise AstraConversationContextError("Declared intent binding requires an active conversation.")
        if len(self._declared_intent_bindings) >= MAXIMUM_DECLARED_INTENT_BINDINGS:
            raise AstraConversationContextError("Declared intent binding capacity is exhausted.")
        next_sequence = self._declared_intent_binding_sequence + 1
        binding = AstraDeclaredIntentBinding(
            binding_id=f"intent_binding_{next_sequence:08d}",
            runtime_instance_id=self._runtime.identity.startup_instance_id,
            conversation_id=owned.metadata.conversation_id,
            current_turn_reference=owned.current_turn.turn_id,
            request_reference=owned.current_turn.request_reference,
            declared_action=declared_action,
            declared_subject=declared_subject,
            declared_target=declared_target,
            declared_parameters=declared_parameters,
            authority_token=self._declared_intent_authority_token,
        )
        self._declared_intent_bindings[binding.binding_id] = binding
        self._declared_intent_binding_sequence = next_sequence
        return binding

    def validates_declared_intent_binding(self, binding: AstraDeclaredIntentBinding) -> bool:
        issued = (
            self._declared_intent_bindings.get(binding.binding_id)
            if isinstance(binding, AstraDeclaredIntentBinding)
            else None
        )
        return (
            isinstance(binding, AstraDeclaredIntentBinding)
            and issued is binding
            and binding.authority_token is self._declared_intent_authority_token
            and binding.runtime_instance_id == self._runtime.identity.startup_instance_id
        )

    def transition_conversation(
        self,
        conversation_id: str,
        next_state: AstraConversationLifecycleState,
        *,
        transitioned_at: datetime,
        summary_reference: str,
        entry_id: str,
    ) -> AstraConversationMetadata:
        self._require_runtime_ready()
        session = self._conversation(conversation_id)
        mutation = session.prepare_transition(
            next_state,
            transitioned_at=transitioned_at,
            summary_reference=summary_reference,
            entry_id=entry_id,
        )
        self._emit_governance_evidence("CONV-STATE", transitioned_at)
        return session.commit(mutation).metadata

    def record_current_turn(
        self,
        conversation_id: str,
        turn: AstraCurrentTurnContext,
        *,
        history_entry_id: str,
        summary_reference: str,
    ) -> AstraConversationMetadata:
        self._require_runtime_ready()
        session = self._conversation(conversation_id)
        mutation = session.prepare_current_turn(
            turn,
            history_entry_id=history_entry_id,
            summary_reference=summary_reference,
        )
        self._emit_governance_evidence("CONV-TURN", turn.received_at)
        return session.commit(mutation).metadata

    def health(self, *, observed_at: datetime | None = None) -> AstraConversationHealthSnapshot:
        observed = observed_at or _utc_now()
        runtime_health = self._runtime.health(observed_at=observed)
        states = tuple(session.metadata.lifecycle_state for session in self._conversations.values())
        health_outcome = self._conversation_health_outcome(runtime_health)
        return AstraConversationHealthSnapshot(
            runtime_instance_id=self._runtime.identity.startup_instance_id,
            runtime_state=runtime_health.runtime_state,
            runtime_health_outcome=runtime_health.health_outcome,
            conversation_count=len(states),
            active_count=states.count(AstraConversationLifecycleState.ACTIVE),
            idle_count=states.count(AstraConversationLifecycleState.IDLE),
            closed_count=states.count(AstraConversationLifecycleState.CLOSED),
            faulted_count=states.count(AstraConversationLifecycleState.FAULTED),
            short_context_limit=self._short_context_limit,
            health_outcome=health_outcome,
            observed_at=observed,
        )

    def _conversation(self, conversation_id: str) -> _AstraConversationSession:
        try:
            return self._conversations[conversation_id]
        except KeyError as exc:
            raise AstraConversationContextError("Conversation identifier is not owned by this runtime.") from exc

    def _emit_governance_evidence(self, operation_prefix: str, timestamp: datetime) -> None:
        operation_sequence = self._operation_sequence + 1
        result = self._runtime.evaluate_governance(
            GovernanceEvaluationInput(
                evaluation_id=f"{operation_prefix}-{operation_sequence:03d}",
                requirement_references=(
                    ConstitutionalRequirementReference(
                        constitutional_source="ASTRA-003",
                        requirement_id="AIR-CTX-003",
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

    def _require_runtime_ready(self) -> None:
        self._require_ready_runtime(self._runtime)

    def _require_ready_runtime(self, runtime: AstraRuntime) -> None:
        if runtime.state is not AstraRuntimeState.READY:
            raise AstraConversationContextError("Conversation Context Engine requires a ready AstraRuntime owner.")

    def _conversation_health_outcome(self, runtime_health) -> AstraConversationHealthOutcome:
        if runtime_health.health_outcome is AstraRuntimeHealthOutcome.FAULTED:
            return AstraConversationHealthOutcome.FAULTED
        if runtime_health.health_outcome is not AstraRuntimeHealthOutcome.HEALTHY:
            return AstraConversationHealthOutcome.STOPPED
        if any(session.metadata.lifecycle_state is AstraConversationLifecycleState.FAULTED for session in self._conversations.values()):
            return AstraConversationHealthOutcome.DEGRADED
        return AstraConversationHealthOutcome.HEALTHY


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone_aware(timestamp: datetime, field_name: str) -> None:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise AstraConversationContextError(f"{field_name} must be timezone-aware.")
