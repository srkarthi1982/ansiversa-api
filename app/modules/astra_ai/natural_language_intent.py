from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from typing import Any, Mapping, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

from app.modules.astra_ai.chat_gateway import (
    AstraChatDeclaredIntent,
    AstraChatDeclaredParameter,
    AstraChatGateway,
    AstraChatRequest,
    AstraChatResponse,
    AstraChatStatus,
)
from app.modules.auth.service import AuthenticatedUserContext
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import (
    SubscriptionAstraCapabilityStatus,
)


ASTRA_AI_INTENT_IMPLEMENTATION_REFERENCE = "ASTRA-AI-INTENT-001"
ASTRA_AI_INTENT_VERSION = "1.0.0"
SUBSCRIPTION_MANAGER_APP_ID = "subscription_manager"
MAX_QUESTION_LENGTH = 2000


class AstraIntentError(ValueError):
    """Raised when an intent candidate cannot preserve the certified boundary."""


class AstraIntentProviderUnavailable(RuntimeError):
    """Raised when the bounded intent provider cannot be reached or used."""


class AstraIntentProviderInvalidResponse(RuntimeError):
    """Raised when a provider response is not one bounded structured candidate."""


class AstraIntentProvider(Protocol):
    def interpret(self, envelope: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class AstraInterpretationStatus(StrEnum):
    RESOLVED = "resolved"
    CLARIFICATION_REQUIRED = "clarification_required"
    UNSUPPORTED = "unsupported"


class AstraIntentReason(StrEnum):
    AMBIGUOUS_COST_BASIS = "ambiguous_cost_basis"
    MISSING_DAYS_WINDOW = "missing_days_window"
    MULTIPLE_SUPPORTED_MEANINGS = "multiple_supported_meanings"
    INSUFFICIENT_SUPPORTED_INTENT = "insufficient_supported_intent"
    UNSUPPORTED_REQUEST = "unsupported_request"
    UNSUPPORTED_WRITE = "unsupported_write"
    UNSUPPORTED_APP = "unsupported_app"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    AUTHORITY_OR_INJECTION_REQUEST = "authority_or_injection_request"


class AstraAgentStatus(StrEnum):
    OK = "ok"
    CLARIFICATION_REQUIRED = "clarification_required"
    UNSUPPORTED = "unsupported"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    INVALID_PROVIDER_RESPONSE = "invalid_provider_response"
    STALE_OR_INVALID_CONVERSATION = "stale_or_invalid_conversation"
    GOVERNED_DENIAL = "governed_denial"


class AstraIntentParameterCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=40)
    value: StrictInt


class AstraIntentCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    interpretation_status: AstraInterpretationStatus
    app_id: str | None = Field(default=None, min_length=3, max_length=80)
    capability_id: str | None = Field(default=None, min_length=3, max_length=120)
    parameters: tuple[AstraIntentParameterCandidate, ...] = Field(default_factory=tuple, max_length=12)
    clarification_reason: AstraIntentReason | None = None

    @model_validator(mode="after")
    def validate_status_shape(self) -> "AstraIntentCandidate":
        names = tuple(parameter.name for parameter in self.parameters)
        if len(names) != len(set(names)):
            raise ValueError("Intent candidate parameter names must be unique.")
        if self.interpretation_status is AstraInterpretationStatus.RESOLVED:
            if self.app_id is None or self.capability_id is None:
                raise ValueError("Resolved intent requires one app and capability.")
            if self.clarification_reason is not None:
                raise ValueError("Resolved intent cannot carry a clarification reason.")
        elif self.app_id is not None or self.capability_id is not None or self.parameters:
            raise ValueError("Non-resolved intent cannot carry executable intent data.")
        elif self.clarification_reason is None:
            raise ValueError("Non-resolved intent requires a bounded reason.")
        return self


class AstraIntentParameterMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    primitive_type: str
    required: bool
    minimum: int | None = None
    maximum: int | None = None


class AstraIntentCapabilityMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    app_id: str
    capability_id: str
    capability_version: str
    purpose: str
    parameters: tuple[AstraIntentParameterMetadata, ...]
    enabled: bool


class AstraIntentMetadataProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = ASTRA_AI_INTENT_VERSION
    capabilities: tuple[AstraIntentCapabilityMetadata, ...]
    digest: str


class AstraValidatedIntent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    app_id: str
    capability_id: str
    parameters: tuple[AstraChatDeclaredParameter, ...]
    metadata_digest: str


class AstraAgentQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, frozen=True)

    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    conversation_id: str | None = Field(
        default=None,
        alias="conversationId",
        pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$",
    )
    client_request_reference: str | None = Field(
        default=None,
        alias="clientRequestReference",
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )

    @field_validator("question")
    @classmethod
    def trim_question(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("Question is required.")
        return question


class AstraAgentQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, frozen=True)

    conversation_id: str | None = Field(default=None, serialization_alias="conversationId")
    status: AstraAgentStatus
    interpretation_status: AstraInterpretationStatus | None = Field(
        default=None,
        serialization_alias="interpretationStatus",
    )
    interpretation_reference: str = Field(serialization_alias="interpretationReference")
    capability_id: str | None = Field(default=None, serialization_alias="capabilityId")
    message: str = Field(min_length=1, max_length=240)
    structured_result: dict[str, Any] | None = Field(default=None, serialization_alias="structuredResult")
    clarification_reason: AstraIntentReason | None = Field(
        default=None,
        serialization_alias="clarificationReason",
    )
    reason_codes: tuple[str, ...] = Field(default_factory=tuple, serialization_alias="reasonCodes")
    production_authorization_state: str = Field(
        default="not_approved",
        serialization_alias="productionAuthorizationState",
        pattern=r"^not_approved$",
    )
    version: str = ASTRA_AI_INTENT_VERSION


EXACT_QUESTION_CAPABILITIES: dict[str, str] = {
    "How many subscriptions do I have?": "subscription.count_all",
    "How many active subscriptions do I have?": "subscription.count_active",
    "Show my active subscriptions": "subscription.list_active",
    "Which subscription costs the most?": "subscription.highest_cost",
    "What is my total recurring subscription cost?": "subscription.total_recurring_cost",
    "What is my estimated monthly subscription cost?": "subscription.monthly_cost_estimate",
    "Which subscriptions renew this month?": "subscription.renewing_this_month",
    "Which subscriptions are overdue for renewal?": "subscription.overdue_renewals",
    "Group my subscriptions by category": "subscription.group_by_category",
}
RENEWING_WITHIN_DAYS_PATTERN = re.compile(r"^Which subscriptions renew within ([1-9][0-9]{0,2}) days\?$")
PROHIBITED_REQUEST_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(delete|cancel|create|update|write|pause)\b.*\bsubscription",
        r"\bpretend\b.*\badmin(?:istrator)?\b",
        r"\b(query|access|use)\b.*\b(database|db|sql)\b",
        r"\banother user(?:'s)?\b",
        r"\bevery user(?:'s)?\b",
        r"\b(system|developer) prompt\b",
        r"\bsubscription\.delete",
        r"\bignore (?:the |all |previous )?(?:rules|instructions)\b",
    )
)


def project_subscription_capabilities() -> AstraIntentMetadataProjection:
    capabilities: list[AstraIntentCapabilityMetadata] = []
    for definition in subscription_reads.capability_catalog():
        parameters: tuple[AstraIntentParameterMetadata, ...] = ()
        if definition.allowed_parameters == ("days",):
            parameters = (
                AstraIntentParameterMetadata(
                    name="days",
                    primitive_type="integer",
                    required=True,
                    minimum=1,
                    maximum=366,
                ),
            )
        capabilities.append(
            AstraIntentCapabilityMetadata(
                app_id=definition.app_identity,
                capability_id=definition.capability_id,
                capability_version=definition.capability_version,
                purpose=definition.purpose,
                parameters=parameters,
                enabled=definition.status is SubscriptionAstraCapabilityStatus.ENABLED,
            )
        )
    payload = [capability.model_dump(mode="json") for capability in capabilities]
    digest = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return AstraIntentMetadataProjection(capabilities=tuple(capabilities), digest=digest)


def exact_intent_candidate(question: str) -> AstraIntentCandidate | None:
    capability_id = EXACT_QUESTION_CAPABILITIES.get(question)
    if capability_id is not None:
        return AstraIntentCandidate(
            interpretation_status=AstraInterpretationStatus.RESOLVED,
            app_id=SUBSCRIPTION_MANAGER_APP_ID,
            capability_id=capability_id,
        )
    match = RENEWING_WITHIN_DAYS_PATTERN.fullmatch(question)
    if match is None:
        return None
    days = int(match.group(1))
    if days < 1 or days > 366:
        return None
    return AstraIntentCandidate(
        interpretation_status=AstraInterpretationStatus.RESOLVED,
        app_id=SUBSCRIPTION_MANAGER_APP_ID,
        capability_id="subscription.renewing_within_days",
        parameters=(AstraIntentParameterCandidate(name="days", value=days),),
    )


def prohibited_request_candidate(question: str) -> AstraIntentCandidate | None:
    if not any(pattern.search(question) for pattern in PROHIBITED_REQUEST_PATTERNS):
        return None
    return AstraIntentCandidate(
        interpretation_status=AstraInterpretationStatus.UNSUPPORTED,
        clarification_reason=AstraIntentReason.AUTHORITY_OR_INJECTION_REQUEST,
    )


def validate_intent_candidate(
    candidate: AstraIntentCandidate,
    projection: AstraIntentMetadataProjection,
) -> AstraValidatedIntent:
    if candidate.interpretation_status is not AstraInterpretationStatus.RESOLVED:
        raise AstraIntentError("Only resolved candidates can be validated for chat handoff.")
    if candidate.app_id != SUBSCRIPTION_MANAGER_APP_ID or candidate.capability_id is None:
        raise AstraIntentError("Intent candidate app is not eligible.")

    projected = {
        item.capability_id: item
        for item in projection.capabilities
        if item.enabled and item.app_id == SUBSCRIPTION_MANAGER_APP_ID
    }
    metadata = projected.get(candidate.capability_id)
    if metadata is None:
        raise AstraIntentError("Intent candidate capability is not in the eligible projection.")

    current = {
        definition.capability_id: definition
        for definition in subscription_reads.capability_catalog()
        if definition.status is SubscriptionAstraCapabilityStatus.ENABLED
    }.get(candidate.capability_id)
    if current is None or current.capability_version != metadata.capability_version:
        raise AstraIntentError("Intent candidate capability is not current in the app-owned catalog.")

    if candidate.capability_id == "subscription.renewing_within_days":
        if len(candidate.parameters) != 1 or candidate.parameters[0].name != "days":
            raise AstraIntentError("Renewal window requires exactly one days parameter.")
        days = candidate.parameters[0].value
        if isinstance(days, bool) or not isinstance(days, int) or days < 1 or days > 366:
            raise AstraIntentError("Renewal day window must be an integer between 1 and 366.")
        parameters = (AstraChatDeclaredParameter(name="days", value=days),)
    else:
        if candidate.parameters:
            raise AstraIntentError("This capability accepts no parameters.")
        parameters = ()

    return AstraValidatedIntent(
        app_id=SUBSCRIPTION_MANAGER_APP_ID,
        capability_id=candidate.capability_id,
        parameters=parameters,
        metadata_digest=projection.digest,
    )


def candidate_output_json_schema() -> dict[str, Any]:
    reasons = [reason.value for reason in AstraIntentReason]
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "interpretation_status": {"type": "string", "enum": [status.value for status in AstraInterpretationStatus]},
            "app_id": {"type": ["string", "null"]},
            "capability_id": {"type": ["string", "null"]},
            "parameters": {
                "type": "array",
                "maxItems": 12,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string", "enum": ["days"]},
                        "value": {"type": "integer"},
                    },
                    "required": ["name", "value"],
                },
            },
            "clarification_reason": {"type": ["string", "null"], "enum": reasons + [None]},
        },
        "required": ["interpretation_status", "app_id", "capability_id", "parameters", "clarification_reason"],
    }


def provider_envelope(question: str, projection: AstraIntentMetadataProjection) -> dict[str, Any]:
    return {
        "schema_version": projection.schema_version,
        "question": question,
        "allowed_interpretation_statuses": [status.value for status in AstraInterpretationStatus],
        "eligible_capabilities": [
            capability.model_dump(mode="json")
            for capability in projection.capabilities
            if capability.enabled
        ],
    }


class AstraNaturalLanguageIntentInterpreter:
    """Coordinates interpretation only; authority remains in certified chat."""

    def __init__(self, *, gateway: AstraChatGateway, provider: AstraIntentProvider | None) -> None:
        self._gateway = gateway
        self._provider = provider

    def handle(
        self,
        request: AstraAgentQueryRequest,
        *,
        authenticated_context: AuthenticatedUserContext,
        subscription_manager_db: Any,
    ) -> AstraAgentQueryResponse:
        reference = f"intent_{uuid4().hex}"
        projection = project_subscription_capabilities()
        candidate = exact_intent_candidate(request.question)
        if candidate is None:
            candidate = prohibited_request_candidate(request.question)
        if candidate is None:
            if self._provider is None:
                return self._failure(
                    reference,
                    status=AstraAgentStatus.PROVIDER_UNAVAILABLE,
                    message="Natural-language interpretation is unavailable. Try a supported exact question.",
                    reason_codes=("intent_provider_unavailable",),
                )
            try:
                raw_candidate = self._provider.interpret(
                    provider_envelope(request.question, projection)
                )
                candidate = AstraIntentCandidate.model_validate(raw_candidate)
            except AstraIntentProviderUnavailable:
                return self._failure(
                    reference,
                    status=AstraAgentStatus.PROVIDER_UNAVAILABLE,
                    message="Natural-language interpretation is temporarily unavailable.",
                    reason_codes=("intent_provider_unavailable",),
                )
            except (AstraIntentProviderInvalidResponse, ValueError, TypeError):
                return self._failure(
                    reference,
                    status=AstraAgentStatus.INVALID_PROVIDER_RESPONSE,
                    message="Natural-language interpretation could not be validated.",
                    reason_codes=("invalid_provider_response",),
                )
            except Exception:
                return self._failure(
                    reference,
                    status=AstraAgentStatus.INVALID_PROVIDER_RESPONSE,
                    message="Natural-language interpretation could not be validated.",
                    reason_codes=("invalid_provider_response",),
                )

        if candidate.interpretation_status is AstraInterpretationStatus.CLARIFICATION_REQUIRED:
            return self._failure(
                reference,
                status=AstraAgentStatus.CLARIFICATION_REQUIRED,
                interpretation_status=candidate.interpretation_status,
                message="Please clarify the supported Subscription Manager question.",
                reason_codes=(candidate.clarification_reason.value,),
                clarification_reason=candidate.clarification_reason,
            )
        if candidate.interpretation_status is AstraInterpretationStatus.UNSUPPORTED:
            return self._failure(
                reference,
                status=AstraAgentStatus.UNSUPPORTED,
                interpretation_status=candidate.interpretation_status,
                message="That request is not supported by the governed read-only agent.",
                reason_codes=(candidate.clarification_reason.value,),
                clarification_reason=candidate.clarification_reason,
            )

        try:
            validated = validate_intent_candidate(candidate, projection)
        except AstraIntentError:
            return self._failure(
                reference,
                status=AstraAgentStatus.INVALID_PROVIDER_RESPONSE,
                interpretation_status=candidate.interpretation_status,
                message="Natural-language interpretation did not match an eligible capability.",
                reason_codes=("candidate_validation_failed",),
            )

        chat_response = self._gateway.handle(
            AstraChatRequest(
                conversation_id=request.conversation_id,
                client_request_reference=request.client_request_reference,
                declared_intent=AstraChatDeclaredIntent(
                    app_id=validated.app_id,
                    declared_action="get_information",
                    declared_subject="subscription",
                    capability_id=validated.capability_id,
                    parameters=validated.parameters,
                ),
            ),
            authenticated_context=authenticated_context,
            subscription_manager_db=subscription_manager_db,
        )
        return self._from_chat(reference, validated, chat_response)

    def _from_chat(
        self,
        reference: str,
        validated: AstraValidatedIntent,
        response: AstraChatResponse,
    ) -> AstraAgentQueryResponse:
        if response.status is AstraChatStatus.OK:
            status = AstraAgentStatus.OK
        elif "foreign_or_stale_conversation" in response.reason_codes:
            status = AstraAgentStatus.STALE_OR_INVALID_CONVERSATION
        else:
            status = AstraAgentStatus.GOVERNED_DENIAL
        return AstraAgentQueryResponse(
            conversation_id=response.conversation_id,
            status=status,
            interpretation_status=AstraInterpretationStatus.RESOLVED,
            interpretation_reference=reference,
            capability_id=validated.capability_id,
            message=response.message,
            structured_result=response.structured_result,
            reason_codes=response.reason_codes,
        )

    @staticmethod
    def _failure(
        reference: str,
        *,
        status: AstraAgentStatus,
        message: str,
        reason_codes: tuple[str, ...],
        interpretation_status: AstraInterpretationStatus | None = None,
        clarification_reason: AstraIntentReason | None = None,
    ) -> AstraAgentQueryResponse:
        return AstraAgentQueryResponse(
            status=status,
            interpretation_status=interpretation_status,
            interpretation_reference=reference,
            message=message,
            clarification_reason=clarification_reason,
            reason_codes=reason_codes,
        )
