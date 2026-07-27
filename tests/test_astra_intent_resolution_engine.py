from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, GovernanceOutcome
from app.modules.astra_ai.conversation_context import (
    AstraDeclaredIntentBinding,
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.intent_resolution import (
    AstraIntentCategory,
    AstraIntentConfidence,
    AstraIntentHealthOutcome,
    AstraIntentRequest,
    AstraIntentResolutionError,
    AstraIntentStatus,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeComponentIdentifier, AstraRuntimeError


NOW = datetime(2026, 7, 27, 8, 0, tzinfo=timezone.utc)
CAPABILITY = "cap_conversation_context_0001"
_CONVERSATION_ENGINES = {}


def ready(suffix="9", capacity=100):
    runtime = AstraRuntime(
        created_at=NOW,
        startup_instance_id="astra_rt_" + suffix * 32,
        evidence_sink_capacity=capacity,
    )
    runtime.startup()
    return runtime


def allow(runtime):
    original = runtime.evaluate_governance

    def evaluate(contract):
        result = original(contract)
        return result.model_copy(
            update={"decision": result.decision.model_copy(update={"outcome": GovernanceOutcome.ALLOW})}
        )

    runtime.evaluate_governance = evaluate


def context(runtime, conversation_id="conv_intent_0001"):
    engine = AstraConversationContextEngine(runtime=runtime)
    engine.create_conversation(conversation_id=conversation_id, created_at=NOW)
    engine.transition_conversation(
        conversation_id,
        AstraConversationLifecycleState.ACTIVE,
        transitioned_at=NOW,
        summary_reference="conversation:active",
        entry_id="ctx_intent_active_0001",
    )
    turn = AstraCurrentTurnContext(
        turn_id="turn_intent_0001",
        received_at=NOW,
        request_reference="request:intent:0001",
        turn_kind=AstraConversationTurnKind.USER_REQUEST,
        route_reference="route:/intent",
    )
    engine.record_current_turn(
        conversation_id,
        turn,
        history_entry_id="ctx_intent_0001",
        summary_reference="intent:declared",
    )
    snapshot = engine.get_conversation(conversation_id)
    _CONVERSATION_ENGINES[(runtime.identity.startup_instance_id, conversation_id)] = engine
    return engine, snapshot


def request(runtime, snapshot, action="request_plan", subject="capability", target=CAPABILITY):
    engine = _CONVERSATION_ENGINES[
        (runtime.identity.startup_instance_id, snapshot.metadata.conversation_id)
    ]
    binding = engine.issue_declared_intent_binding(
        conversation_snapshot=snapshot,
        declared_action=action,
        declared_subject=subject,
        declared_target=target,
    )
    return AstraIntentRequest(
        intent_request_id="intent_req_resolution_0001",
        runtime_instance_id=runtime.identity.startup_instance_id,
        conversation_id=snapshot.metadata.conversation_id,
        current_turn_reference=snapshot.current_turn.turn_id,
        request_reference=snapshot.current_turn.request_reference,
        declared_action=action,
        declared_subject=subject,
        declared_target=target,
        declared_intent_binding=binding,
        constitutional_requirements=(
            ConstitutionalRequirementReference(
                constitutional_source="ASTRA-002",
                requirement_id="AIR-INT-001",
                requirement_version="1.0.0",
            ),
        ),
        timestamp=NOW,
        version="1.0.0",
    )


def resolve(runtime, engine, snapshot, intent_request):
    return runtime.intent_resolution.resolve(
        intent_request,
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        requester_context=runtime.capability_discovery.internal_request_context(),
    )


def test_runtime_registers_one_lifecycle_bound_engine():
    runtime = ready()
    assert runtime.registered_component_identifiers.count(AstraRuntimeComponentIdentifier.INTENT_RESOLUTION) == 1
    interface = runtime.intent_resolution
    engine, snapshot = context(runtime)
    intent_request = request(runtime, snapshot)
    runtime.shutdown()
    with pytest.raises(AstraRuntimeError):
        interface.resolve(
            intent_request,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            requester_context=object(),
        )


def test_exact_declared_signal_resolves_deterministically_without_authority():
    runtime = ready()
    allow(runtime)
    engine, snapshot = context(runtime)
    intent_request = request(runtime, snapshot)
    first = resolve(runtime, engine, snapshot, intent_request)
    second = resolve(runtime, engine, snapshot, intent_request)
    assert first.intent_id == second.intent_id
    assert first.intent_status is AstraIntentStatus.RESOLVED
    assert first.intent_confidence is AstraIntentConfidence.EXACT_MATCH
    assert first.intent_category is AstraIntentCategory.PLANNING_REQUEST
    assert first.planning_eligible is True
    assert first.execution_authorization_state == "not_authorized"
    with pytest.raises(ValidationError):
        first.intent_status = AstraIntentStatus.INVALID


@pytest.mark.parametrize(
    ("outcome", "status"),
    (
        (GovernanceOutcome.CLARIFY, AstraIntentStatus.CLARIFICATION_REQUIRED),
        (GovernanceOutcome.DEFER, AstraIntentStatus.DEFERRED),
        (GovernanceOutcome.REFUSE, AstraIntentStatus.REFUSED),
        (GovernanceOutcome.CONTAIN, AstraIntentStatus.GOVERNANCE_BLOCKED),
        (GovernanceOutcome.FAIL_CLOSED, AstraIntentStatus.INVALID),
    ),
)
def test_governance_mapping_releases_no_planning_eligibility(outcome, status):
    runtime = ready("8")
    original = runtime.evaluate_governance

    def forced(contract):
        result = original(contract)
        return result.model_copy(update={"decision": result.decision.model_copy(update={"outcome": outcome})})

    runtime.evaluate_governance = forced
    engine, snapshot = context(runtime)
    result = resolve(runtime, engine, snapshot, request(runtime, snapshot))
    assert result.intent_status is status
    assert result.planning_eligible is False
    assert result.resolved_capability_ids == ()


def test_ambiguous_and_unsupported_signals_never_guess():
    runtime = ready()
    allow(runtime)
    engine, snapshot = context(runtime)
    ambiguous = resolve(runtime, engine, snapshot, request(runtime, snapshot, subject=None))
    unsupported = resolve(runtime, engine, snapshot, request(runtime, snapshot, action="invent_action"))
    assert ambiguous.intent_status is AstraIntentStatus.CLARIFICATION_REQUIRED
    assert ambiguous.intent_confidence is AstraIntentConfidence.AMBIGUOUS
    assert unsupported.intent_status is AstraIntentStatus.UNSUPPORTED
    assert unsupported.planning_eligible is False


def test_current_turn_stale_foreign_and_closed_conversations_are_rejected():
    runtime = ready()
    allow(runtime)
    engine, snapshot = context(runtime)
    with pytest.raises(AstraIntentResolutionError):
        resolve(runtime, engine, snapshot, request(runtime, snapshot).model_copy(update={"current_turn_reference": "turn_wrong_0001"}))

    stale = snapshot
    stale_request = request(runtime, stale)
    engine.record_current_turn(
        snapshot.metadata.conversation_id,
        AstraCurrentTurnContext(
            turn_id="turn_intent_0002",
            received_at=NOW,
            request_reference="request:intent:0002",
            turn_kind=AstraConversationTurnKind.USER_REQUEST,
        ),
        history_entry_id="ctx_intent_0002",
        summary_reference="intent:new",
    )
    with pytest.raises(AstraIntentResolutionError):
        resolve(runtime, engine, stale, stale_request)

    foreign = ready("7")
    allow(foreign)
    with pytest.raises(AstraIntentResolutionError):
            foreign.intent_resolution.resolve(
                stale_request,
            conversation_engine=engine,
            conversation_snapshot=stale,
            requester_context=foreign.capability_discovery.internal_request_context(),
        )


def test_forged_foreign_and_mismatched_declared_intent_bindings_are_rejected():
    runtime = ready()
    allow(runtime)
    engine, snapshot = context(runtime)
    intent_request = request(runtime, snapshot)
    valid_request = request(runtime, snapshot)
    valid_binding = valid_request.declared_intent_binding

    forged = AstraDeclaredIntentBinding(
        **valid_binding.model_dump(),
        authority_token=object(),
    )
    with pytest.raises(AstraIntentResolutionError):
        resolve(
            runtime,
            engine,
            snapshot,
            valid_request.model_copy(update={"declared_intent_binding": forged}),
        )

    foreign = ready("6")
    foreign_engine, foreign_snapshot = context(foreign, "conv_foreign_binding_0001")
    foreign_binding = foreign_engine.issue_declared_intent_binding(
        conversation_snapshot=foreign_snapshot,
        declared_action="request_plan",
        declared_subject="capability",
        declared_target=CAPABILITY,
    )
    with pytest.raises(AstraIntentResolutionError):
        resolve(
            runtime,
            engine,
            snapshot,
            valid_request.model_copy(update={"declared_intent_binding": foreign_binding}),
        )

    with pytest.raises(AstraIntentResolutionError):
        resolve(
            runtime,
            engine,
            snapshot,
            valid_request.model_copy(update={"declared_action": "lookup_capability"}),
        )


def test_closed_conversation_is_rejected():
    runtime = ready()
    allow(runtime)
    engine, snapshot = context(runtime)
    intent_request = request(runtime, snapshot)
    engine.transition_conversation(
        snapshot.metadata.conversation_id,
        AstraConversationLifecycleState.IDLE,
        transitioned_at=NOW,
        summary_reference="conversation:idle",
        entry_id="ctx_intent_idle_0001",
    )
    engine.transition_conversation(
        snapshot.metadata.conversation_id,
        AstraConversationLifecycleState.CLOSING,
        transitioned_at=NOW,
        summary_reference="conversation:closing",
        entry_id="ctx_intent_closing_0001",
    )
    engine.transition_conversation(
        snapshot.metadata.conversation_id,
        AstraConversationLifecycleState.CLOSED,
        transitioned_at=NOW,
        summary_reference="conversation:closed",
        entry_id="ctx_intent_closed_0001",
    )
    closed = engine.get_conversation(snapshot.metadata.conversation_id)
    with pytest.raises(AstraIntentResolutionError):
        resolve(runtime, engine, closed, intent_request)


def test_evidence_before_release_and_failure_atomicity():
    runtime = ready(capacity=4)
    allow(runtime)
    engine, snapshot = context(runtime)  # two conversation evidence records
    before = runtime.evidence_count()
    with pytest.raises(Exception):
        resolve(runtime, engine, snapshot, request(runtime, snapshot))
    assert runtime._intent_resolution._sequence == 0
    assert runtime._intent_resolution._conversation_engine is None
    assert runtime.evidence_count() >= before


def test_health_is_truthful_and_payload_free():
    runtime = ready()
    health = runtime.intent_resolution.health(observed_at=NOW)
    assert health.health_outcome is AstraIntentHealthOutcome.DEGRADED
    assert health.conversation_dependency_available is False
    allow(runtime)
    engine, snapshot = context(runtime)
    resolve(runtime, engine, snapshot, request(runtime, snapshot))
    health = runtime.intent_resolution.health(observed_at=NOW)
    assert health.health_outcome is AstraIntentHealthOutcome.HEALTHY
    assert "conversation_id" not in health.model_dump()


def test_contract_rejects_prompt_provider_and_executable_fields():
    runtime = ready()
    engine, snapshot = context(runtime)
    payload = request(runtime, snapshot).model_dump()
    for key in ("prompt", "provider_payload", "handler", "callable", "command"):
        with pytest.raises(ValidationError):
            AstraIntentRequest(**payload, **{key: "forbidden"})
