from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.config import Settings, settings
from app.modules.astra_ai.configuration import (
    ASTRA_CONFIGURATION_ID,
    ASTRA_CONFIGURATION_VERSION,
    AstraConfigurationSourceClass,
    AstraConfigurationValidationResult,
    _default_configuration_candidate,
    _validate_astra_configuration_candidate,
    get_astra_configuration,
    load_astra_configuration,
)
from app.modules.astra_ai.constitutional_contracts import (
    AuditEvidenceBehavior,
    EnvironmentScope,
    ImplementationPhase,
    ProductionAuthorizationState,
    RuntimeUseState,
)


def app_settings(app_env: str, vercel_env: str | None = None, **overrides):
    return Settings(APP_ENV=app_env, VERCEL_ENV=vercel_env, **overrides)


def candidate(**overrides):
    values = _default_configuration_candidate(EnvironmentScope.QA)
    values.update(overrides)
    return values


class AstraConfigurationFoundationTests(unittest.TestCase):
    def test_default_configuration_is_disabled_and_fail_closed(self):
        loaded = load_astra_configuration(
            app_settings=app_settings("development"),
            loaded_at=datetime(2026, 7, 26, tzinfo=timezone.utc),
        )
        config = loaded.configuration

        self.assertEqual(config.configuration_id, ASTRA_CONFIGURATION_ID)
        self.assertEqual(config.configuration_version, ASTRA_CONFIGURATION_VERSION)
        self.assertEqual(config.implementation_phase, ImplementationPhase.ASTRA_IMP_002)
        self.assertFalse(config.feature_enabled)
        self.assertTrue(config.fail_closed_default)
        self.assertEqual(config.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)
        self.assertEqual(config.provider_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.memory_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.adaptation_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.execution_handoff, RuntimeUseState.DISABLED)
        self.assertEqual(config.audit_evidence_behavior, AuditEvidenceBehavior.METADATA_ONLY)

    def test_every_supported_environment_loads_disabled(self):
        cases = (
            ("local", None, EnvironmentScope.LOCAL),
            ("development", None, EnvironmentScope.DEVELOPMENT),
            ("qa", None, EnvironmentScope.QA),
            ("staging", None, EnvironmentScope.STAGING),
            ("development", "", EnvironmentScope.DEVELOPMENT),
            ("qa", "development", EnvironmentScope.QA),
            ("development", "preview", EnvironmentScope.STAGING),
            ("qa", "staging", EnvironmentScope.STAGING),
            ("production", None, EnvironmentScope.PRODUCTION),
            ("development", "production", EnvironmentScope.PRODUCTION),
        )

        for app_env, vercel_env, expected_scope in cases:
            with self.subTest(app_env=app_env, vercel_env=vercel_env):
                loaded = load_astra_configuration(app_settings=app_settings(app_env, vercel_env))

                self.assertEqual(loaded.configuration.environment_scope, expected_scope)
                self.assertFalse(loaded.configuration.feature_enabled)
                self.assertEqual(
                    loaded.configuration.production_authorization_state,
                    ProductionAuthorizationState.NOT_APPROVED,
                )
                self.assertEqual(loaded.configuration.provider_use, RuntimeUseState.DISABLED)
                self.assertEqual(loaded.configuration.memory_use, RuntimeUseState.DISABLED)
                self.assertEqual(loaded.configuration.adaptation_use, RuntimeUseState.DISABLED)
                self.assertEqual(loaded.configuration.execution_handoff, RuntimeUseState.DISABLED)
                self.assertTrue(loaded.configuration.fail_closed_default)

    def test_production_environment_does_not_infer_authorization(self):
        loaded = load_astra_configuration(app_settings=app_settings("production"))

        self.assertEqual(loaded.configuration.environment_scope, EnvironmentScope.PRODUCTION)
        self.assertFalse(loaded.configuration.feature_enabled)
        self.assertEqual(loaded.configuration.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)

    def test_unknown_app_env_fails_closed(self):
        with self.assertRaises(ValueError):
            load_astra_configuration(app_settings=app_settings("unknown"))

    def test_misspelled_production_app_env_fails_closed(self):
        with self.assertRaises(ValueError):
            load_astra_configuration(app_settings=app_settings("prodution"))

    def test_unknown_vercel_env_fails_closed(self):
        with self.assertRaises(ValueError):
            load_astra_configuration(app_settings=app_settings("development", "unexpected-value"))

    def test_public_loader_exposes_no_arbitrary_override_path(self):
        signature = inspect.signature(load_astra_configuration)

        self.assertNotIn("overrides", signature.parameters)
        with self.assertRaises(TypeError):
            load_astra_configuration(
                app_settings=app_settings("production"),
                overrides={"environment_scope": "local"},
            )

    def test_environment_scope_comes_only_from_authoritative_settings(self):
        loaded = load_astra_configuration(app_settings=app_settings("production"))

        self.assertEqual(loaded.configuration.environment_scope, EnvironmentScope.PRODUCTION)
        self.assertEqual(loaded.provenance.environment_scope, EnvironmentScope.PRODUCTION)

    def test_configuration_identity_cannot_be_caller_overridden(self):
        loaded = load_astra_configuration(app_settings=app_settings("qa"))

        self.assertEqual(loaded.configuration.configuration_id, ASTRA_CONFIGURATION_ID)
        self.assertEqual(loaded.configuration.configuration_version, ASTRA_CONFIGURATION_VERSION)
        self.assertEqual(loaded.configuration.implementation_phase, ImplementationPhase.ASTRA_IMP_002)

    def test_unknown_fields_fail(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(provider_model="gpt-x"))

    def test_invalid_enum_values_fail(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(provider_use="enabled"))

    def test_provider_memory_adaptation_and_execution_cannot_be_enabled(self):
        for field in ("provider_use", "memory_use", "adaptation_use", "execution_handoff"):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    _validate_astra_configuration_candidate(candidate(**{field: "enabled"}))

    def test_feature_activation_cannot_be_enabled(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(feature_enabled=True))

    def test_production_authorization_cannot_be_inferred_or_overridden(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(
                candidate(
                    environment_scope=EnvironmentScope.PRODUCTION,
                    production_authorization_state="approved",
                )
            )

    def test_malformed_identifiers_and_versions_fail(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(configuration_id="bad-id"))

        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(configuration_version="1"))

    def test_non_fail_closed_configuration_fails(self):
        with self.assertRaises(ValidationError):
            _validate_astra_configuration_candidate(candidate(fail_closed_default=False))

    def test_provenance_is_bounded_and_contains_no_raw_secret_values(self):
        loaded = load_astra_configuration(
            app_settings=app_settings("qa", OPENAI_API_KEY="sk-secret", TURSO_AUTH_TOKEN="db-token"),
            loaded_at=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
        )
        payload = loaded.model_dump_json()

        self.assertEqual(loaded.provenance.configuration_id, ASTRA_CONFIGURATION_ID)
        self.assertEqual(loaded.provenance.configuration_version, ASTRA_CONFIGURATION_VERSION)
        self.assertEqual(loaded.provenance.environment_scope, EnvironmentScope.QA)
        self.assertEqual(loaded.provenance.source_class, AstraConfigurationSourceClass.EXISTING_APP_SETTINGS)
        self.assertEqual(loaded.provenance.validation_result, AstraConfigurationValidationResult.PASSED)
        self.assertNotIn("sk-secret", payload)
        self.assertNotIn("db-token", payload)
        self.assertNotIn("OPENAI_API_KEY", payload)
        self.assertNotIn("TURSO_AUTH_TOKEN", payload)

    def test_naive_load_timestamp_fails(self):
        with self.assertRaises(ValueError):
            load_astra_configuration(
                app_settings=app_settings("qa"),
                loaded_at=datetime(2026, 7, 26, 12, 0),
            )

    def test_access_returns_validated_copy_safe_configuration(self):
        first = get_astra_configuration()
        first.configuration.feature_enabled = True

        second = get_astra_configuration()

        self.assertFalse(second.configuration.feature_enabled)
        self.assertEqual(second.configuration.implementation_phase, ImplementationPhase.ASTRA_IMP_002)
        self.assertEqual(second.provenance.validation_result, AstraConfigurationValidationResult.PASSED)

    def test_existing_application_settings_remain_backward_compatible(self):
        self.assertIsInstance(settings.APP_ENV, str)
        self.assertIsInstance(settings.ASTRA_PERSONAL_DATA_TOOLS_ENABLED, bool)
        self.assertTrue(hasattr(settings, "ASSISTANT_OPENAI_ENABLED"))


if __name__ == "__main__":
    unittest.main()
