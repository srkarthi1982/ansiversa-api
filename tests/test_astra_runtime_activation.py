from __future__ import annotations

from datetime import datetime, timezone
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
    AstraRuntimeActivationIssuer,
    AstraRuntimeActivationSource,
    AstraRuntimeActivationStatus,
    activation_digest,
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
) -> AstraRuntimeActivationContract:
    return AstraRuntimeActivationContract(
        activation_id=ASTRA_RUNTIME_ACTIVATION_ID,
        activation_version=ASTRA_RUNTIME_ACTIVATION_VERSION,
        activation_instance_id="astra_act_" + "1" * 32,
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
        source=AstraRuntimeActivationSource.SERVER_CONFIGURATION,
        issuer_reference="runtime-activation:test",
    )


def issued_activation(
    *,
    runtime_instance_id: str = RUNTIME_ID,
    environment_scope: EnvironmentScope = EnvironmentScope.DEVELOPMENT,
    issued_at: datetime = NOW,
) -> AstraRuntimeActivationContract:
    issuer = AstraRuntimeActivationIssuer(
        runtime_instance_id=runtime_instance_id,
        issuer_reference="runtime-activation:test",
        _runtime_authority=object(),
    )
    return issuer.issue(environment_scope=environment_scope, issued_at=issued_at)


def activation_context_values(value: AstraRuntimeActivationContract) -> dict[str, object]:
    return {
        "activation_context": value,
        "activation_reference": value.activation_reference,
        "activation_digest": f"sha256:{activation_digest(value)}",
    }


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
        activation_reference=None,
        activation_digest=None,
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
    issuer = AstraRuntimeActivationIssuer(
        runtime_instance_id=RUNTIME_ID,
        issuer_reference="runtime-activation:test",
        _runtime_authority=object(),
    )
    loaded = load_runtime_activation(
        runtime_instance_id=RUNTIME_ID,
        environment_scope=environment_scope,
        app_settings=settings_for(enabled="true"),
        loaded_at=NOW,
        activation_issuer=issuer,
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
            activation_issuer=AstraRuntimeActivationIssuer(
                runtime_instance_id=RUNTIME_ID,
                issuer_reference="runtime-activation:test",
                _runtime_authority=object(),
            ),
        )


def test_unknown_environment_fails_closed_in_stage_zero_loader():
    from app.modules.astra_ai.configuration import load_astra_configuration

    with pytest.raises(Exception):
        load_astra_configuration(app_settings=settings_for(app_env="unknown"), loaded_at=NOW)


def test_real_governance_fails_without_activation_and_allows_exact_valid_activation():
    no_activation = evaluate_governance(governance_input())
    assert no_activation.decision.outcome is GovernanceOutcome.FAIL_CLOSED

    exact = issued_activation()
    with_activation = evaluate_governance(governance_input(**activation_context_values(exact)))
    assert with_activation.decision.outcome is GovernanceOutcome.ALLOW


def test_reconstructed_and_copied_activation_do_not_authorize_direct_governance():
    reconstructed = activation()
    assert evaluate_governance(
        governance_input(**activation_context_values(reconstructed))
    ).decision.outcome is GovernanceOutcome.FAIL_CLOSED

    exact = issued_activation()
    copied = exact.model_copy()
    assert evaluate_governance(
        governance_input(**activation_context_values(copied))
    ).decision.outcome is GovernanceOutcome.FAIL_CLOSED

    tampered = exact.model_copy(update={"requested_app_id": "subscription_manager"})
    assert evaluate_governance(
        governance_input(**activation_context_values(tampered))
    ).decision.outcome is GovernanceOutcome.FAIL_CLOSED


def test_modified_activation_reference_or_digest_fails():
    exact = issued_activation()
    assert evaluate_governance(
        governance_input(
            **(
                activation_context_values(exact)
                | {"activation_reference": "ASTRA-RUNTIME-ACT-001:1.0.0:astra_rt_77777777777777777777777777777777:astra_act_22222222222222222222222222222222"}
            )
        )
    ).decision.outcome is GovernanceOutcome.FAIL_CLOSED
    assert evaluate_governance(
        governance_input(
            **(
                activation_context_values(exact)
                | {"activation_digest": "sha256:" + "0" * 64}
            )
        )
    ).decision.outcome is GovernanceOutcome.FAIL_CLOSED


def test_activation_evidence_contains_safe_provenance_without_authority_material():
    exact = issued_activation()
    result = evaluate_governance(governance_input(**activation_context_values(exact)))
    assert result.decision.outcome is GovernanceOutcome.ALLOW
    assert exact.activation_reference in result.evidence.integrity.provenance_reference
    payload = result.evidence.model_dump_json()
    assert exact.activation_reference in payload
    assert f"sha256:{activation_digest(exact)}" in governance_input(**activation_context_values(exact)).model_dump_json()
    assert "_runtime_activation_issuer" not in payload
    assert "runtime_authority" not in payload


def test_no_activation_evidence_does_not_claim_activation():
    result = evaluate_governance(governance_input())
    assert result.decision.outcome is GovernanceOutcome.FAIL_CLOSED
    assert "ASTRA-RUNTIME-ACT-001" not in result.evidence.integrity.provenance_reference


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
    result = evaluate_governance(governance_input(**activation_context_values(issued_activation()), **changes))
    assert result.decision.outcome is not GovernanceOutcome.ALLOW


def test_real_governance_rejects_foreign_activation():
    foreign = evaluate_governance(
        governance_input(**activation_context_values(issued_activation(runtime_instance_id="astra_rt_" + "8" * 32)))
    )
    assert foreign.decision.outcome is GovernanceOutcome.FAIL_CLOSED


def test_runtime_owns_loaded_activation_and_ignores_forged_input_context():
    forged = issued_activation(runtime_instance_id="astra_rt_" + "9" * 32)

    def enabled_loader(**values):
        return load_runtime_activation(
            **values,
            app_settings=settings_for(enabled="true"),
        )

    with patch("app.modules.astra_ai.runtime.load_runtime_activation", side_effect=enabled_loader):
        runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        runtime.startup()
    try:
        snapshot = runtime.health(observed_at=NOW).activation
        assert snapshot is not None
        assert snapshot.status is AstraRuntimeActivationStatus.ACTIVE
        result = runtime.evaluate_governance(governance_input(**activation_context_values(forged)))
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


def test_runtime_lifecycle_bound_activation_remains_available_and_shutdown_invalidates_it():
    captured: dict[str, AstraRuntimeActivationContract] = {}

    def enabled_loader(**values):
        result = load_runtime_activation(
            **values,
            app_settings=settings_for(enabled="true"),
        )
        captured["activation"] = result
        return result

    with patch("app.modules.astra_ai.runtime.load_runtime_activation", side_effect=enabled_loader):
        runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        runtime.startup()
    exact = captured["activation"]
    try:
        later = datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc)
        result = runtime.evaluate_governance(governance_input(evaluation_timestamp=later))
        assert result.decision.outcome is GovernanceOutcome.ALLOW
    finally:
        runtime.shutdown()

    after_shutdown = evaluate_governance(governance_input(**activation_context_values(exact)))
    assert after_shutdown.decision.outcome is GovernanceOutcome.FAIL_CLOSED
