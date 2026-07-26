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
APP_ENVIRONMENT_SCOPES = {
    "local": EnvironmentScope.LOCAL,
    "development": EnvironmentScope.DEVELOPMENT,
    "qa": EnvironmentScope.QA,
    "staging": EnvironmentScope.STAGING,
    "production": EnvironmentScope.PRODUCTION,
}
VERCEL_ENVIRONMENT_SCOPES = {
    "development": None,
    "preview": EnvironmentScope.STAGING,
    "staging": EnvironmentScope.STAGING,
    "production": EnvironmentScope.PRODUCTION,
}


class AstraConfigurationError(ValueError):
    """Raised when Astra configuration identity cannot be safely resolved."""


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
    loaded_at: datetime | None = None,
) -> LoadedAstraConfiguration:
    """Load the disabled-by-default Astra Stage 1 configuration.

    The loader consumes only existing environment identity settings. It never
    accepts arbitrary caller overrides, reads provider keys, model settings,
    secrets, or unrelated environment values.
    """

    environment_scope = _resolve_environment_scope(app_settings)
    payload = _default_configuration_candidate(environment_scope)
    return _load_validated_configuration(
        payload,
        source_class=AstraConfigurationSourceClass.EXISTING_APP_SETTINGS,
        loaded_at=loaded_at,
    )


def _default_configuration_candidate(environment_scope: EnvironmentScope) -> dict[str, Any]:
    return {
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


def _validate_astra_configuration_candidate(
    candidate: Mapping[str, Any],
    *,
    loaded_at: datetime | None = None,
) -> LoadedAstraConfiguration:
    return _load_validated_configuration(
        dict(candidate),
        source_class=AstraConfigurationSourceClass.TEST_OVERRIDE,
        loaded_at=loaded_at,
    )


def _load_validated_configuration(
    payload: Mapping[str, Any],
    *,
    source_class: AstraConfigurationSourceClass,
    loaded_at: datetime | None,
) -> LoadedAstraConfiguration:
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
    if app_env not in APP_ENVIRONMENT_SCOPES:
        raise AstraConfigurationError("Unknown Astra APP_ENV value.")
    if vercel_env and vercel_env not in VERCEL_ENVIRONMENT_SCOPES:
        raise AstraConfigurationError("Unknown Astra VERCEL_ENV value.")
    if vercel_env == "production" or app_env == "production":
        return EnvironmentScope.PRODUCTION
    vercel_scope = VERCEL_ENVIRONMENT_SCOPES.get(vercel_env)
    if vercel_scope is not None:
        return vercel_scope
    return APP_ENVIRONMENT_SCOPES[app_env]
