from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from app.modules.astra_ai.activation import (
    SUBSCRIPTION_MANAGER_APP_ID,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
    AstraRuntimeActivationContract,
    activation_digest,
)
from app.modules.astra_ai.constitutional_contracts import (
    AuthorityClass,
    ProductionAuthorizationState,
    SafetyClassification,
    assert_no_prohibited_contract_material,
)


METADATA_ACTIVATION_BINDING_VERSION = "1.0.0"
METADATA_ACTIVATION_BINDING_REFERENCE = "ASTRA-META-ACT-BIND-001"
METADATA_CONTEXT_TTL_SECONDS = 300


class AstraMetadataActivationBindingError(ValueError):
    """Raised when governed metadata context binding fails closed."""


class AstraGovernedMetadataContextStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


def _is_exact_runtime_owner(
    value: object | None,
    *,
    runtime_instance_id: str,
    runtime_authority: object,
) -> bool:
    from app.modules.astra_ai.runtime import AstraRuntime

    return (
        isinstance(value, AstraRuntime)
        and value.identity.startup_instance_id == runtime_instance_id
        and value._metadata_context_issuer_authority is runtime_authority
    )


class AstraGovernedMetadataContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)
    _metadata_context_issuer: AstraGovernedMetadataContextIssuer | None = PrivateAttr(default=None)

    context_id: str = Field(pattern=r"^astra_meta_ctx_[a-f0-9]{32}$")
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-z0-9][a-z0-9_-]{7,120}$")
    current_turn_reference: str = Field(pattern=r"^turn_[a-z0-9][a-z0-9_-]{7,120}$")
    request_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,160}$")
    app_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,80}$")
    capability_scope: str = Field(pattern=r"^[a-z][a-z0-9_.:-]{2,120}$")
    capability_id: str = Field(pattern=r"^subscription\.[a-z][a-z0-9_]{2,80}$")
    capability_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    activation_reference: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,200}$")
    activation_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    issued_at: datetime
    expires_at: datetime
    production_authorization_state: ProductionAuthorizationState = ProductionAuthorizationState.NOT_APPROVED
    version: str = METADATA_ACTIVATION_BINDING_VERSION

    @model_validator(mode="after")
    def validate_context(self) -> "AstraGovernedMetadataContext":
        _aware(self.issued_at, "Governed metadata context issuance")
        _aware(self.expires_at, "Governed metadata context expiration")
        if self.expires_at <= self.issued_at:
            raise AstraMetadataActivationBindingError("Governed metadata context expiration must follow issuance.")
        if self.app_id != SUBSCRIPTION_MANAGER_APP_ID:
            raise AstraMetadataActivationBindingError("Governed metadata context only supports Subscription Manager.")
        if self.capability_scope != SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE:
            raise AstraMetadataActivationBindingError("Governed metadata context scope is not authorized.")
        if self.production_authorization_state is not ProductionAuthorizationState.NOT_APPROVED:
            raise AstraMetadataActivationBindingError("Governed metadata context cannot approve production.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self

    @property
    def context_reference(self) -> str:
        return f"{METADATA_ACTIVATION_BINDING_REFERENCE}:{self.version}:{self.runtime_instance_id}:{self.context_id}"


class AstraGovernedMetadataContextIssuer:
    def __init__(
        self,
        *,
        runtime_instance_id: str,
        issuer_reference: str,
        _runtime_authority: object | None = None,
        _runtime_owner: object | None = None,
        capacity: int = 200,
    ) -> None:
        if (
            _runtime_authority is None
            or not _is_exact_runtime_owner(
                _runtime_owner,
                runtime_instance_id=runtime_instance_id,
                runtime_authority=_runtime_authority,
            )
        ):
            raise AstraMetadataActivationBindingError("Governed metadata context issuers require Runtime-owned authority.")
        if capacity < 1 or capacity > 1000:
            raise AstraMetadataActivationBindingError("Governed metadata context issuer capacity is invalid.")
        self.runtime_instance_id = runtime_instance_id
        self.issuer_reference = issuer_reference
        self._runtime_authority = _runtime_authority
        self._runtime_owner = _runtime_owner
        self._capacity = capacity
        self._issued: dict[str, AstraGovernedMetadataContext] = {}
        self._active = True

    def issue(
        self,
        *,
        conversation_id: str,
        current_turn_reference: str,
        request_reference: str,
        app_id: str,
        capability_scope: str,
        capability_id: str,
        capability_version: str,
        activation: AstraRuntimeActivationContract,
        issued_at: datetime,
        _runtime_authority: object | None = None,
    ) -> AstraGovernedMetadataContext:
        if not self._active:
            raise AstraMetadataActivationBindingError("Governed metadata context issuer is inactive.")
        if _runtime_authority is not self._runtime_authority:
            raise AstraMetadataActivationBindingError("Governed metadata context issuance requires Runtime-owned authority.")
        _aware(issued_at, "Governed metadata context issuance")
        if not self._valid_activation(activation, app_id=app_id, capability_scope=capability_scope, observed_at=issued_at):
            raise AstraMetadataActivationBindingError("Governed metadata context requires exact Runtime activation coverage.")
        if len(self._issued) >= self._capacity:
            self._issued.pop(next(iter(self._issued)))
        context = AstraGovernedMetadataContext(
            context_id=f"astra_meta_ctx_{uuid4().hex}",
            runtime_instance_id=self.runtime_instance_id,
            conversation_id=conversation_id,
            current_turn_reference=current_turn_reference,
            request_reference=request_reference,
            app_id=app_id,
            capability_scope=capability_scope,
            capability_id=capability_id,
            capability_version=capability_version,
            activation_reference=activation.activation_reference,
            activation_digest=f"sha256:{activation_digest(activation)}",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(seconds=METADATA_CONTEXT_TTL_SECONDS),
        )
        context._metadata_context_issuer = self
        self._issued[context.context_reference] = context
        return context

    def validates(
        self,
        context: Any,
        *,
        observed_at: datetime,
        conversation_id: str,
        current_turn_reference: str,
        request_reference: str,
        app_id: str,
        capability_scope: str,
        capability_id: str,
        capability_version: str,
    ) -> bool:
        _aware(observed_at, "Governed metadata context validation")
        return (
            self._active
            and isinstance(context, AstraGovernedMetadataContext)
            and context._metadata_context_issuer is self
            and self._runtime_owner_validates_issuer()
            and self._issued.get(context.context_reference) is context
            and context.runtime_instance_id == self.runtime_instance_id
            and context.conversation_id == conversation_id
            and context.current_turn_reference == current_turn_reference
            and context.request_reference == request_reference
            and context.app_id == app_id
            and context.capability_scope == capability_scope
            and context.capability_id == capability_id
            and context.capability_version == capability_version
            and context.issued_at <= observed_at < context.expires_at
            and context.production_authorization_state is ProductionAuthorizationState.NOT_APPROVED
        )

    def invalidate(self) -> None:
        self._active = False
        self._issued = {}

    def _valid_activation(
        self,
        activation: AstraRuntimeActivationContract,
        *,
        app_id: str,
        capability_scope: str,
        observed_at: datetime,
    ) -> bool:
        return (
            isinstance(activation, AstraRuntimeActivationContract)
            and activation.validates_runtime_ownership(
                activation_reference=activation.activation_reference,
                activation_digest_value=f"sha256:{activation_digest(activation)}",
            )
            and activation.covers(
                runtime_instance_id=self.runtime_instance_id,
                authority_class=AuthorityClass.READ_ONLY,
                safety_classification=SafetyClassification.PRIVATE_READ,
                app_id=app_id,
                capability_scope=capability_scope,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                provider_requested=False,
                memory_requested=False,
                adaptation_requested=False,
                execution_handoff_requested=False,
                observed_at=observed_at,
            )
            and activation.covers(
                runtime_instance_id=self.runtime_instance_id,
                authority_class=AuthorityClass.ADVISORY,
                safety_classification=SafetyClassification.PRIVATE_READ,
                app_id=app_id,
                capability_scope=capability_scope,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
                provider_requested=False,
                memory_requested=False,
                adaptation_requested=False,
                execution_handoff_requested=False,
                observed_at=observed_at,
            )
        )

    def _runtime_owner_validates_issuer(self) -> bool:
        if not _is_exact_runtime_owner(
            self._runtime_owner,
            runtime_instance_id=self.runtime_instance_id,
            runtime_authority=self._runtime_authority,
        ):
            return False
        validator = getattr(self._runtime_owner, "_validates_metadata_context_issuer", None)
        return bool(callable(validator) and validator(self))


def governed_metadata_context_digest(value: AstraGovernedMetadataContext) -> str:
    return hashlib.sha256(
        json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraMetadataActivationBindingError(f"{label} timestamp must be timezone-aware.")
