from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from enum import StrEnum
from functools import lru_cache
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import Settings, settings
from app.modules.astra_ai.constitutional_contracts import (
    AstraConfigurationContract,
    AuditEvidenceBehavior,
    EnvironmentScope,
    ImplementationPhase,
    ProductionAuthorizationState,
    RuntimeUseState,
)


ASTRA_CONFIGURATION_ID = "ASTRA-CONFIG-002"
ASTRA_CONFIGURATION_VERSION = "1.0.0"


class AstraConfigurationSourceClass(StrEnum):
    SERVER_DEFAULTS = "server_defaults"
    EXISTING_APP_SETTINGS = "existing_app_settings"
    TEST_OVERRIDE = "test_override"


class AstraConfigurationValidationResult(StrEnum):
    PASSED = "passed"


class AstraConfigurationProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    configuration_id: str
    configuration_version: str
    environment_scope: EnvironmentScope
    source_class: AstraConfigurationSourceClass
    loaded_at: datetime
    validation_result: AstraConfigurationValidationResult


class LoadedAstraConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    configuration: AstraConfigurationContract
    provenance: AstraConfigurationProvenance


def load_astra_configuration(
    *,
    app_settings: Settings = settings,
    overrides: Mapping[str, Any] | None = None,
    loaded_at: datetime | None = None,
) -> LoadedAstraConfiguration:
    """Load the disabled-by-default Astra Stage 1 configuration.

    The loader consumes only existing environment identity settings and
    optional explicit test overrides. It never reads provider keys, model
    settings, secrets, or unrelated environment values.
    """

    environment_scope = _resolve_environment_scope(app_settings)
    payload: dict[str, Any] = {
        "configuration_id": ASTRA_CONFIGURATION_ID,
        "feature_enabled": False,
        "environment_scope": environment_scope,
        "implementation_phase": ImplementationPhase.ASTRA_IMP_002,
        "production_authorization_state": ProductionAuthorizationState.NOT_APPROVED,
        "provider_use": RuntimeUseState.DISABLED,
        "memory_use": RuntimeUseState.DISABLED,
        "adaptation_use": RuntimeUseState.DISABLED,
        "execution_handoff": RuntimeUseState.DISABLED,
        "audit_evidence_behavior": AuditEvidenceBehavior.METADATA_ONLY,
        "fail_closed_default": True,
        "configuration_version": ASTRA_CONFIGURATION_VERSION,
    }
    source_class = AstraConfigurationSourceClass.EXISTING_APP_SETTINGS
    if overrides is not None:
        payload.update(dict(overrides))
        source_class = AstraConfigurationSourceClass.TEST_OVERRIDE

    configuration = AstraConfigurationContract(**payload)
    timestamp = loaded_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Astra configuration load timestamp must be timezone-aware.")

    return LoadedAstraConfiguration(
        configuration=configuration,
        provenance=AstraConfigurationProvenance(
            configuration_id=configuration.configuration_id,
            configuration_version=configuration.configuration_version,
            environment_scope=configuration.environment_scope,
            source_class=source_class,
            loaded_at=timestamp,
            validation_result=AstraConfigurationValidationResult.PASSED,
        ),
    )


@lru_cache(maxsize=1)
def _authoritative_astra_configuration() -> LoadedAstraConfiguration:
    return load_astra_configuration()


def get_astra_configuration() -> LoadedAstraConfiguration:
    """Return copy-safe validated configuration for future internal components."""

    return deepcopy(_authoritative_astra_configuration())


def _resolve_environment_scope(app_settings: Settings) -> EnvironmentScope:
    vercel_env = (app_settings.VERCEL_ENV or "").strip().lower()
    app_env = app_settings.APP_ENV.strip().lower()
    if vercel_env == "production" or app_env == "production":
        return EnvironmentScope.PRODUCTION
    if vercel_env in {"preview", "staging"} or app_env == "staging":
        return EnvironmentScope.STAGING
    if app_env == "qa":
        return EnvironmentScope.QA
    if app_env == "local":
        return EnvironmentScope.LOCAL
    return EnvironmentScope.DEVELOPMENT
