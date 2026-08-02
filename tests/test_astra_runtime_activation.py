from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.modules.astra_ai.activation import (
    ASTRA_RUNTIME_ACTIVATION_ID,
    ASTRA_RUNTIME_ACTIVATION_VERSION,
    SUBSCRIPTION_MANAGER_APP_ID,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
    AstraRuntimeActivationContract,
    AstraRuntimeActivationError,
    AstraRuntimeActivationSource,
    AstraRuntimeActivationStatus,
    load_runtime_activation,
)
from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION
from app.modules.astra_ai.constitutional_contracts import AstraConfigurationContract
from app.modules.astra_ai.configuration import get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    EnvironmentScope,
    GovernanceOutcome,
    ProductionAuthorizationState,
    RuntimeUseState,
    SafetyClassification,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput, evaluate_governance
from app.modules.astra_ai.runtime import AstraRuntime


NOW = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "7" * 32
REQ = ConstitutionalRequirementReference(
    constitutional_source="ASTRA-010",
    requirement_id="AIR-CM-009",
    requirement_version="1.0.0",
)


def settings_for(*, app_env: str = "development", vercel_env: str | None = None, enabled: str = "false") -> Settings:
    return Settings(APP_ENV=app_env, VERCEL_ENV=vercel_env, ASTRA_NONPROD_READ_ENABLED=enabled)


def activation(
    *,
    runtime_instance_id: str = RUNTIME_ID,
    environment_scope: EnvironmentScope = EnvironmentScope.DEVELOPMENT,
    issued_at: datetime = NOW,
    expires_at: datetime | None = None,
) -> AstraRuntimeActivationContract:
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
        issued_at=issued_at,
        expires_at=expires_at or issued_at + timedelta(minutes=15),
        source=AstraRuntimeActivationSource.TEST_OVERRIDE,
    )


def governance_input(**changes) -> GovernanceEvaluationInput:
    values = dict(
        evaluation_id="RUNTIME-ACT-GOV-001",
        requirement_references=(REQ,),
        requested_authority_class=AuthorityClass.ADVISORY,
        safety_classification=SafetyClassification.PRIVATE_READ,
        approval_state=ApprovalState.NOT_REQUIRED,
        runtime_instance_id=RUNTIME_ID,
        requested_app_id=SUBSCRIPTION_MANAGER_APP_ID,
        requested_capability_scope=SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
        configuration_id=ASTRA_CONFIGURATION_ID,
        configuration_version=ASTRA_CONFIGURATION_VERSION,
        production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
        evaluation_timestamp=NOW,
    )
    values.update(changes)
    return GovernanceEvaluationInput(**values)


def test_activation_defaults_disabled_and_stage_zero_remains_disabled():
    assert load_runtime_activation(
        runtime_instance_id=RUNTIME_ID,
        environment_scope=EnvironmentScope.DEVELOPMENT,
        app_settings=settings_for(),
        loaded_at=NOW,
    ) is None
    configuration = get_astra_configuration().configuration
    assert configuration.feature_enabled is False
    with pytest.raises(ValidationError):
        AstraConfigurationContract(**(configuration.model_dump(mode="json") | {"feature_enabled": True}))


def test_malformed_activation_flag_fails_closed():
    with pytest.raises((AstraRuntimeActivationError, ValidationError)):
        load_runtime_activation(
            runtime_instance_id=RUNTIME_ID,
            environment_scope=EnvironmentScope.DEVELOPMENT,
            app_settings=settings_for(enabled="maybe"),
            loaded_at=NOW,
        )


@pytest.mark.parametrize(
    "environment_scope",
    (
        EnvironmentScope.LOCAL,
        EnvironmentScope.DEVELOPMENT,
        EnvironmentScope.QA,
        EnvironmentScope.STAGING,
    ),
)
def test_nonproduction_activation_loads_for_allowed_environments(environment_scope):
    loaded = load_runtime_activation(
        runtime_instance_id=RUNTIME_ID,
        environment_scope=environment_scope,
        app_settings=settings_for(enabled="true"),
        loaded_at=NOW,
    )
    assert loaded is not None
    assert loaded.enabled is True
    assert loaded.environment_scope is environment_scope
    assert loaded.authorized_app_ids == (SUBSCRIPTION_MANAGER_APP_ID,)
    assert loaded.provider_use is RuntimeUseState.DISABLED
    assert loaded.memory_use is RuntimeUseState.DISABLED
    assert loaded.adaptation_use is RuntimeUseState.DISABLED
    assert loaded.write_use is RuntimeUseState.DISABLED


def test_production_activation_is_always_prohibited():
    assert load_runtime_activation(
        runtime_instance_id=RUNTIME_ID,
        environment_scope=EnvironmentScope.PRODUCTION,
        app_settings=settings_for(enabled="false"),
        loaded_at=NOW,
    ) is None
    with pytest.raises((AstraRuntimeActivationError, ValidationError)):
        load_runtime_activation(
            runtime_instance_id=RUNTIME_ID,
            environment_scope=EnvironmentScope.PRODUCTION,
            app_settings=settings_for(app_env="production", enabled="true"),
            loaded_at=NOW,
        )


def test_unknown_environment_fails_closed_in_stage_zero_loader():
    from app.modules.astra_ai.configuration import load_astra_configuration

    with pytest.raises(Exception):
        load_astra_configuration(app_settings=settings_for(app_env="unknown"), loaded_at=NOW)


def test_real_governance_fails_without_activation_and_allows_exact_valid_activation():
    no_activation = evaluate_governance(governance_input())
    assert no_activation.decision.outcome is GovernanceOutcome.FAIL_CLOSED

    with_activation = evaluate_governance(governance_input(activation_context=activation()))
    assert with_activation.decision.outcome is GovernanceOutcome.ALLOW


@pytest.mark.parametrize(
    "changes",
    (
        {"requested_app_id": "expense_tracker"},
        {"requested_authority_class": AuthorityClass.APPROVAL_REQUIRED},
        {"requested_authority_class": AuthorityClass.PRODUCTION_BOUNDARY},
        {"safety_classification": SafetyClassification.PRIVATE_WRITE},
        {"safety_classification": SafetyClassification.HIGH_IMPACT},
        {"safety_classification": SafetyClassification.EXTERNAL_EXPOSURE},
        {"provider_use_requested": True},
        {"memory_use_requested": True},
        {"adaptation_use_requested": True},
        {"execution_handoff_requested": True},
        {"production_authorization_state": ProductionAuthorizationState.APPROVED},
    ),
)
def test_real_governance_rejects_invalid_activated_scope(changes):
    result = evaluate_governance(governance_input(activation_context=activation(), **changes))
    assert result.decision.outcome is not GovernanceOutcome.ALLOW


def test_real_governance_rejects_foreign_and_expired_activation():
    foreign = evaluate_governance(
        governance_input(activation_context=activation(runtime_instance_id="astra_rt_" + "8" * 32))
    )
    assert foreign.decision.outcome is GovernanceOutcome.FAIL_CLOSED

    expired = evaluate_governance(
        governance_input(
            activation_context=activation(
                issued_at=NOW - timedelta(minutes=20),
                expires_at=NOW - timedelta(minutes=1),
            )
        )
    )
    assert expired.decision.outcome is GovernanceOutcome.FAIL_CLOSED


def test_runtime_owns_loaded_activation_and_ignores_forged_input_context():
    active = activation(runtime_instance_id=RUNTIME_ID)
    forged = activation(runtime_instance_id="astra_rt_" + "9" * 32)
    with patch("app.modules.astra_ai.runtime.load_runtime_activation", return_value=active):
        runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        runtime.startup()
    try:
        snapshot = runtime.health(observed_at=NOW).activation
        assert snapshot is not None
        assert snapshot.status is AstraRuntimeActivationStatus.ACTIVE
        result = runtime.evaluate_governance(governance_input(activation_context=forged))
        assert result.decision.outcome is GovernanceOutcome.ALLOW
    finally:
        runtime.shutdown()


def test_runtime_without_loaded_activation_keeps_governance_fail_closed():
    with patch("app.modules.astra_ai.runtime.load_runtime_activation", return_value=None):
        runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        runtime.startup()
    try:
        snapshot = runtime.activation
        assert snapshot.status is AstraRuntimeActivationStatus.DISABLED
        result = runtime.evaluate_governance(governance_input())
        assert result.decision.outcome is GovernanceOutcome.FAIL_CLOSED
    finally:
        runtime.shutdown()
