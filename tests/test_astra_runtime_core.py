from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pydantic import ValidationError

from app.modules.astra_ai import configuration as configuration_module
from app.modules.astra_ai import runtime as runtime_module
from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION
from app.modules.astra_ai.constitutional_contracts import (
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    GovernanceOutcome,
    ProductionAuthorizationState,
    RuntimeUseState,
    SafetyClassification,
)
from app.modules.astra_ai.governance import GovernanceEvaluationInput
from app.modules.astra_ai.runtime import (
    ASTRA_CONSTITUTIONAL_BASELINE,
    ASTRA_RUNTIME_IMPLEMENTATION_PHASE,
    AstraRuntime,
    AstraRuntimeComponentIdentifier,
    AstraRuntimeError,
    AstraRuntimeFaultClassification,
    AstraRuntimeHealthOutcome,
    AstraRuntimeState,
    _ComponentRegistry,
)


TIMESTAMP = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
INSTANCE_ID = "astra_rt_" + "a" * 32


def requirement():
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-CM-009",
        requirement_version="1.0.0",
    )


def governance_input(evaluation_id="GOV-EVAL-001"):
    return GovernanceEvaluationInput(
        evaluation_id=evaluation_id,
        requirement_references=(requirement(),),
        requested_authority_class=AuthorityClass.READ_ONLY,
        safety_classification=SafetyClassification.PUBLIC,
        approval_state=ApprovalState.NOT_REQUIRED,
        configuration_id=ASTRA_CONFIGURATION_ID,
        configuration_version=ASTRA_CONFIGURATION_VERSION,
        production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
        evaluation_timestamp=TIMESTAMP,
    )


class FailingStartupRuntime(AstraRuntime):
    def _load_configuration(self):
        raise ValueError("api_key:secret raw_prompt hidden_reasoning")


class FailingEvidenceRuntime(AstraRuntime):
    def _create_evidence_sink(self, loaded_configuration):
        raise ValueError("postgresql://secret")


class AstraRuntimeCoreTests(unittest.TestCase):
    def test_runtime_starts_uninitialized_with_immutable_safe_identity(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        self.assertEqual(runtime.state, AstraRuntimeState.UNINITIALIZED)
        self.assertEqual(runtime.identity.runtime_id, "ASTRA-RUNTIME-005")
        self.assertEqual(runtime.identity.constitutional_baseline, ASTRA_CONSTITUTIONAL_BASELINE)
        self.assertEqual(runtime.identity.implementation_phase, ASTRA_RUNTIME_IMPLEMENTATION_PHASE)

        with self.assertRaises(ValidationError):
            runtime.identity.runtime_name = "Mutated"

    def test_constructing_runtime_does_not_load_authoritative_configuration(self):
        with patch("app.modules.astra_ai.runtime.get_astra_configuration") as loader:
            runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        loader.assert_not_called()
        self.assertEqual(runtime.state, AstraRuntimeState.UNINITIALIZED)
        self.assertIsNone(runtime.health(observed_at=TIMESTAMP).startup_metadata)

    def test_startup_registers_only_authorized_foundation_components(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        health = runtime.startup()

        self.assertEqual(runtime.state, AstraRuntimeState.READY)
        self.assertEqual(health.health_outcome, AstraRuntimeHealthOutcome.HEALTHY)
        self.assertEqual(
            runtime.registered_component_identifiers,
            (
                AstraRuntimeComponentIdentifier.CONFIGURATION,
                AstraRuntimeComponentIdentifier.GOVERNANCE,
                AstraRuntimeComponentIdentifier.EVIDENCE_SINK,
                AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY,
            ),
        )
        self.assertEqual(
            tuple(registration.implementation_reference for registration in runtime.component_registrations),
            ("ASTRA-IMP-002", "ASTRA-IMP-003", "ASTRA-IMP-004", "ASTRA-IMP-007"),
        )

    def test_governance_component_decides_but_disabled_configuration_does_not_allow(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()

        result = runtime.governance.evaluate(governance_input())

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.evidence_references, (result.evidence.evidence_id,))

    def test_runtime_bound_governance_evaluation_enforces_ready_state(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime.evaluate_governance(governance_input())

        runtime.startup()
        result = runtime.evaluate_governance(governance_input())
        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_evidence_sink_is_runtime_owned_and_receives_bounded_evidence(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()
        result = runtime.governance.evaluate(governance_input())

        returned = runtime.evidence_sink.append(result.evidence)

        self.assertEqual(returned, result.evidence)
        self.assertEqual(runtime.evidence_sink.count(), 1)

    def test_runtime_bound_evidence_operations_enforce_ready_state(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime.evidence_count()
        with self.assertRaises(AstraRuntimeError):
            runtime.retrieve_evidence()

        runtime.startup()
        result = runtime.evaluate_governance(governance_input())
        runtime.append_evidence(result.evidence)

        self.assertEqual(runtime.evidence_count(), 1)
        self.assertEqual(runtime.retrieve_evidence(), (result.evidence,))

    def test_component_access_requires_ready_state(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            _ = runtime.configuration
        with self.assertRaises(AstraRuntimeError):
            runtime.governance.evaluate(governance_input())
        with self.assertRaises(AstraRuntimeError):
            runtime.evidence_sink.count()

    def test_configuration_access_is_copy_safe_and_cannot_mutate_authority(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()

        returned = runtime.configuration
        returned.configuration.feature_enabled = True

        self.assertFalse(runtime.configuration.configuration.feature_enabled)
        self.assertFalse(runtime.configuration.configuration.provider_use is not RuntimeUseState.DISABLED)

    def test_configuration_remains_disabled_and_non_production_authorized(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()
        configuration = runtime.configuration.configuration

        self.assertFalse(configuration.feature_enabled)
        self.assertEqual(configuration.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)
        self.assertEqual(configuration.provider_use, RuntimeUseState.DISABLED)
        self.assertEqual(configuration.memory_use, RuntimeUseState.DISABLED)
        self.assertEqual(configuration.adaptation_use, RuntimeUseState.DISABLED)
        self.assertEqual(configuration.execution_handoff, RuntimeUseState.DISABLED)
        self.assertTrue(configuration.fail_closed_default)

    def test_startup_loads_configuration_once_and_health_uses_validated_metadata(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        configuration_module._authoritative_astra_configuration.cache_clear()

        with patch(
            "app.modules.astra_ai.configuration.load_astra_configuration",
            wraps=configuration_module.load_astra_configuration,
        ) as loader:
            health = runtime.startup()

        loader.assert_called_once()
        self.assertIsNotNone(health.startup_metadata)
        self.assertEqual(health.startup_metadata.configuration_id, ASTRA_CONFIGURATION_ID)
        self.assertEqual(health.startup_metadata.configuration_version, ASTRA_CONFIGURATION_VERSION)
        self.assertEqual(health.environment_scope, runtime.configuration.configuration.environment_scope)
        self.assertEqual(health.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)

    def test_startup_failure_fails_closed_without_partial_ready_or_secret_fault(self):
        runtime = FailingStartupRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime.startup()

        health = runtime.health(observed_at=TIMESTAMP)
        self.assertEqual(runtime.state, AstraRuntimeState.FAULTED)
        self.assertEqual(health.health_outcome, AstraRuntimeHealthOutcome.FAULTED)
        self.assertFalse(health.configuration_loaded)
        self.assertFalse(health.governance_available)
        self.assertFalse(health.evidence_sink_available)
        self.assertFalse(health.capability_discovery_available)
        self.assertIsNone(health.startup_metadata)
        self.assertIsNone(health.environment_scope)
        self.assertIsNone(health.production_authorization_state)
        self.assertEqual(health.fault.classification, AstraRuntimeFaultClassification.STARTUP_FAILURE)
        self.assertNotIn("api_key", health.model_dump_json())
        self.assertNotIn("raw_prompt", health.model_dump_json())

    def test_evidence_sink_creation_failure_never_reaches_partial_ready(self):
        runtime = FailingEvidenceRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime.startup()

        health = runtime.health(observed_at=TIMESTAMP)
        self.assertEqual(runtime.state, AstraRuntimeState.FAULTED)
        self.assertFalse(health.configuration_loaded)
        self.assertFalse(health.governance_available)
        self.assertFalse(health.evidence_sink_available)
        self.assertFalse(health.capability_discovery_available)

    def test_repeated_startup_and_restart_are_rejected(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()

        with self.assertRaises(AstraRuntimeError):
            runtime.startup()

        runtime.shutdown()
        with self.assertRaises(AstraRuntimeError):
            runtime.startup()

    def test_shutdown_releases_components_and_enters_stopped(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()

        health = runtime.shutdown()

        self.assertEqual(runtime.state, AstraRuntimeState.STOPPED)
        self.assertEqual(health.health_outcome, AstraRuntimeHealthOutcome.STOPPED)
        self.assertFalse(health.configuration_loaded)
        self.assertFalse(health.capability_discovery_available)
        self.assertEqual(runtime.registered_component_identifiers, ())
        self.assertIsNone(health.startup_metadata)

    def test_shutdown_from_faulted_is_available_for_safe_cleanup(self):
        runtime = FailingStartupRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        with self.assertRaises(AstraRuntimeError):
            runtime.startup()

        health = runtime.shutdown()

        self.assertEqual(runtime.state, AstraRuntimeState.STOPPED)
        self.assertEqual(health.health_outcome, AstraRuntimeHealthOutcome.STOPPED)

    def test_shutdown_from_invalid_states_fails_deterministically(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime.shutdown()

        runtime.startup()
        runtime.shutdown()
        with self.assertRaises(AstraRuntimeError):
            runtime.shutdown()

    def test_invalid_lifecycle_transition_is_rejected(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)

        with self.assertRaises(AstraRuntimeError):
            runtime._transition_to(AstraRuntimeState.READY)

        self.assertEqual(runtime.state, AstraRuntimeState.UNINITIALIZED)

    def test_component_registry_rejects_unknown_duplicate_and_sealed_mutation(self):
        registry = _ComponentRegistry()

        with self.assertRaises(AstraRuntimeError):
            registry.register(
                component_identifier="provider",  # type: ignore[arg-type]
                component_type="Provider",
                implementation_reference="ASTRA-IMP-005",
                certified_parent_reference="Unauthorized",
                registered_at=TIMESTAMP,
            )

        registry.register(
            component_identifier=AstraRuntimeComponentIdentifier.CONFIGURATION,
            component_type="LoadedAstraConfiguration",
            implementation_reference="ASTRA-IMP-002",
            certified_parent_reference="ASTRA-IMP-002 Certified / Approved",
            registered_at=TIMESTAMP,
        )
        with self.assertRaises(AstraRuntimeError):
            registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.CONFIGURATION,
                component_type="ReplacementConfiguration",
                implementation_reference="ASTRA-IMP-002",
                certified_parent_reference="ASTRA-IMP-002 Certified / Approved",
                registered_at=TIMESTAMP,
            )

    def test_component_registry_must_be_complete_before_sealing(self):
        registry = _ComponentRegistry()

        with self.assertRaises(AstraRuntimeError):
            registry.seal()

    def test_component_registry_cannot_mutate_after_ready(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()

        with self.assertRaises(AstraRuntimeError):
            runtime._registry.register(
                component_identifier=AstraRuntimeComponentIdentifier.CONFIGURATION,
                component_type="ReplacementConfiguration",
                implementation_reference="ASTRA-IMP-002",
                certified_parent_reference="ASTRA-IMP-002 Certified / Approved",
                registered_at=TIMESTAMP,
            )

    def test_health_outcomes_are_structural(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        self.assertEqual(runtime.health(observed_at=TIMESTAMP).health_outcome, AstraRuntimeHealthOutcome.STOPPED)

        runtime.startup()
        self.assertEqual(runtime.health(observed_at=TIMESTAMP).health_outcome, AstraRuntimeHealthOutcome.HEALTHY)

        runtime._evidence_sink = None
        degraded = runtime.health(observed_at=TIMESTAMP)
        self.assertEqual(degraded.health_outcome, AstraRuntimeHealthOutcome.DEGRADED)
        self.assertFalse(degraded.evidence_sink_available)

        runtime._evidence_sink = object()
        runtime._capability_discovery = None
        degraded = runtime.health(observed_at=TIMESTAMP)
        self.assertEqual(degraded.health_outcome, AstraRuntimeHealthOutcome.DEGRADED)
        self.assertFalse(degraded.capability_discovery_available)

    def test_handles_obtained_before_shutdown_cannot_operate_after_shutdown(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()
        governance = runtime.governance
        evidence = runtime.evidence_sink
        result = governance.evaluate(governance_input())

        runtime.shutdown()

        with self.assertRaises(AstraRuntimeError):
            governance.evaluate(governance_input("GOV-EVAL-002"))
        with self.assertRaises(AstraRuntimeError):
            evidence.append(result.evidence)
        with self.assertRaises(AstraRuntimeError):
            evidence.retrieve()
        with self.assertRaises(AstraRuntimeError):
            evidence.count()
        with self.assertRaises(AstraRuntimeError):
            runtime.capability_discovery.health(observed_at=TIMESTAMP)

    def test_shutdown_prevents_all_later_component_operations(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id=INSTANCE_ID)
        runtime.startup()
        runtime.shutdown()

        with self.assertRaises(AstraRuntimeError):
            runtime.evaluate_governance(governance_input())
        with self.assertRaises(AstraRuntimeError):
            runtime.evidence_count()
        with self.assertRaises(AstraRuntimeError):
            runtime.retrieve_evidence()
        with self.assertRaises(AstraRuntimeError):
            runtime.capability_discovery.health(observed_at=TIMESTAMP)

    def test_multiple_runtimes_have_isolated_evidence_sinks(self):
        first = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "b" * 32)
        second = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "c" * 32)
        first.startup()
        second.startup()

        first.append_evidence(first.evaluate_governance(governance_input("GOV-EVAL-001")).evidence)

        self.assertEqual(first.evidence_count(), 1)
        self.assertEqual(second.evidence_count(), 0)
        self.assertIsNot(first.evidence_sink, second.evidence_sink)

    def test_one_runtime_interface_cannot_operate_on_another_runtime_components(self):
        first = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "f" * 32)
        second = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "1" * 32)
        first.startup()
        second.startup()
        first_interface = first.evidence_sink
        first.shutdown()

        with self.assertRaises(AstraRuntimeError):
            first_interface.count()

        self.assertEqual(second.evidence_count(), 0)

    def test_one_runtime_cannot_mutate_another_runtime_state(self):
        first = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "d" * 32)
        second = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "e" * 32)
        first.startup()
        second.startup()

        first.shutdown()

        self.assertEqual(first.state, AstraRuntimeState.STOPPED)
        self.assertEqual(second.state, AstraRuntimeState.READY)

    def test_runtime_module_does_not_import_external_surfaces(self):
        source = inspect.getsource(runtime_module).lower()

        for forbidden in (
            "from fastapi",
            "import fastapi",
            "sqlalchemy",
            "app.modules.audit",
            "openai",
            "anthropic",
            "tool_executor",
            "alembic",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
