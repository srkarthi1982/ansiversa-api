from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.modules.astra_ai import capability_discovery as capability_module
from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryEngine,
    AstraCapabilityDiscoveryError,
    AstraCapabilityDiscoveryRequestContext,
    AstraCapabilityExecutionAuthority,
    AstraCapabilityHealthOutcome,
    AstraCapabilityMetadata,
    AstraCapabilityRegistry,
    AstraCapabilityRequesterClass,
    AstraCapabilityStatus,
    AstraCapabilityType,
    AstraCapabilityVisibility,
    authenticated_discovery_context,
    public_discovery_context,
)
from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, GovernanceOutcome
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationMetadata,
    AstraConversationSnapshot,
)
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


def force_governance_outcome(runtime: AstraRuntime, outcome: GovernanceOutcome) -> None:
    original = runtime.evaluate_governance

    def evaluate(input_contract):
        result = original(input_contract)
        return result.model_copy(
            update={
                "decision": result.decision.model_copy(update={"outcome": outcome}),
            }
        )

    runtime.evaluate_governance = evaluate


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
            tuple(
                item.capability_id
                for item in registry.discover(
                    allowed_visibilities=(
                        AstraCapabilityVisibility.PUBLIC,
                        AstraCapabilityVisibility.AUTHENTICATED,
                        AstraCapabilityVisibility.INTERNAL,
                    ),
                )
            ),
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

        result = runtime.capability_discovery.discover(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(result.runtime_instance_id, runtime.identity.startup_instance_id)
        self.assertEqual(result.capabilities, ())
        self.assertEqual(result.governance_outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_allow_discovery_is_deterministic_and_structural(self):
        runtime = ready_runtime()
        force_governance_outcome(runtime, GovernanceOutcome.ALLOW)

        result = runtime.capability_discovery.discover(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(
            tuple(item.capability_id for item in result.capabilities),
            tuple(sorted(item.capability_id for item in result.capabilities)),
        )
        self.assertTrue(all(item.execution_authority is AstraCapabilityExecutionAuthority.METADATA_ONLY for item in result.capabilities))

    def test_fail_closed_discovery_returns_no_capabilities_but_records_evidence(self):
        runtime = ready_runtime()
        before = runtime.evidence_count()

        result = runtime.discover_capabilities(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(result.governance_outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.capabilities, ())
        self.assertEqual(runtime.evidence_count(), before + 1)

    def test_non_allow_outcomes_cannot_expose_metadata(self):
        outcomes = (
            (GovernanceOutcome.REFUSE, "1"),
            (GovernanceOutcome.CONTAIN, "2"),
            (GovernanceOutcome.DEFER, "3"),
            (GovernanceOutcome.CLARIFY, "4"),
        )
        for outcome, suffix in outcomes:
            runtime = ready_runtime(suffix)
            force_governance_outcome(runtime, outcome)

            result = runtime.discover_capabilities(
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

            self.assertEqual(result.governance_outcome, outcome)
            self.assertEqual(result.capabilities, ())

    def test_visibility_and_status_filters_are_governed_by_request_context(self):
        runtime = ready_runtime()
        force_governance_outcome(runtime, GovernanceOutcome.ALLOW)
        runtime._capability_discovery = AstraCapabilityDiscoveryEngine(
            runtime=runtime,
            capabilities=(
                capability("cap_public_alpha_0001", visibility=AstraCapabilityVisibility.PUBLIC),
                capability("cap_authenticated_alpha_0001", visibility=AstraCapabilityVisibility.AUTHENTICATED),
                capability("cap_internal_alpha_0001", visibility=AstraCapabilityVisibility.INTERNAL),
            ),
        )

        public = runtime.discover_capabilities(
            request_context=public_discovery_context(),
            discovered_at=TIMESTAMP,
        )
        internal = runtime.discover_capabilities(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(tuple(item.visibility for item in public.capabilities), (AstraCapabilityVisibility.PUBLIC,))
        self.assertEqual(len(internal.capabilities), 3)

    def test_public_and_authenticated_contexts_cannot_self_select_internal_visibility(self):
        runtime = ready_runtime()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.discover_capabilities(
                request_context=public_discovery_context(),
                requested_visibility=AstraCapabilityVisibility.AUTHENTICATED,
                discovered_at=TIMESTAMP,
            )
        with self.assertRaises(AstraCapabilityDiscoveryError):
            authenticated_discovery_context()

    def test_caller_cannot_self_assert_authenticated_state(self):
        with self.assertRaises(ValidationError):
            AstraCapabilityDiscoveryRequestContext(
                requester_class=AstraCapabilityRequesterClass.AUTHENTICATED,
                authenticated=True,
                maximum_visibility=AstraCapabilityVisibility.AUTHENTICATED,
                governance_reference=requirement(),
            )

    def test_internal_visibility_requires_trusted_runtime_ownership(self):
        runtime = ready_runtime()

        forged = AstraCapabilityDiscoveryRequestContext(
            requester_class=AstraCapabilityRequesterClass.INTERNAL_RUNTIME,
            authenticated=True,
            runtime_instance_id=runtime.identity.startup_instance_id,
            maximum_visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=requirement(),
            authority_token=object(),
        )
        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.discover_capabilities(
                request_context=forged,
                discovered_at=TIMESTAMP,
            )
        with self.assertRaises(ValidationError):
            AstraCapabilityDiscoveryRequestContext(
                requester_class=AstraCapabilityRequesterClass.INTERNAL_RUNTIME,
                authenticated=False,
                runtime_instance_id=runtime.identity.startup_instance_id,
                maximum_visibility=AstraCapabilityVisibility.INTERNAL,
                governance_reference=requirement(),
            )

    def test_foreign_runtime_minted_internal_context_is_rejected(self):
        first = ready_runtime("b")
        second = ready_runtime("c")
        foreign_context = first.capability_discovery.internal_request_context()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            second.discover_capabilities(
                request_context=foreign_context,
                discovered_at=TIMESTAMP,
            )

    def test_owner_issued_internal_context_remains_governance_gated(self):
        runtime = ready_runtime()
        context = runtime.capability_discovery.internal_request_context()

        result = runtime.discover_capabilities(
            request_context=context,
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(result.governance_outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.capabilities, ())

    def test_caller_input_cannot_broaden_visibility(self):
        with self.assertRaises(ValidationError):
            AstraCapabilityDiscoveryRequestContext(
                requester_class=AstraCapabilityRequesterClass.PUBLIC,
                authenticated=False,
                maximum_visibility=AstraCapabilityVisibility.INTERNAL,
                governance_reference=requirement(),
            )

    def test_discovery_emits_bounded_evidence_without_execution(self):
        runtime = ready_runtime()
        before = runtime.evidence_count()

        result = runtime.discover_capabilities(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )

        self.assertEqual(runtime.evidence_count(), before + 1)
        self.assertEqual(runtime.retrieve_evidence()[-1].evidence_id, result.evidence_reference)

    def test_capability_lookup_cannot_return_metadata_on_non_allow_outcome(self):
        runtime = ready_runtime()
        before = runtime.evidence_count()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.get_capability(
                "cap_conversation_context_0001",
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

        self.assertEqual(runtime.evidence_count(), before + 1)

    def test_allowed_unknown_capability_lookup_fails_after_governed_evidence(self):
        runtime = ready_runtime()
        force_governance_outcome(runtime, GovernanceOutcome.ALLOW)
        before = runtime.evidence_count()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.get_capability(
                "cap_missing_0001",
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

        self.assertEqual(runtime.evidence_count(), before + 1)

    def test_no_result_is_released_before_successful_evidence_append_and_sequence_commit(self):
        runtime = ready_runtime(evidence_sink_capacity=1)
        first = runtime.discover_capabilities(
            request_context=runtime.capability_discovery.internal_request_context(),
            discovered_at=TIMESTAMP,
        )
        self.assertEqual(first.capabilities, ())
        self.assertEqual(runtime._capability_discovery._operation_sequence, 1)

        with self.assertRaises(Exception):
            runtime.discover_capabilities(
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

        self.assertEqual(runtime.evidence_count(), 1)
        self.assertEqual(runtime._capability_discovery._operation_sequence, 1)

    def test_runtime_lifecycle_controls_capability_discovery_handles(self):
        runtime = ready_runtime()
        interface = runtime.capability_discovery
        context = interface.internal_request_context()
        runtime.shutdown()

        with self.assertRaises(AstraRuntimeError):
            interface.discover(
                request_context=context,
                discovered_at=TIMESTAMP,
            )
        with self.assertRaises(AstraRuntimeError):
            interface.get(
                "cap_conversation_context_0001",
                request_context=context,
                discovered_at=TIMESTAMP,
            )

    def test_conversation_discovery_integration_is_informational_only(self):
        runtime = ready_runtime()
        force_governance_outcome(runtime, GovernanceOutcome.ALLOW)
        conversation_engine = AstraConversationContextEngine(runtime=runtime)
        conversation = conversation_engine.create_conversation(
            conversation_id="conv_alpha_0001",
            created_at=TIMESTAMP,
        )
        discovery = runtime.capability_discovery.discover_for_conversation(
            conversation_engine=conversation_engine,
            conversation_snapshot=conversation,
            request_context=runtime.capability_discovery.internal_request_context(),
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
                conversation_engine=conversation_engine,
                conversation_snapshot=conversation,
                request_context=second.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

    def test_fabricated_conversation_snapshot_is_rejected(self):
        runtime = ready_runtime()

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.capability_discovery.discover_for_conversation(
                conversation_engine=object(),
                conversation_snapshot=object(),
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

    def test_same_runtime_unregistered_conversation_snapshot_is_rejected(self):
        runtime = ready_runtime()
        conversation_engine = AstraConversationContextEngine(runtime=runtime)
        forged = AstraConversationSnapshot(
            metadata=AstraConversationMetadata(
                conversation_id="conv_forged_0001",
                runtime_instance_id=runtime.identity.startup_instance_id,
                created_at=TIMESTAMP,
                last_activity_at=TIMESTAMP,
                conversation_version="1.0.0",
                implementation_reference="ASTRA-IMP-006",
                lifecycle_state=AstraConversationLifecycleState.ACTIVE,
            )
        )

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.capability_discovery.discover_for_conversation(
                conversation_engine=conversation_engine,
                conversation_snapshot=forged,
                request_context=runtime.capability_discovery.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

    def test_closed_conversation_snapshot_is_rejected(self):
        runtime = ready_runtime()
        conversation_engine = AstraConversationContextEngine(runtime=runtime)
        conversation = conversation_engine.create_conversation(
            conversation_id="conv_alpha_0001",
            created_at=TIMESTAMP,
        )
        conversation_engine.transition_conversation(
            conversation.metadata.conversation_id,
            AstraConversationLifecycleState.CLOSING,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:closing",
            entry_id="ctx_transition_0001",
        )
        closed = conversation_engine.transition_conversation(
            conversation.metadata.conversation_id,
            AstraConversationLifecycleState.CLOSED,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:closed",
            entry_id="ctx_transition_0002",
        )
        closed_snapshot = conversation_engine.get_conversation(closed.conversation_id)

        with self.assertRaises(AstraCapabilityDiscoveryError):
            runtime.capability_discovery.discover_for_conversation(
                conversation_engine=conversation_engine,
                conversation_snapshot=closed_snapshot,
                request_context=runtime.capability_discovery.internal_request_context(),
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
            engine.discover_capabilities(
                request_context=engine.internal_request_context(),
                discovered_at=TIMESTAMP,
            )

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
