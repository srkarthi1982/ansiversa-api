from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.config import Settings, settings
from app.modules.astra_ai.constitutional_contracts import (
    AuthorityClass,
    EnvironmentScope,
    ProductionAuthorizationState,
    RuntimeUseState,
    SafetyClassification,
    assert_no_prohibited_contract_material,
)


ASTRA_RUNTIME_ACTIVATION_ID = "ASTRA-RUNTIME-ACT-001"
ASTRA_RUNTIME_ACTIVATION_VERSION = "1.0.0"
SUBSCRIPTION_MANAGER_APP_ID = "subscription_manager"
SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE = "subscription_manager:private_read"
ACTIVATION_TTL_SECONDS = 900
ALLOWED_NONPRODUCTION_ENVIRONMENTS = (
    EnvironmentScope.LOCAL,
    EnvironmentScope.DEVELOPMENT,
    EnvironmentScope.QA,
    EnvironmentScope.STAGING,
)


class AstraRuntimeActivationError(ValueError):
    pass


class AstraRuntimeActivationStatus(StrEnum):
    DISABLED = "disabled"
    ACTIVE = "active"
    INVALID = "invalid"


class AstraRuntimeActivationSource(StrEnum):
    SERVER_CONFIGURATION = "server_configuration"
    TEST_OVERRIDE = "test_override"


class AstraRuntimeActivationContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    activation_id: str = Field(pattern=r"^ASTRA-RUNTIME-ACT-001$")
    activation_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    enabled: bool
    status: AstraRuntimeActivationStatus
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    environment_scope: EnvironmentScope
    authorized_authority_classes: tuple[AuthorityClass, ...] = Field(min_length=1, max_length=2)
    authorized_safety_classes: tuple[SafetyClassification, ...] = Field(min_length=1, max_length=1)
    authorized_app_ids: tuple[str, ...] = Field(min_length=1, max_length=1)
    authorized_capability_scopes: tuple[str, ...] = Field(min_length=1, max_length=1)
    production_authorization_state: ProductionAuthorizationState
    provider_use: RuntimeUseState
    memory_use: RuntimeUseState
    adaptation_use: RuntimeUseState
    write_use: RuntimeUseState
    issued_at: datetime
    expires_at: datetime
    source: AstraRuntimeActivationSource

    @model_validator(mode="after")
    def validate_activation(self) -> "AstraRuntimeActivationContract":
        _aware(self.issued_at)
        _aware(self.expires_at)
        if self.expires_at <= self.issued_at:
            raise AstraRuntimeActivationError("Runtime activation expiration must follow issuance.")
        if self.enabled and self.status is not AstraRuntimeActivationStatus.ACTIVE:
            raise AstraRuntimeActivationError("Enabled activation must be active.")
        if not self.enabled and self.status is AstraRuntimeActivationStatus.ACTIVE:
            raise AstraRuntimeActivationError("Disabled activation cannot be active.")
        if self.environment_scope is EnvironmentScope.PRODUCTION:
            raise AstraRuntimeActivationError("Runtime activation is prohibited in production.")
        if self.environment_scope not in ALLOWED_NONPRODUCTION_ENVIRONMENTS:
            raise AstraRuntimeActivationError("Runtime activation environment is not allowed.")
        if set(self.authorized_authority_classes) != {AuthorityClass.ADVISORY, AuthorityClass.READ_ONLY}:
            raise AstraRuntimeActivationError("Runtime activation only permits advisory/read-only authority.")
        if self.authorized_safety_classes != (SafetyClassification.PRIVATE_READ,):
            raise AstraRuntimeActivationError("Runtime activation only permits private-read safety.")
        if self.authorized_app_ids != (SUBSCRIPTION_MANAGER_APP_ID,):
            raise AstraRuntimeActivationError("Runtime activation only permits Subscription Manager.")
        if self.authorized_capability_scopes != (SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,):
            raise AstraRuntimeActivationError("Runtime activation capability scope is invalid.")
        if self.production_authorization_state is not ProductionAuthorizationState.NOT_APPROVED:
            raise AstraRuntimeActivationError("Runtime activation cannot approve production.")
        if any(
            value is not RuntimeUseState.DISABLED
            for value in (self.provider_use, self.memory_use, self.adaptation_use, self.write_use)
        ):
            raise AstraRuntimeActivationError("Runtime activation prohibits provider, memory, adaptation, and writes.")
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self

    @property
    def activation_reference(self) -> str:
        return f"{self.activation_id}:{self.activation_version}:{self.runtime_instance_id}"

    def covers(
        self,
        *,
        runtime_instance_id: str | None,
        authority_class: AuthorityClass,
        safety_classification: SafetyClassification,
        app_id: str | None,
        capability_scope: str | None,
        production_authorization_state: ProductionAuthorizationState,
        provider_requested: bool,
        memory_requested: bool,
        adaptation_requested: bool,
        execution_handoff_requested: bool,
        observed_at: datetime,
    ) -> bool:
        _aware(observed_at)
        return (
            self.enabled
            and self.status is AstraRuntimeActivationStatus.ACTIVE
            and runtime_instance_id == self.runtime_instance_id
            and self.environment_scope in ALLOWED_NONPRODUCTION_ENVIRONMENTS
            and self.environment_scope is not EnvironmentScope.PRODUCTION
            and authority_class in self.authorized_authority_classes
            and safety_classification in self.authorized_safety_classes
            and app_id in self.authorized_app_ids
            and capability_scope in self.authorized_capability_scopes
            and production_authorization_state is ProductionAuthorizationState.NOT_APPROVED
            and not provider_requested
            and not memory_requested
            and not adaptation_requested
            and not execution_handoff_requested
            and self.issued_at <= observed_at < self.expires_at
        )


class AstraRuntimeActivationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    activation_id: str = Field(pattern=r"^ASTRA-RUNTIME-ACT-001$")
    activation_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: AstraRuntimeActivationStatus
    enabled: bool
    runtime_instance_id: str = Field(pattern=r"^astra_rt_[a-f0-9]{32}$")
    environment_scope: EnvironmentScope
    authorized_app_ids: tuple[str, ...] = Field(max_length=1)
    authorized_capability_scopes: tuple[str, ...] = Field(max_length=1)
    production_authorization_state: ProductionAuthorizationState
    source: AstraRuntimeActivationSource
    issued_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def validate_snapshot(self) -> "AstraRuntimeActivationSnapshot":
        _aware(self.issued_at)
        _aware(self.expires_at)
        assert_no_prohibited_contract_material(self.model_dump(mode="json"))
        return self


def load_runtime_activation(
    *,
    runtime_instance_id: str,
    environment_scope: EnvironmentScope,
    app_settings: Settings = settings,
    loaded_at: datetime | None = None,
    source: AstraRuntimeActivationSource = AstraRuntimeActivationSource.SERVER_CONFIGURATION,
) -> AstraRuntimeActivationContract | None:
    flag = _parse_activation_flag(getattr(app_settings, "ASTRA_NONPROD_READ_ENABLED", "false"))
    if not flag:
        return None
    timestamp = loaded_at or datetime.now(timezone.utc)
    _aware(timestamp)
    return AstraRuntimeActivationContract(
        activation_id=ASTRA_RUNTIME_ACTIVATION_ID,
        activation_version=ASTRA_RUNTIME_ACTIVATION_VERSION,
        enabled=True,
        status=AstraRuntimeActivationStatus.ACTIVE,
        runtime_instance_id=runtime_instance_id,
        environment_scope=environment_scope,
        authorized_authority_classes=(AuthorityClass.ADVISORY, AuthorityClass.READ_ONLY),
        authorized_safety_classes=(SafetyClassification.PRIVATE_READ,),
        authorized_app_ids=(SUBSCRIPTION_MANAGER_APP_ID,),
        authorized_capability_scopes=(SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,),
        production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
        provider_use=RuntimeUseState.DISABLED,
        memory_use=RuntimeUseState.DISABLED,
        adaptation_use=RuntimeUseState.DISABLED,
        write_use=RuntimeUseState.DISABLED,
        issued_at=timestamp,
        expires_at=timestamp + timedelta(seconds=ACTIVATION_TTL_SECONDS),
        source=source,
    )


def activation_snapshot(
    activation: AstraRuntimeActivationContract | None,
    *,
    runtime_instance_id: str,
    environment_scope: EnvironmentScope,
    observed_at: datetime,
) -> AstraRuntimeActivationSnapshot:
    _aware(observed_at)
    if activation is None:
        return AstraRuntimeActivationSnapshot(
            activation_id=ASTRA_RUNTIME_ACTIVATION_ID,
            activation_version=ASTRA_RUNTIME_ACTIVATION_VERSION,
            status=AstraRuntimeActivationStatus.DISABLED,
            enabled=False,
            runtime_instance_id=runtime_instance_id,
            environment_scope=environment_scope,
            authorized_app_ids=(),
            authorized_capability_scopes=(),
            production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
            source=AstraRuntimeActivationSource.SERVER_CONFIGURATION,
            issued_at=observed_at,
            expires_at=observed_at + timedelta(seconds=1),
        )
    return AstraRuntimeActivationSnapshot(
        activation_id=activation.activation_id,
        activation_version=activation.activation_version,
        status=activation.status if activation.covers(
            runtime_instance_id=runtime_instance_id,
            authority_class=AuthorityClass.ADVISORY,
            safety_classification=SafetyClassification.PRIVATE_READ,
            app_id=SUBSCRIPTION_MANAGER_APP_ID,
            capability_scope=SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
            production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
            provider_requested=False,
            memory_requested=False,
            adaptation_requested=False,
            execution_handoff_requested=False,
            observed_at=observed_at,
        ) else AstraRuntimeActivationStatus.INVALID,
        enabled=activation.enabled,
        runtime_instance_id=activation.runtime_instance_id,
        environment_scope=activation.environment_scope,
        authorized_app_ids=activation.authorized_app_ids,
        authorized_capability_scopes=activation.authorized_capability_scopes,
        production_authorization_state=activation.production_authorization_state,
        source=activation.source,
        issued_at=activation.issued_at,
        expires_at=activation.expires_at,
    )


def activation_digest(value: AstraRuntimeActivationContract) -> str:
    return hashlib.sha256(
        json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _parse_activation_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise AstraRuntimeActivationError("Runtime activation flag must be true or false.")
    normalized = value.strip().lower()
    if normalized in {"false", "0", "no", "off", ""}:
        return False
    if normalized in {"true", "1", "yes", "on"}:
        return True
    raise AstraRuntimeActivationError("Runtime activation flag is malformed.")


def _aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraRuntimeActivationError("Runtime activation timestamp must be timezone-aware.")
