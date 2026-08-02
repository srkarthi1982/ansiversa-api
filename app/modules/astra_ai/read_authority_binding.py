from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.astra_ai.constitutional_contracts import GovernanceOutcome
from app.modules.astra_ai.intent_resolution import AstraIntentResolution, AstraIntentStatus
from app.modules.astra_ai.read_access_authorization import (
    AstraAuthorityProof,
    AstraAuthorityProofIssuer,
    AstraNamedReadCapability,
    AstraNamedReadCapabilityRegistry,
    AstraReadAuthorizationDecision,
    AstraReadAuthorizationRequest,
    AstraReadDecisionStatus,
    AstraReadPurpose,
    preview_authorization_decision_id,
)
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import (
    APP_ID as SUBSCRIPTION_MANAGER_APP_ID,
    APP_SCOPE as SUBSCRIPTION_MANAGER_APP_SCOPE,
    CAPABILITY_VERSION as SUBSCRIPTION_MANAGER_CAPABILITY_VERSION,
    SubscriptionAstraAuthorizationReference,
    SubscriptionAstraCapabilityError,
    SubscriptionAstraParameter,
    SubscriptionAstraReadGrant,
    SubscriptionAstraReadRequest,
)


READ_AUTHORITY_BINDING_VERSION = "1.0.0"
READ_AUTHORITY_BINDING_IMPLEMENTATION_REFERENCE = "ASTRA-READ-AUTH-BIND-001"
AUTHORITY_TTL_SECONDS = 300
DEFAULT_TENANT_SCOPE = "current_tenant"
DEFAULT_RECORD_SCOPE = "owned_records"
REQUIRED_PROOF_CLASSES = ("principal", "user", "tenant", "app", "record", "field", "purpose")


class AstraReadAuthorityBindingError(ValueError):
    """Raised when Runtime-owned read authority binding fails closed."""


class AstraReadAuthorityBindingStatus(StrEnum):
    READY = "ready"
    UNAVAILABLE = "unavailable"


class AstraReadAuthorityCapabilitySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    read_capability_id: str
    adapter_capability_id: str
    owning_app_id: str
    version: str
    maximum_row_count: int
    allowed_purposes: tuple[AstraReadPurpose, ...]
    allowed_field_references: tuple[str, ...]


class AstraBoundReadAuthorization(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    authorization_request: AstraReadAuthorizationRequest
    authorization_decision: AstraReadAuthorizationDecision
    app_read_grant: SubscriptionAstraReadGrant = Field(exclude=True)
    adapter_capability_id: str
    adapter_capability_version: str
    authenticated_principal_reference: str
    request_reference: str
    maximum_result_count: int = Field(ge=1, le=50)

    @model_validator(mode="after")
    def validate_binding(self) -> "AstraBoundReadAuthorization":
        if self.authorization_decision.decision_status is not AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY:
            raise AstraReadAuthorityBindingError("Read authority binding requires authorized metadata-only decision.")
        if self.authorization_decision.owning_app_id != SUBSCRIPTION_MANAGER_APP_ID:
            raise AstraReadAuthorityBindingError("Read authority binding only supports Subscription Manager.")
        if self.app_read_grant.capability_id != self.adapter_capability_id:
            raise AstraReadAuthorityBindingError("App read grant does not match adapter capability.")
        return self


class AstraReadAuthorityBinding:
    """Runtime-owned bridge for certified read capability and proof authority."""

    def __init__(
        self,
        *,
        runtime: Any,
        read_access_authorization: Any,
        read_capability_registry: AstraNamedReadCapabilityRegistry,
    ) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._read_access_authorization = read_access_authorization
        self._registry = read_capability_registry
        self._sequence = 0

    @property
    def status(self) -> AstraReadAuthorityBindingStatus:
        if getattr(getattr(self._runtime, "state", None), "value", None) == "ready":
            return AstraReadAuthorityBindingStatus.READY
        return AstraReadAuthorityBindingStatus.UNAVAILABLE

    @property
    def read_capability_registry(self) -> AstraNamedReadCapabilityRegistry:
        return self._registry

    def capabilities(self) -> tuple[AstraReadAuthorityCapabilitySummary, ...]:
        return tuple(
            AstraReadAuthorityCapabilitySummary(
                read_capability_id=capability.read_capability_id,
                adapter_capability_id=_adapter_capability_id(capability),
                owning_app_id=capability.owning_app_id,
                version=capability.version,
                maximum_row_count=capability.maximum_row_count,
                allowed_purposes=capability.allowed_purposes,
                allowed_field_references=capability.allowed_field_references,
            )
            for capability in self._registry.capabilities
        )

    def authorize_subscription_manager_read(
        self,
        *,
        authenticated_user: Any,
        conversation_engine: Any,
        conversation_snapshot: Any,
        intent_resolution: AstraIntentResolution,
        adapter_capability_id: str,
        requested_field_references: tuple[str, ...] | None = None,
        requested_filter_references: tuple[str, ...] = (),
        requested_aggregation_references: tuple[str, ...] = (),
        requested_row_limit: int | None = None,
        requested_time_range_days: int = 366,
        declared_purpose: AstraReadPurpose | None = None,
        parameters: tuple[SubscriptionAstraParameter, ...] = (),
        requested_at: datetime | None = None,
    ) -> AstraBoundReadAuthorization:
        self._require_ready()
        timestamp = requested_at or _utc_now()
        _ensure_aware(timestamp, "Read authority binding")
        user_id = _authenticated_user_id(authenticated_user)
        capability = self._capability_for_adapter(adapter_capability_id)
        fields = requested_field_references or capability.allowed_field_references
        row_limit = requested_row_limit or min(capability.maximum_row_count, 50)
        purpose = declared_purpose or subscription_reads.default_read_purpose_for_adapter(adapter_capability_id)
        request_reference = _request_reference(intent_resolution, adapter_capability_id, timestamp)
        principal_reference = f"principal:{user_id}"

        non_owner_proofs = self._issue_non_owner_proofs(
            principal_reference=principal_reference,
            capability=capability,
            requested_field_references=fields,
            declared_purpose=purpose,
            timestamp=timestamp,
        )
        provisional_request = self._authorization_request(
            capability=capability,
            intent_resolution=intent_resolution,
            conversation_snapshot=conversation_snapshot,
            authenticated_principal_reference=principal_reference,
            request_reference=request_reference,
            requested_field_references=fields,
            requested_filter_references=requested_filter_references,
            requested_aggregation_references=requested_aggregation_references,
            requested_row_limit=row_limit,
            requested_time_range_days=requested_time_range_days,
            declared_purpose=purpose,
            proofs=non_owner_proofs,
            timestamp=timestamp,
        )
        expected_decision_id = preview_authorization_decision_id(
            request=provisional_request,
            capability=capability,
            status=AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY,
            governance_outcome=GovernanceOutcome.ALLOW,
            checks=self._read_access_authorization._evaluate_scope(provisional_request, capability),
        )
        app_grant = self._issue_app_grant(
            authenticated_user=authenticated_user,
            adapter_capability_id=adapter_capability_id,
            authorization_id=expected_decision_id,
            principal_reference=principal_reference,
            request_reference=request_reference,
            maximum_result_count=row_limit,
            purpose="Summarize current user subscriptions.",
            parameters=parameters,
            observed_at=timestamp,
        )
        owner_acceptance = self._issue_owner_acceptance_proof(
            capability=capability,
            app_grant=app_grant,
            authenticated_user=authenticated_user,
            timestamp=timestamp,
        )
        final_request = provisional_request.model_copy(update={"proofs": (*non_owner_proofs, owner_acceptance)})
        decision = self._runtime.authorize_read_access(
            final_request,
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation_snapshot,
            intent_resolution=intent_resolution,
            plan=None,
        )
        if decision.authorization_decision_id != expected_decision_id:
            raise AstraReadAuthorityBindingError("Read authorization decision changed after app grant issuance.")
        return AstraBoundReadAuthorization(
            authorization_request=final_request,
            authorization_decision=decision,
            app_read_grant=app_grant,
            adapter_capability_id=adapter_capability_id,
            adapter_capability_version=SUBSCRIPTION_MANAGER_CAPABILITY_VERSION,
            authenticated_principal_reference=principal_reference,
            request_reference=request_reference,
            maximum_result_count=row_limit,
        )

    def _authorization_request(
        self,
        *,
        capability: AstraNamedReadCapability,
        intent_resolution: AstraIntentResolution,
        conversation_snapshot: Any,
        authenticated_principal_reference: str,
        request_reference: str,
        requested_field_references: tuple[str, ...],
        requested_filter_references: tuple[str, ...],
        requested_aggregation_references: tuple[str, ...],
        requested_row_limit: int,
        requested_time_range_days: int,
        declared_purpose: AstraReadPurpose,
        proofs: tuple[AstraAuthorityProof, ...],
        timestamp: datetime,
    ) -> AstraReadAuthorizationRequest:
        if not isinstance(intent_resolution, AstraIntentResolution):
            raise AstraReadAuthorityBindingError("Resolved intent is required for read authority binding.")
        if intent_resolution.intent_status is not AstraIntentStatus.RESOLVED:
            raise AstraReadAuthorityBindingError("Read authority binding requires a resolved intent.")
        current_turn = getattr(conversation_snapshot, "current_turn", None)
        if current_turn is None:
            raise AstraReadAuthorityBindingError("Current turn is required for read authority binding.")
        return AstraReadAuthorizationRequest(
            authorization_request_id=_authorization_request_id(intent_resolution, capability, timestamp),
            runtime_instance_id=self._runtime_instance_id,
            conversation_id=conversation_snapshot.metadata.conversation_id,
            current_turn_reference=current_turn.turn_id,
            intent_resolution_reference=intent_resolution.intent_id,
            read_capability_id=capability.read_capability_id,
            authenticated_principal_reference=authenticated_principal_reference,
            requested_field_references=requested_field_references,
            requested_filter_references=requested_filter_references,
            requested_aggregation_references=requested_aggregation_references,
            requested_row_limit=requested_row_limit,
            requested_time_range_days=requested_time_range_days,
            declared_purpose=declared_purpose,
            requester_authority_context=f"read-authority/{READ_AUTHORITY_BINDING_IMPLEMENTATION_REFERENCE}",
            constitutional_requirement_references=capability.governance_requirement_references,
            proofs=proofs,
            requested_at=timestamp,
            request_version=READ_AUTHORITY_BINDING_VERSION,
        )

    def _issue_non_owner_proofs(
        self,
        *,
        principal_reference: str,
        capability: AstraNamedReadCapability,
        requested_field_references: tuple[str, ...],
        declared_purpose: AstraReadPurpose,
        timestamp: datetime,
    ) -> tuple[AstraAuthorityProof, ...]:
        return (
            self._proof(
                "principal",
                subject_reference=principal_reference,
                scope_references=(principal_reference,),
                timestamp=timestamp,
            ),
            self._proof(
                "user",
                subject_reference=principal_reference,
                scope_references=(capability.allowed_subject_scope,),
                timestamp=timestamp,
            ),
            self._proof(
                "tenant",
                subject_reference=principal_reference,
                scope_references=(capability.allowed_tenant_scope,),
                timestamp=timestamp,
            ),
            self._proof(
                "app",
                subject_reference=SUBSCRIPTION_MANAGER_APP_SCOPE,
                scope_references=(capability.owning_app_id,),
                timestamp=timestamp,
            ),
            self._proof(
                "record",
                subject_reference=principal_reference,
                scope_references=(capability.allowed_record_scope,),
                timestamp=timestamp,
            ),
            self._proof(
                "field",
                subject_reference=principal_reference,
                scope_references=requested_field_references,
                timestamp=timestamp,
            ),
            self._proof(
                "purpose",
                subject_reference=principal_reference,
                scope_references=(declared_purpose.value,),
                timestamp=timestamp,
            ),
        )

    def _issue_owner_acceptance_proof(
        self,
        *,
        capability: AstraNamedReadCapability,
        app_grant: SubscriptionAstraReadGrant,
        authenticated_user: Any,
        timestamp: datetime,
    ) -> AstraAuthorityProof:
        if app_grant.app_scope != SUBSCRIPTION_MANAGER_APP_SCOPE:
            raise AstraReadAuthorityBindingError("Unsupported app-owned read grant scope.")
        if app_grant.authenticated_user_id != _authenticated_user_id(authenticated_user):
            raise AstraReadAuthorityBindingError("App-owned grant principal does not match authenticated user.")
        if app_grant.capability_id != _adapter_capability_id(capability):
            raise AstraReadAuthorityBindingError("App-owned grant capability does not match read capability.")
        if not subscription_reads.default_read_grant_issuer().validates(
            app_grant,
            authenticated_user=authenticated_user,
            observed_at=timestamp,
        ):
            raise AstraReadAuthorityBindingError("App-owned read grant is not valid for owner acceptance.")
        return self._proof(
            "owner_acceptance",
            subject_reference=SUBSCRIPTION_MANAGER_APP_SCOPE,
            scope_references=(capability.read_capability_id,),
            timestamp=timestamp,
        )

    def _issue_app_grant(
        self,
        *,
        authenticated_user: Any,
        adapter_capability_id: str,
        authorization_id: str,
        principal_reference: str,
        request_reference: str,
        maximum_result_count: int,
        purpose: str,
        parameters: tuple[SubscriptionAstraParameter, ...],
        observed_at: datetime,
    ) -> SubscriptionAstraReadGrant:
        try:
            request = SubscriptionAstraReadRequest(
                capability_id=adapter_capability_id,
                capability_version=SUBSCRIPTION_MANAGER_CAPABILITY_VERSION,
                app_identity=SUBSCRIPTION_MANAGER_APP_ID,
                request_reference=request_reference,
                requested_maximum_result_count=maximum_result_count,
                authorization_reference=SubscriptionAstraAuthorizationReference(
                    authorization_id=authorization_id,
                    capability_id=adapter_capability_id,
                    capability_version=SUBSCRIPTION_MANAGER_CAPABILITY_VERSION,
                    app_scope=SUBSCRIPTION_MANAGER_APP_SCOPE,
                    decision_status="authorized_metadata_only",
                    authenticated_principal_reference=principal_reference,
                    issued_at=observed_at,
                    expires_at=observed_at + timedelta(seconds=AUTHORITY_TTL_SECONDS),
                ),
                purpose=purpose,
                observed_at=observed_at,
                parameters=parameters,
            )
            return subscription_reads.issue_read_grant(
                authenticated_user=authenticated_user,
                request=request,
            )
        except SubscriptionAstraCapabilityError as exc:
            raise AstraReadAuthorityBindingError("Subscription Manager rejected app-owned read grant issuance.") from exc

    def _proof(
        self,
        proof_class: str,
        *,
        subject_reference: str,
        scope_references: tuple[str, ...],
        timestamp: datetime,
    ) -> AstraAuthorityProof:
        issuer = self._read_access_authorization._issuers.get(proof_class)
        if not isinstance(issuer, AstraAuthorityProofIssuer):
            raise AstraReadAuthorityBindingError("Runtime-owned proof issuer is unavailable.")
        self._sequence += 1
        return issuer.issue(
            proof_id=_proof_id(proof_class, subject_reference, scope_references, timestamp, self._sequence),
            proof_class=proof_class,
            subject_reference=subject_reference,
            scope_references=scope_references,
            issued_at=timestamp,
            expires_at=timestamp + timedelta(seconds=AUTHORITY_TTL_SECONDS),
            version=READ_AUTHORITY_BINDING_VERSION,
        )

    def _capability_for_adapter(self, adapter_capability_id: str) -> AstraNamedReadCapability:
        try:
            read_capability_id = subscription_reads.read_capability_id_for_adapter(adapter_capability_id)
        except SubscriptionAstraCapabilityError as exc:
            raise AstraReadAuthorityBindingError("Unsupported Subscription Manager read capability.") from exc
        capability = self._registry.get(read_capability_id)
        if capability.owning_app_id != SUBSCRIPTION_MANAGER_APP_ID:
            raise AstraReadAuthorityBindingError("Only Subscription Manager read capabilities are authorized.")
        return capability

    def _require_ready(self) -> None:
        if self.status is not AstraReadAuthorityBindingStatus.READY:
            raise AstraReadAuthorityBindingError("Read authority binding requires ready Runtime.")


def certified_subscription_manager_read_registry() -> AstraNamedReadCapabilityRegistry:
    return AstraNamedReadCapabilityRegistry(subscription_reads.read_authorization_capabilities())


def create_runtime_read_authority_issuers(
    *,
    runtime: Any,
    issuer_authority: object,
) -> dict[str, AstraAuthorityProofIssuer]:
    issuers = {}
    for proof_class in (*REQUIRED_PROOF_CLASSES, "owner_acceptance"):
        issuers[proof_class] = AstraAuthorityProofIssuer(
            runtime_instance_id=runtime.identity.startup_instance_id,
            issuer_reference=f"runtime-read-authority:{proof_class}",
            capacity=500,
            _runtime_authority=issuer_authority,
        )
    return issuers


def bind_runtime_read_authority_issuers(
    *,
    read_access_authorization: Any,
    issuers: dict[str, AstraAuthorityProofIssuer],
) -> None:
    for proof_class in (*REQUIRED_PROOF_CLASSES, "owner_acceptance"):
        issuer = issuers.get(proof_class)
        if not isinstance(issuer, AstraAuthorityProofIssuer):
            raise AstraReadAuthorityBindingError("Runtime-owned proof issuer is missing.")
        read_access_authorization.bind_certified_issuer(proof_class, issuer)


def _adapter_capability_id(capability: AstraNamedReadCapability) -> str:
    for definition in subscription_reads.capability_catalog():
        if subscription_reads.read_capability_id_for_adapter(definition.capability_id) == capability.read_capability_id:
            return definition.capability_id
    raise AstraReadAuthorityBindingError("Unsupported Subscription Manager read capability identity.")


def _authenticated_user_id(user: Any) -> str:
    user_id = getattr(user, "id", None)
    if not isinstance(user_id, str) or not user_id:
        raise AstraReadAuthorityBindingError("Authenticated user is required for read authority binding.")
    return user_id


def _authorization_request_id(
    intent_resolution: AstraIntentResolution,
    capability: AstraNamedReadCapability,
    timestamp: datetime,
) -> str:
    digest = hashlib.sha256(
        _canonical(
            {
                "intent": intent_resolution.intent_id,
                "capability": capability.read_capability_id,
                "timestamp": timestamp.isoformat(),
            }
        ).encode()
    ).hexdigest()
    return f"read_req_auth_bind_{digest[:16]}"


def _request_reference(
    intent_resolution: AstraIntentResolution,
    adapter_capability_id: str,
    timestamp: datetime,
) -> str:
    digest = hashlib.sha256(
        f"{intent_resolution.intent_id}:{adapter_capability_id}:{timestamp.isoformat()}".encode()
    ).hexdigest()
    return f"subscription/read-authority/{digest[:24]}"


def _proof_id(
    proof_class: str,
    subject_reference: str,
    scope_references: tuple[str, ...],
    timestamp: datetime,
    sequence: int,
) -> str:
    digest = hashlib.sha256(
        _canonical(
            {
                "class": proof_class,
                "subject": subject_reference,
                "scope": scope_references,
                "timestamp": timestamp.isoformat(),
                "sequence": sequence,
            }
        ).encode()
    ).hexdigest()
    return f"proof_{proof_class}_{digest[:16]}"


def _ensure_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraReadAuthorityBindingError(f"{label} timestamp must be timezone-aware.")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
