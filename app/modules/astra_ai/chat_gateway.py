from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.astra_ai.conversation_context import (
    AstraBoundDeclaredIntentParameter,
    AstraConversationContextEngine,
    AstraConversationContextError,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.constitutional_contracts import (
    ConstitutionalRequirementReference,
    FailurePosture,
    GovernanceOutcome,
)
from app.modules.astra_ai.intent_resolution import (
    AstraDeclaredIntentParameter,
    AstraIntentRequest,
    AstraIntentResolution,
    AstraIntentStatus,
)
from app.modules.astra_ai.read_access_authorization import AstraReadPurpose
from app.modules.astra_ai.read_authority_binding import AstraReadAuthorityBindingError
from app.modules.astra_ai.read_execution import AstraReadExecutionError, AstraReadExecutionResult
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError, AstraRuntimeState
from app.modules.auth.service import AuthenticatedUserContext, validates_authenticated_user_context
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import SubscriptionAstraParameter


ASTRA_CHAT_IMPLEMENTATION_REFERENCE = "ASTRA-CHAT-001"
ASTRA_CHAT_VERSION = "1.0.0"
SUBSCRIPTION_MANAGER_APP_ID = "subscription_manager"
SUPPORTED_SUBSCRIPTION_CAPABILITIES = tuple(
    definition.capability_id for definition in subscription_reads.capability_catalog()
)
MAX_CHAT_CONVERSATIONS = 200


class AstraChatGatewayError(ValueError):
    """Raised when the governed chat gateway cannot preserve its boundary."""


class AstraChatStatus(StrEnum):
    OK = "ok"
    CLARIFICATION_REQUIRED = "clarification_required"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    DENIED = "denied"
    ERROR = "error"


class AstraChatResponseKind(StrEnum):
    SUBSCRIPTION_READ_RESULT = "subscription_read_result"
    CLARIFICATION = "clarification"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    GOVERNED_DENIAL = "governed_denial"
    MALFORMED_REQUEST = "malformed_request"


class AstraChatDeclaredParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Literal["days", "status", "category"]
    value: int | str = Field(union_mode="left_to_right")


class AstraChatDeclaredIntent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    app_id: str = Field(default=SUBSCRIPTION_MANAGER_APP_ID, min_length=3, max_length=80)
    declared_action: str = Field(default="get_information", pattern=r"^[a-z][a-z0-9_]{1,60}$")
    declared_subject: str | None = Field(default="subscription", pattern=r"^[a-z][a-z0-9_.:-]{1,100}$")
    capability_id: str | None = Field(default=None, min_length=3, max_length=120)
    parameters: tuple[AstraChatDeclaredParameter, ...] = Field(default_factory=tuple, max_length=12)

    @field_validator("parameters")
    @classmethod
    def validate_unique_parameters(cls, value):
        names = tuple(parameter.name for parameter in value)
        if len(names) != len(set(names)):
            raise ValueError("Declared intent parameter names must be unique.")
        return value


class AstraChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    conversation_id: str | None = Field(default=None, pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    declared_intent: AstraChatDeclaredIntent | None = None
    requested_field_references: tuple[str, ...] | None = Field(default=None, max_length=50)
    requested_row_limit: int | None = Field(default=None, ge=1, le=100)
    client_request_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )

    @field_validator("requested_field_references")
    @classmethod
    def validate_unique_fields(cls, value):
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Requested field references must be unique.")
        return value


class AstraChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    conversation_id: str
    turn_id: str
    status: AstraChatStatus
    resolved_intent: str | None = None
    capability_id: str | None = None
    response_kind: AstraChatResponseKind
    message: str = Field(min_length=1, max_length=240)
    structured_result: dict[str, Any] | None = None
    reason_codes: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    clarification_required: bool
    evidence_references: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    authorization_decision_reference: str | None = Field(default=None, min_length=8, max_length=160)
    governance_decision_reference: str | None = Field(default=None, min_length=8, max_length=160)
    production_authorization_state: Literal["not_approved"] = "not_approved"
    observed_at: datetime
    version: str = ASTRA_CHAT_VERSION

    @model_validator(mode="after")
    def validate_response(self) -> "AstraChatResponse":
        _ensure_aware(self.observed_at, "Chat response")
        _validate_safe_payload(self.model_dump(mode="json"))
        return self


class AstraChatGateway:
    """Backend-only orchestrator for declared-intent governed chat reads."""

    def __init__(self, *, runtime: AstraRuntime) -> None:
        if not isinstance(runtime, AstraRuntime) or runtime.state is not AstraRuntimeState.READY:
            raise AstraChatGatewayError("Astra chat gateway requires a ready certified Runtime.")
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._conversation_engine = AstraConversationContextEngine(runtime=runtime)
        self._conversation_principals: dict[str, str] = {}
        self._turn_sequence = 0
        self._execution_sequence = 0

    @property
    def runtime(self) -> AstraRuntime:
        return self._runtime

    def handle(
        self,
        request: AstraChatRequest,
        *,
        authenticated_context: AuthenticatedUserContext,
        subscription_manager_db: Any,
        observed_at: datetime | None = None,
    ) -> AstraChatResponse:
        timestamp = observed_at or _utc_now()
        _ensure_aware(timestamp, "Chat request")
        if not validates_authenticated_user_context(authenticated_context, observed_at=timestamp):
            return self._bounded_failure(
                conversation_id=request.conversation_id or _fallback_conversation_id(timestamp),
                turn_id=_fallback_turn_id(timestamp),
                status=AstraChatStatus.DENIED,
                response_kind=AstraChatResponseKind.GOVERNED_DENIAL,
                message="The authenticated chat context is not authorized.",
                reason_codes=("authentication_context_invalid",),
                observed_at=timestamp,
            )
        try:
            conversation_id, turn_id = self._prepare_turn(request, authenticated_context, timestamp)
        except AstraChatGatewayError:
            return self._bounded_failure(
                conversation_id=request.conversation_id or _fallback_conversation_id(timestamp),
                turn_id=_fallback_turn_id(timestamp),
                status=AstraChatStatus.DENIED,
                response_kind=AstraChatResponseKind.GOVERNED_DENIAL,
                message="The chat conversation is not authorized for this principal.",
                reason_codes=("foreign_or_stale_conversation",),
                observed_at=timestamp,
            )

        declared = request.declared_intent
        if declared is None:
            return self._bounded_failure(
                conversation_id=conversation_id,
                turn_id=turn_id,
                status=AstraChatStatus.CLARIFICATION_REQUIRED,
                response_kind=AstraChatResponseKind.CLARIFICATION,
                message="Please choose a supported Subscription Manager intent.",
                reason_codes=("declared_intent_required", "natural_language_inference_not_enabled"),
                observed_at=timestamp,
            )
        if declared.app_id != SUBSCRIPTION_MANAGER_APP_ID:
            return self._unavailable(conversation_id, turn_id, "unsupported_app", timestamp)
        if declared.capability_id not in SUPPORTED_SUBSCRIPTION_CAPABILITIES:
            return self._unavailable(conversation_id, turn_id, "unsupported_capability", timestamp)

        try:
            snapshot = self._conversation_engine.get_conversation(conversation_id)
            requester_context = self._runtime.capability_discovery.internal_request_context()
            intent_resolution = self._resolve_declared_intent(
                declared,
                conversation_snapshot=snapshot,
                requester_context=requester_context,
                observed_at=timestamp,
            )
            if intent_resolution.intent_status is not AstraIntentStatus.RESOLVED:
                return self._intent_non_success(
                    conversation_id=conversation_id,
                    turn_id=turn_id,
                    intent_resolution=intent_resolution,
                    observed_at=timestamp,
                )
            bound = self._runtime.read_authority.authorize_subscription_manager_read(
                authenticated_context=authenticated_context,
                conversation_engine=self._conversation_engine,
                conversation_snapshot=snapshot,
                intent_resolution=intent_resolution,
                adapter_capability_id=declared.capability_id,
                requested_field_references=request.requested_field_references,
                requested_row_limit=request.requested_row_limit,
                parameters=_subscription_parameters(declared.parameters),
                requested_at=timestamp,
            )
            execution_request = self._runtime.read_execution.issue_request(
                execution_request_id=self._execution_request_id(timestamp),
                read_authorization_decision=bound.authorization_decision,
                app_read_grant=bound.app_read_grant,
                authenticated_principal_reference=bound.authenticated_principal_reference,
                request_reference=bound.request_reference,
                requested_maximum_result_count=bound.maximum_result_count,
                requested_at=timestamp,
                adapter_capability_id=bound.adapter_capability_id,
                adapter_capability_version=bound.adapter_capability_version,
            )
            result = self._runtime.read_execution.execute(
                execution_request,
                db=subscription_manager_db,
                authenticated_user=authenticated_context.authenticated_user,
            )
        except (
            AstraChatGatewayError,
            AstraConversationContextError,
            AstraReadAuthorityBindingError,
            AstraReadExecutionError,
            AstraRuntimeError,
            RuntimeError,
            ValueError,
        ):
            return self._bounded_failure(
                conversation_id=conversation_id,
                turn_id=turn_id,
                status=AstraChatStatus.DENIED,
                response_kind=AstraChatResponseKind.GOVERNED_DENIAL,
                message="The governed read request was denied.",
                reason_codes=("governed_read_denied",),
                observed_at=timestamp,
            )

        structured = _structured_result(result)
        return AstraChatResponse(
            conversation_id=conversation_id,
            turn_id=turn_id,
            status=AstraChatStatus.OK,
            resolved_intent=intent_resolution.intent_id,
            capability_id=declared.capability_id,
            response_kind=AstraChatResponseKind.SUBSCRIPTION_READ_RESULT,
            message=_message(result),
            structured_result=structured,
            reason_codes=tuple(_bounded_reason_codes((*result.reason_codes, "astra_chat_orchestration"))),
            clarification_required=False,
            evidence_references=tuple(
                _bounded_references((*intent_resolution.evidence_references, *result.evidence_references))
            ),
            authorization_decision_reference=bound.authorization_decision.authorization_decision_id,
            governance_decision_reference=bound.authorization_decision.governance_decision_reference,
            observed_at=timestamp,
        )

    def _prepare_turn(
        self,
        request: AstraChatRequest,
        authenticated_context: AuthenticatedUserContext,
        timestamp: datetime,
    ) -> tuple[str, str]:
        principal_reference = authenticated_context.authenticated_principal_reference
        if request.conversation_id is None:
            if len(self._conversation_principals) >= MAX_CHAT_CONVERSATIONS:
                raise AstraChatGatewayError("Astra chat conversation capacity reached.")
            conversation_id = f"conv_chat_{uuid4().hex}"
            self._conversation_engine.create_conversation(
                conversation_id=conversation_id,
                created_at=timestamp,
            )
            self._conversation_principals[conversation_id] = principal_reference
        else:
            conversation_id = request.conversation_id
            if self._conversation_principals.get(conversation_id) != principal_reference:
                raise AstraChatGatewayError("Conversation does not belong to the authenticated principal.")
        self._turn_sequence += 1
        turn_id = f"turn_chat_{self._turn_sequence:08d}_{uuid4().hex[:12]}"
        self._conversation_engine.record_current_turn(
            conversation_id,
            AstraCurrentTurnContext(
                turn_id=turn_id,
                received_at=timestamp,
                request_reference=f"chat/request/{_digest(conversation_id + turn_id)[:24]}",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
                route_reference="route:/astra/chat",
            ),
            history_entry_id=f"ctx_chat_{self._turn_sequence:08d}_{uuid4().hex[:12]}",
            summary_reference="astra-chat:declared-intent",
        )
        return conversation_id, turn_id

    def _resolve_declared_intent(
        self,
        declared: AstraChatDeclaredIntent,
        *,
        conversation_snapshot: Any,
        requester_context: Any,
        observed_at: datetime,
    ) -> AstraIntentResolution:
        parameters = _intent_parameters(declared.parameters)
        binding = self._conversation_engine.issue_declared_intent_binding(
            conversation_snapshot=conversation_snapshot,
            declared_action=declared.declared_action,
            declared_subject=declared.declared_subject,
            declared_target=None,
            declared_parameters=tuple(
                AstraBoundDeclaredIntentParameter(name=item.name, value_reference=item.value_reference)
                for item in parameters
            ),
        )
        current_turn = conversation_snapshot.current_turn
        request = AstraIntentRequest(
            intent_request_id=f"intent_req_chat_{_digest(binding.binding_id + current_turn.turn_id)[:24]}",
            runtime_instance_id=self._runtime_instance_id,
            conversation_id=conversation_snapshot.metadata.conversation_id,
            current_turn_reference=current_turn.turn_id,
            request_reference=current_turn.request_reference,
            declared_action=declared.declared_action,
            declared_subject=declared.declared_subject,
            declared_target=None,
            declared_parameters=parameters,
            declared_intent_binding=binding,
            constitutional_requirements=_chat_requirements(),
            timestamp=observed_at,
            version=ASTRA_CHAT_VERSION,
        )
        return self._runtime.intent_resolution.resolve(
            request,
            conversation_engine=self._conversation_engine,
            conversation_snapshot=conversation_snapshot,
            requester_context=requester_context,
        )

    def _execution_request_id(self, timestamp: datetime) -> str:
        self._execution_sequence += 1
        return f"read_exec_req_chat_{self._execution_sequence:08d}_{_digest(timestamp.isoformat())[:16]}"

    def _intent_non_success(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        intent_resolution: AstraIntentResolution,
        observed_at: datetime,
    ) -> AstraChatResponse:
        status = (
            AstraChatStatus.CLARIFICATION_REQUIRED
            if intent_resolution.clarification_required
            else AstraChatStatus.CAPABILITY_UNAVAILABLE
        )
        return self._bounded_failure(
            conversation_id=conversation_id,
            turn_id=turn_id,
            status=status,
            response_kind=(
                AstraChatResponseKind.CLARIFICATION
                if status is AstraChatStatus.CLARIFICATION_REQUIRED
                else AstraChatResponseKind.CAPABILITY_UNAVAILABLE
            ),
            message="The declared intent could not be resolved for governed execution.",
            reason_codes=(intent_resolution.intent_status.value, "intent_resolution_non_success"),
            observed_at=observed_at,
            resolved_intent=intent_resolution.intent_id,
            evidence_references=intent_resolution.evidence_references,
        )

    def _unavailable(
        self,
        conversation_id: str,
        turn_id: str,
        reason_code: str,
        observed_at: datetime,
    ) -> AstraChatResponse:
        return self._bounded_failure(
            conversation_id=conversation_id,
            turn_id=turn_id,
            status=AstraChatStatus.CAPABILITY_UNAVAILABLE,
            response_kind=AstraChatResponseKind.CAPABILITY_UNAVAILABLE,
            message="That declared capability is not available in Astra chat.",
            reason_codes=(reason_code,),
            observed_at=observed_at,
        )

    def _bounded_failure(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        status: AstraChatStatus,
        response_kind: AstraChatResponseKind,
        message: str,
        reason_codes: tuple[str, ...],
        observed_at: datetime,
        resolved_intent: str | None = None,
        evidence_references: tuple[str, ...] = (),
    ) -> AstraChatResponse:
        return AstraChatResponse(
            conversation_id=conversation_id,
            turn_id=turn_id,
            status=status,
            resolved_intent=resolved_intent,
            capability_id=None,
            response_kind=response_kind,
            message=message,
            structured_result=None,
            reason_codes=tuple(_bounded_reason_codes(reason_codes)),
            clarification_required=status is AstraChatStatus.CLARIFICATION_REQUIRED,
            evidence_references=tuple(_bounded_references(evidence_references)),
            observed_at=observed_at,
        )


def _subscription_parameters(
    parameters: tuple[AstraChatDeclaredParameter, ...],
) -> tuple[SubscriptionAstraParameter, ...]:
    return tuple(SubscriptionAstraParameter(name=item.name, value=item.value) for item in parameters)


def _intent_parameters(
    parameters: tuple[AstraChatDeclaredParameter, ...],
) -> tuple[AstraDeclaredIntentParameter, ...]:
    return tuple(
        AstraDeclaredIntentParameter(name=item.name, value_reference=_value_reference(item))
        for item in parameters
    )


def _value_reference(parameter: AstraChatDeclaredParameter) -> str:
    value = str(parameter.value).strip().lower().replace(" ", "_")
    safe = "".join(character for character in value if character.isalnum() or character in {":", ".", "_", "-", "/"})
    if not safe:
        safe = "value"
    return f"value:{parameter.name}:{safe[:120]}"


def _structured_result(result: AstraReadExecutionResult) -> dict[str, Any]:
    return {
        "status": result.status.value,
        "result_kind": result.result_kind,
        "summary": dict(result.summary),
        "records": [dict(record) for record in result.records],
        "record_count": result.record_count,
        "returned_count": result.returned_count,
        "truncated": result.truncated,
        "reason_codes": list(_bounded_reason_codes(result.reason_codes)),
    }


def _message(result: AstraReadExecutionResult) -> str:
    summary = result.summary
    if summary.get("answer_type") == "count" and "count" in summary:
        return f"{summary.get('subject', 'subscriptions').title()}: {summary['count']}."
    if result.returned_count:
        return f"Returned {result.returned_count} governed Subscription Manager result item(s)."
    if result.record_count:
        return f"Prepared governed Subscription Manager summary for {result.record_count} item(s)."
    return "No matching Subscription Manager records were found."


def _chat_requirements() -> tuple[ConstitutionalRequirementReference, ...]:
    return (
        ConstitutionalRequirementReference(
            constitutional_source="ASTRA-010",
            requirement_id="AIR-CM-009",
            requirement_version="1.0.0",
        ),
    )


def _bounded_reason_codes(values: tuple[str, ...]) -> tuple[str, ...]:
    result = []
    for value in values:
        safe = "".join(character for character in value.lower() if character.isalnum() or character in {"_", "-"})
        if safe and safe not in result:
            result.append(safe[:80])
    return tuple(result[:20])


def _bounded_references(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(value for value in values if isinstance(value, str) and len(value) <= 160)[:20]


def _validate_safe_payload(value: Any) -> None:
    serialized = json.dumps(value, default=str, sort_keys=True).lower()
    prohibited = (
        "authorization: bearer",
        "api_key",
        "password",
        "private_key",
        "provider_" + "payload",
        "raw_" + "pro" + "mpt",
        "secret",
        "ses" + "sion",
        "s" + "ql",
        "token",
        "traceback",
    )
    if any(item in serialized for item in prohibited):
        raise AstraChatGatewayError("Astra chat response contains prohibited private material.")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _fallback_conversation_id(timestamp: datetime) -> str:
    return f"conv_chat_denied_{_digest(timestamp.isoformat())[:24]}"


def _fallback_turn_id(timestamp: datetime) -> str:
    return f"turn_chat_denied_{_digest(timestamp.isoformat())[:24]}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraChatGatewayError(f"{label} timestamp must be timezone-aware.")
