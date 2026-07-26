from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from app.modules.astra_ai import conversation_context as conversation_module
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationContextError,
    AstraConversationHealthOutcome,
    AstraConversationHistoryKind,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.runtime import AstraRuntime


TIMESTAMP = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)


def ready_runtime(instance_suffix: str = "a", *, evidence_sink_capacity: int = 50) -> AstraRuntime:
    runtime = AstraRuntime(
        created_at=TIMESTAMP,
        startup_instance_id="astra_rt_" + instance_suffix * 32,
        evidence_sink_capacity=evidence_sink_capacity,
    )
    runtime.startup()
    return runtime


def current_turn(turn_id: str = "turn_request_0001") -> AstraCurrentTurnContext:
    return AstraCurrentTurnContext(
        turn_id=turn_id,
        received_at=TIMESTAMP,
        request_reference=f"request:{turn_id}",
        turn_kind=AstraConversationTurnKind.USER_REQUEST,
        route_reference="route:/quiz",
        context_references=("context:current-route",),
    )


class AstraConversationContextEngineTests(unittest.TestCase):
    def test_conversation_creation_is_deterministic_and_runtime_owned(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)

        conversation = engine.create_conversation(
            conversation_id="conv_alpha_0001",
            created_at=TIMESTAMP,
        )

        self.assertEqual(conversation.metadata.conversation_id, "conv_alpha_0001")
        self.assertEqual(conversation.metadata.runtime_instance_id, runtime.identity.startup_instance_id)
        self.assertEqual(conversation.metadata.lifecycle_state, AstraConversationLifecycleState.CREATED)
        self.assertEqual(conversation.metadata.implementation_reference, "ASTRA-IMP-006")
        self.assertEqual(conversation.metadata.conversation_version, "1.0.0")

    def test_conversation_cannot_exist_without_runtime_ownership_token(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        conversation = engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)

        self.assertFalse(hasattr(conversation, "transition"))
        self.assertFalse(hasattr(conversation, "record_current_turn"))

    def test_engine_requires_ready_runtime_owner(self):
        runtime = AstraRuntime(created_at=TIMESTAMP, startup_instance_id="astra_rt_" + "b" * 32)

        with self.assertRaises(AstraConversationContextError):
            AstraConversationContextEngine(runtime=runtime)

    def test_valid_lifecycle_transitions(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)

        active = engine.transition_conversation(
            "conv_alpha_0001",
            AstraConversationLifecycleState.ACTIVE,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:active",
            entry_id="ctx_transition_0001",
        )
        idle = engine.transition_conversation(
            "conv_alpha_0001",
            AstraConversationLifecycleState.IDLE,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:idle",
            entry_id="ctx_transition_0002",
        )
        closing = engine.transition_conversation(
            "conv_alpha_0001",
            AstraConversationLifecycleState.CLOSING,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:closing",
            entry_id="ctx_transition_0003",
        )
        closed = engine.transition_conversation(
            "conv_alpha_0001",
            AstraConversationLifecycleState.CLOSED,
            transitioned_at=TIMESTAMP,
            summary_reference="conversation:closed",
            entry_id="ctx_transition_0004",
        )

        self.assertEqual(active.lifecycle_state, AstraConversationLifecycleState.ACTIVE)
        self.assertEqual(idle.lifecycle_state, AstraConversationLifecycleState.IDLE)
        self.assertEqual(closing.lifecycle_state, AstraConversationLifecycleState.CLOSING)
        self.assertEqual(closed.lifecycle_state, AstraConversationLifecycleState.CLOSED)

    def test_invalid_lifecycle_transition_is_rejected(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)

        with self.assertRaises((AstraConversationContextError, ValidationError)):
            engine.transition_conversation(
                "conv_alpha_0001",
                AstraConversationLifecycleState.CLOSED,
                transitioned_at=TIMESTAMP,
                summary_reference="conversation:invalid",
                entry_id="ctx_transition_0001",
            )

    def test_current_turn_context_is_bounded_metadata_only(self):
        turn = current_turn()

        self.assertEqual(turn.request_reference, "request:turn_request_0001")
        self.assertEqual(turn.context_references, ("context:current-route",))
        self.assertNotIn("message", turn.model_dump())

        with self.assertRaises(Exception):
            AstraCurrentTurnContext(
                turn_id="turn_secret_0001",
                received_at=TIMESTAMP,
                request_reference="request:api_key:secret",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
            )

    def test_short_context_history_is_bounded_and_evicts_oldest(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime, short_context_limit=2)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)

        for index in range(1, 5):
            engine.record_current_turn(
                "conv_alpha_0001",
                current_turn(f"turn_request_000{index}"),
                history_entry_id=f"ctx_history_000{index}",
                summary_reference=f"turn:summary:{index}",
            )

        history = engine.get_conversation("conv_alpha_0001").short_context

        self.assertEqual(len(history), 2)
        self.assertEqual(tuple(entry.entry_id for entry in history), ("ctx_history_0003", "ctx_history_0004"))
        self.assertTrue(all(entry.history_kind is AstraConversationHistoryKind.TURN_RECORDED for entry in history))

    def test_short_context_retrieval_is_copy_safe(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        engine.record_current_turn(
            "conv_alpha_0001",
            current_turn(),
            history_entry_id="ctx_history_0001",
            summary_reference="turn:summary:1",
        )

        retrieved = engine.get_conversation("conv_alpha_0001").short_context

        with self.assertRaises(ValidationError):
            retrieved[0].summary_reference = "mutated"

        self.assertEqual(
            engine.get_conversation("conv_alpha_0001").short_context[0].summary_reference,
            "turn:summary:1",
        )

    def test_snapshot_obtained_before_shutdown_cannot_mutate_conversation(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        snapshot = engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        runtime.shutdown()

        self.assertFalse(hasattr(snapshot, "transition"))
        self.assertFalse(hasattr(snapshot, "record_current_turn"))
        with self.assertRaises(ValidationError):
            snapshot.metadata.lifecycle_state = AstraConversationLifecycleState.ACTIVE
        with self.assertRaises(AstraConversationContextError):
            engine.transition_conversation(
                "conv_alpha_0001",
                AstraConversationLifecycleState.ACTIVE,
                transitioned_at=TIMESTAMP,
                summary_reference="conversation:active",
                entry_id="ctx_transition_0001",
            )

    def test_conversation_isolation_by_runtime_engine(self):
        first_runtime = ready_runtime("c")
        second_runtime = ready_runtime("d")
        first = AstraConversationContextEngine(runtime=first_runtime)
        second = AstraConversationContextEngine(runtime=second_runtime)
        first.create_conversation(conversation_id="conv_shared_0001", created_at=TIMESTAMP)
        second.create_conversation(conversation_id="conv_shared_0001", created_at=TIMESTAMP)

        self.assertNotEqual(
            first.get_conversation("conv_shared_0001").metadata.runtime_instance_id,
            second.get_conversation("conv_shared_0001").metadata.runtime_instance_id,
        )

    def test_unknown_conversation_is_not_owned_by_runtime_engine(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)

        with self.assertRaises((AstraConversationContextError, ValidationError)):
            engine.get_conversation("conv_unknown_0001")

    def test_evidence_is_emitted_through_runtime_core(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        starting_count = runtime.evidence_count()

        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        engine.record_current_turn(
            "conv_alpha_0001",
            current_turn(),
            history_entry_id="ctx_history_0001",
            summary_reference="turn:summary:1",
        )

        self.assertEqual(runtime.evidence_count(), starting_count + 2)
        self.assertTrue(all(evidence.evidence_type == "governance_decision" for evidence in runtime.retrieve_evidence()))

    def test_evidence_capacity_failure_does_not_create_conversation(self):
        runtime = ready_runtime(evidence_sink_capacity=1)
        filler = AstraConversationContextEngine(runtime=runtime)
        filler.create_conversation(conversation_id="conv_filler_0001", created_at=TIMESTAMP)
        engine = AstraConversationContextEngine(runtime=runtime)

        with self.assertRaises(Exception):
            engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)

        self.assertEqual(engine.health(observed_at=TIMESTAMP).conversation_count, 0)
        self.assertEqual(engine._operation_sequence, 0)

    def test_evidence_failure_does_not_change_lifecycle_current_turn_or_history(self):
        runtime = ready_runtime(evidence_sink_capacity=1)
        engine = AstraConversationContextEngine(runtime=runtime)
        created = engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        before_count = runtime.evidence_count()

        with self.assertRaises(Exception):
            engine.transition_conversation(
                "conv_alpha_0001",
                AstraConversationLifecycleState.ACTIVE,
                transitioned_at=TIMESTAMP,
                summary_reference="conversation:active",
                entry_id="ctx_transition_0001",
            )

        after_transition = engine.get_conversation("conv_alpha_0001")
        self.assertEqual(after_transition.metadata, created.metadata)
        self.assertIsNone(after_transition.current_turn)
        self.assertEqual(after_transition.short_context, ())
        self.assertEqual(runtime.evidence_count(), before_count)
        self.assertEqual(engine._operation_sequence, 1)

        with self.assertRaises(Exception):
            engine.record_current_turn(
                "conv_alpha_0001",
                current_turn(),
                history_entry_id="ctx_history_0001",
                summary_reference="turn:summary:1",
            )

        after_turn = engine.get_conversation("conv_alpha_0001")
        self.assertEqual(after_turn.metadata, created.metadata)
        self.assertIsNone(after_turn.current_turn)
        self.assertEqual(after_turn.short_context, ())
        self.assertEqual(runtime.evidence_count(), before_count)
        self.assertEqual(engine._operation_sequence, 1)

    def test_successful_operations_commit_exactly_one_evidence_record_together(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)

        before = runtime.evidence_count()
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        after_create = runtime.evidence_count()
        engine.record_current_turn(
            "conv_alpha_0001",
            current_turn(),
            history_entry_id="ctx_history_0001",
            summary_reference="turn:summary:1",
        )
        after_turn = runtime.evidence_count()

        self.assertEqual(after_create, before + 1)
        self.assertEqual(after_turn, after_create + 1)
        self.assertEqual(engine._operation_sequence, 2)

    def test_backdated_transitions_and_turns_fail(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        later = TIMESTAMP + timedelta(minutes=5)
        earlier = TIMESTAMP + timedelta(minutes=1)
        engine.record_current_turn(
            "conv_alpha_0001",
            current_turn("turn_request_0001").model_copy(update={"received_at": later}),
            history_entry_id="ctx_history_0001",
            summary_reference="turn:summary:1",
        )

        with self.assertRaises(AstraConversationContextError):
            engine.transition_conversation(
                "conv_alpha_0001",
                AstraConversationLifecycleState.IDLE,
                transitioned_at=earlier,
                summary_reference="conversation:idle",
                entry_id="ctx_transition_0001",
            )
        with self.assertRaises(AstraConversationContextError):
            engine.record_current_turn(
                "conv_alpha_0001",
                current_turn("turn_request_0002").model_copy(update={"received_at": earlier}),
                history_entry_id="ctx_history_0002",
                summary_reference="turn:summary:2",
            )

    def test_governance_integration_fails_if_runtime_stops(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        runtime.shutdown()

        with self.assertRaises(AstraConversationContextError):
            engine.record_current_turn(
                "conv_alpha_0001",
                current_turn(),
                history_entry_id="ctx_history_0001",
                summary_reference="turn:summary:1",
            )

    def test_health_integrates_runtime_status_without_runtime_authority_change(self):
        runtime = ready_runtime()
        engine = AstraConversationContextEngine(runtime=runtime)
        engine.create_conversation(conversation_id="conv_alpha_0001", created_at=TIMESTAMP)
        engine.record_current_turn(
            "conv_alpha_0001",
            current_turn(),
            history_entry_id="ctx_history_0001",
            summary_reference="turn:summary:1",
        )

        health = engine.health(observed_at=TIMESTAMP)

        self.assertEqual(health.runtime_state, runtime.state)
        self.assertEqual(health.runtime_health_outcome.value, "healthy")
        self.assertEqual(health.health_outcome, AstraConversationHealthOutcome.HEALTHY)
        self.assertEqual(health.conversation_count, 1)
        self.assertEqual(health.active_count, 1)

    def test_context_models_reject_naive_timestamps(self):
        with self.assertRaises((AstraConversationContextError, ValidationError)):
            AstraCurrentTurnContext(
                turn_id="turn_request_0001",
                received_at=datetime(2026, 7, 26, 12, 0),
                request_reference="request:turn",
                turn_kind=AstraConversationTurnKind.USER_REQUEST,
            )

    def test_module_does_not_import_unauthorized_surfaces(self):
        source = inspect.getsource(conversation_module).lower()

        for forbidden in (
            "from fastapi",
            "import fastapi",
            "sqlalchemy",
            "openai",
            "anthropic",
            "tool_executor",
            "alembic",
            "model invocation",
            "prompt",
            "embedding",
            "vector",
            "app.modules.audit",
            "app.main",
            "apirouter",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
