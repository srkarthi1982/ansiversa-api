from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.modules.astra_ai import capability_discovery as capability_module
from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryEngine,
    AstraCapabilityDiscoveryError,
    AstraCapabilityExecutionAuthority,
    AstraCapabilityHealthOutcome,
    AstraCapabilityMetadata,
    AstraCapabilityRegistry,
    AstraCapabilityStatus,
    AstraCapabilityType,
    AstraCapabilityVisibility,
)
from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, GovernanceOutcome
from app.modules.astra_ai.conversation_context import AstraConversationContextEngine
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeComponentIdentifier, AstraRuntimeError


TIMESTAMP = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)


def ready_runtime(instance_suffix: str = "a", *, evidence_sink_capacity: int = 50) -> AstraRuntime:
    runtime = AstraRuntime(
        created_at=TIMESTAMP,
        startup_instance_id="astra_rt_" + instance_suffix * 32,
        evidence_sink_capacity=evidence_sink_capacity,
    )
    runtime.startup()
    return runtime


def requirement() -> ConstitutionalRequirementReference:
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-004",
        requirement_id="AIR-CAP-001",
        requirement_version="1.0.0",
    )


def capability(
    capability_id: str,
    *,
    name: str | None = None,
    visibility: AstraCapabilityVisibility = AstraCapabilityVisibility.INTERNAL,
    status: AstraCapabilityStatus = AstraCapabilityStatus.AVAILABLE,
) -> AstraCapabilityMetadata:
    return AstraCapabilityMetadata(
        capability_id=capability_id,
        capability_name=name or capability_id.replace("_", " ").title(),
        capability_type=AstraCapabilityType.PLATFORM_METADATA,
        owning_module="app.modules.astra_ai.capability_discovery",
        version="1.0.0",
        status=status,
        visibility=visibility,
        governance_reference=requirement(),
        execution_authority=AstraCapabilityExecutionAuthority.METADATA_ONLY,
        description=f"Metadata-only discovery record for {capability_id}.",
    )


class AstraCapabilityDiscoveryEngineTests(unittest.TestCase):
    def test_capability_model_is_immutable_metadata_only(self):
        metadata = capability("cap_registry_alpha_0001")

        self.assertEqual(metadata.execution_authority, AstraCapabilityExecutionAuthority.METADATA_ONLY)
        self.assertNotIn("handler", metadata.model_dump())
        self.assertNotIn("callable", metadata.model_dump())
        with self.assertRaises(ValidationError):
            metadata.capability_name = "Mutated"

    def test_registry_registration_and_discovery_order_are_deterministic(self):
        registry = AstraCapabilityRegistry(
            (
                capability("cap_registry_gamma_0001"),
                capability("cap_registry_alpha_0001"),
                capability("cap_registry_beta_0001"),
            )
        )

        self.assertEqual(
            tuple(item.capability_id for item in registry.discover()),
            ("cap_registry_alpha_0001", "cap_registry_beta_0001", "cap_registry_gamma_0001"),
        )

    def test_registry_rejects_duplicates_and_unknown_lookup(self):
        duplicate = capability("cap_registry_alpha_0001")

        with self.assertRaises(AstraCapabilityDiscoveryError):
            AstraCapabilityRegistry((duplicate, duplicate))

        registry = AstraCapabilityRegistry((duplicate,))
        with self.assertRaises(AstraCapabilityDiscoveryError):
            registry.get("cap_registry_unknown_0001")

    def test_registry_has_no_public_mutation_surface_and_returns_copies(self):
        registry = AstraCapabilityRegistry((capability("cap_registry_alpha_0001"),))

        self.assertFalse(hasattr(registry, "register"))
        returned = registry.get("cap_registry_alpha_0001")
        with self.assertRaises(ValidationError):
            returned.capability_name = "Mutated"
        self.assertEqual(registry.get("cap_registry_alpha_0001").capability_name, "Cap Registry Alpha 0001")

    def test_runtime_registers_exactly_one_capability_discovery_engine(self):
        runtime = ready_runtime()

        self.assertIn(AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY, runtime.registered_component_identifiers)
        registrations = tuple(
            registration
            for registration in runtime.component_registrations
            if registration.component_identifier is AstraRuntimeComponentIdentifier.CAPABILITY_DISCOVERY
        )
        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0].implementation_reference, "ASTRA-IMP-007")

    def test_runtime_owned_discovery_is_deterministic_and_structural(self):
        runtime = ready_runtime()

        result = runtime.capability_discovery.discover(discovered_at=TIMESTAMP)

        self.assertEqual(result.runtime_instance_id, runtime.identity.startup_instance_id)
        self.assertEqual(
            tuple(item.capability_id for item in result.capabilities),
            tuple(sorted(item.capability_id for item in result.capabilities)),
        )
        self.assertTrue(all(item.execution_authority is AstraCapabilityExecutionAuthority.METADATA_ONLY for item in result.capabilities))
        self.assertEqual(result.governance_outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_visibility_and_status_filters_are_metadata_only(self):
        runtime = ready_runtime()

        internal = runtime.discover_capabilities(visibility=AstraCapabilityVisibility.INTERNAL, discovered_at=TIMESTAMP)
        public = runtime.discover_capabilities(visibility=AstraCapabilityVisibility.PUBLIC, discovered_at=TIMESTAMP)

        self.assertGreaterEqual(len(internal.capabilities), 1)
        self.assertEqual(public.capabilities, ())

    def test_discovery_emits_bounded_evidence_without_execution(self):
        runtime = ready_runtime()
        before = runtime.evidence_count()

        result = runtime.discover_capabilities(discovered_at=TIMESTAMP)

        self.assertEqual(runtime.evidence_count(), before + 1)
        self.assertEqual(runtime.retrieve_evidence()[-1].evidence_id, result.evidence_reference)

    def test_unknown_capability_lookup_fails_without_evidence(self):
        runtime = ready_runtime()
        before = runtime.evidence_count()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.get_capability("cap_missing_0001", discovered_at=TIMESTAMP)

        self.assertEqual(runtime.evidence_count(), before)

    def test_runtime_lifecycle_controls_capability_discovery_handles(self):
        runtime = ready_runtime()
        interface = runtime.capability_discovery
        runtime.shutdown()

        with self.assertRaises(AstraRuntimeError):
            interface.discover(discovered_at=TIMESTAMP)
        with self.assertRaises(AstraRuntimeError):
            interface.get("cap_conversation_context_0001", discovered_at=TIMESTAMP)

    def test_conversation_discovery_integration_is_informational_only(self):
        runtime = ready_runtime()
        conversation_engine = AstraConversationContextEngine(runtime=runtime)
        conversation = conversation_engine.create_conversation(
            conversation_id="conv_alpha_0001",
            created_at=TIMESTAMP,
        )
        discovery = runtime.capability_discovery.discover_for_conversation(
            conversation_snapshot=conversation,
            discovered_at=TIMESTAMP,
        )

        self.assertGreaterEqual(len(discovery.capabilities), 1)
        self.assertFalse(hasattr(discovery.capabilities[0], "execute"))
        self.assertFalse(hasattr(discovery.capabilities[0], "plan"))

    def test_conversation_from_another_runtime_is_rejected(self):
        first = ready_runtime("b")
        second = ready_runtime("c")
        conversation_engine = AstraConversationContextEngine(runtime=first)
        conversation = conversation_engine.create_conversation(
            conversation_id="conv_alpha_0001",
            created_at=TIMESTAMP,
        )

        with self.assertRaises(AstraCapabilityDiscoveryError):
            second.capability_discovery.discover_for_conversation(
                conversation_snapshot=conversation,
                discovered_at=TIMESTAMP,
            )

    def test_health_is_structural(self):
        runtime = ready_runtime()

        health = runtime.capability_discovery.health(observed_at=TIMESTAMP)

        self.assertTrue(health.registry_loaded)
        self.assertEqual(health.capability_count, 3)
        self.assertTrue(health.duplicate_free)
        self.assertTrue(health.registry_valid)
        self.assertEqual(health.health_outcome, AstraCapabilityHealthOutcome.HEALTHY)

    def test_engine_requires_runtime_ownership(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "d" * 32)
        engine = AstraCapabilityDiscoveryEngine(runtime=runtime)

        with self.assertRaises(AstraCapabilityDiscoveryError):
            engine.discover_capabilities(discovered_at=TIMESTAMP)

    def test_module_does_not_import_unauthorized_surfaces(self):
        source = inspect.getsource(capability_module).lower()

        for forbidden in (
            "from fastapi",
            "import fastapi",
            "sqlalchemy",
            "openai",
            "anthropic",
            "assistanttoolexecutor",
            "tool_executor",
            "alembic",
            "model invocation",
            "embedding",
            "vector",
            "app.modules.audit",
            "app.main",
            "apirouter",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
