from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.modules.astra_ai.activation import (
    SUBSCRIPTION_MANAGER_APP_ID,
    SUBSCRIPTION_MANAGER_PRIVATE_READ_SCOPE,
    load_runtime_activation,
)
from app.modules.astra_ai.capability_discovery import AstraCapabilityDiscoveryError
from app.modules.astra_ai.configuration import _validate_astra_configuration_candidate, get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, GovernanceOutcome
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.intent_resolution import AstraIntentRequest, AstraIntentResolutionError, AstraIntentStatus
from app.modules.astra_ai.metadata_activation_binding import (
    METADATA_CONTEXT_TTL_SECONDS,
    AstraGovernedMetadataContext,
    AstraGovernedMetadataContextIssuer,
    AstraMetadataActivationBindingError,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError


NOW = datetime(2026, 8, 2, 16, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "6" * 32


def runtime(suffix: str = "6") -> AstraRuntime:
    loaded = _stage_zero_test_configuration()

    def enabled_activation_loader(**values):
        return load_runtime_activation(
            **values,
            app_settings=Settings(APP_ENV="development", ASTRA_NONPROD_READ_ENABLED="true"),
        )

    with (
        patch("app.modules.astra_ai.runtime.get_astra_configuration", return_value=loaded),
        patch("app.modules.astra_ai.governance.get_astra_configuration", return_value=loaded),
        patch("app.modules.astra_ai.runtime.load_runtime_activation", side_effect=enabled_activation_loader),
    ):
        instance = AstraRuntime(created_at=NOW, startup_instance_id="astra_rt_" + suffix * 32)
        instance.startup()
    return instance


def runtime_without_activation() -> AstraRuntime:
    loaded = _stage_zero_test_configuration()
    with (
        patch("app.modules.astra_ai.runtime.get_astra_configuration", return_value=loaded),
        patch("app.modules.astra_ai.governance.get_astra_configuration", return_value=loaded),
        patch("app.modules.astra_ai.runtime.load_runtime_activation", return_value=None),
    ):
        instance = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        instance.startup()
    return instance


def _stage_zero_test_configuration():
    candidate = get_astra_configuration().configuration.model_dump(mode="json")
    return _validate_astra_configuration_candidate(candidate, loaded_at=NOW)


def conversation(instance: AstraRuntime, suffix: str = "0001"):
    engine = AstraConversationContextEngine(runtime=instance)
    conversation_id = f"conv_meta_bind_{suffix}"
    engine.create_conversation(conversation_id=conversation_id, created_at=NOW)
    engine.transition_conversation(
        conversation_id,
        AstraConversationLifecycleState.ACTIVE,
        transitioned_at=NOW,
        summary_reference="conversation:active",
        entry_id=f"ctx_meta_bind_active_{suffix}",
    )
    engine.record_current_turn(
        conversation_id,
        AstraCurrentTurnContext(
            turn_id=f"turn_meta_bind_{suffix}",
            received_at=NOW,
            request_reference=f"request:meta-bind:{suffix}",
            turn_kind=AstraConversationTurnKind.USER_REQUEST,
            route_reference="route:/astra/metadata-context",
        ),
        history_entry_id=f"ctx_meta_bind_turn_{suffix}",
        summary_reference="metadata-context:declared",
    )
    return engine, engine.get_conversation(conversation_id)


def record_turn(
    engine: AstraConversationContextEngine,
    conversation_id: str,
    *,
    suffix: str,
    received_at: datetime,
    turn_id: str | None = None,
    request_reference: str | None = None,
):
    engine.record_current_turn(
        conversation_id,
        AstraCurrentTurnContext(
            turn_id=turn_id or f"turn_meta_bind_{suffix}",
            received_at=received_at,
            request_reference=request_reference or f"request:meta-bind:{suffix}",
            turn_kind=AstraConversationTurnKind.USER_REQUEST,
            route_reference="route:/astra/metadata-context",
        ),
        history_entry_id=f"ctx_meta_bind_turn_{suffix}",
        summary_reference="metadata-context:declared",
    )
    return engine.get_conversation(conversation_id)


def issue_context(
    instance: AstraRuntime,
    engine: AstraConversationContextEngine,
    snapshot,
    capability_id: str = "subscription.count_active",
) -> AstraGovernedMetadataContext:
    return instance.issue_subscription_manager_governed_metadata_context(
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        adapter_capability_id=capability_id,
        requested_at=NOW,
    )


def request_context(instance: AstraRuntime, context: AstraGovernedMetadataContext | None = None):
    base = instance.capability_discovery.internal_request_context()
    if context is None:
        return base
    return base.model_copy(update={"governed_metadata_context": context})


def raw_replay_request_context(instance: AstraRuntime, context: AstraGovernedMetadataContext):
    return instance.capability_discovery.internal_request_context().model_copy(
        update={
            "governed_metadata_context": context,
            "conversation_id": context.conversation_id,
            "current_turn_reference": context.current_turn_reference,
            "request_reference": context.request_reference,
        }
    )


def intent_request(instance: AstraRuntime, engine: AstraConversationContextEngine, snapshot, context, target=None):
    current_turn = snapshot.current_turn
    target = target or context.capability_id
    binding = engine.issue_declared_intent_binding(
        conversation_snapshot=snapshot,
        declared_action="get_information",
        declared_subject="subscription",
        declared_target=target,
    )
    return AstraIntentRequest(
        intent_request_id="intent_req_meta_bind_0001",
        runtime_instance_id=instance.identity.startup_instance_id,
        conversation_id=snapshot.metadata.conversation_id,
        current_turn_reference=current_turn.turn_id,
        request_reference=current_turn.request_reference,
        declared_action="get_information",
        declared_subject="subscription",
        declared_target=target,
        governed_metadata_context=context,
        declared_intent_binding=binding,
        constitutional_requirements=(
            ConstitutionalRequirementReference(
                constitutional_source="ASTRA-010",
                requirement_id="AIR-CM-009",
                requirement_version="1.0.0",
            ),
        ),
        timestamp=NOW,
        version="1.0.0",
    )


def assert_context_rejected(instance: AstraRuntime, engine, snapshot, context) -> None:
    with pytest.raises((AstraCapabilityDiscoveryError, AstraIntentResolutionError, AstraRuntimeError)):
        instance.capability_discovery.discover_for_conversation(
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            request_context=request_context(instance, context),
            discovered_at=NOW,
        )


def test_positive_governed_metadata_context_uses_real_activation_without_execution():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context = issue_context(instance, engine, snapshot)

    discovery = instance.capability_discovery.discover_for_conversation(
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        request_context=request_context(instance, context),
        discovered_at=NOW,
    )
    intent = instance.intent_resolution.resolve(
        intent_request(instance, engine, snapshot, context),
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        requester_context=request_context(instance, context),
    )

    assert discovery.governance_outcome is GovernanceOutcome.ALLOW
    assert all(item.execution_authority.value == "metadata_only" for item in discovery.capabilities)
    assert intent.intent_status is AstraIntentStatus.RESOLVED
    assert intent.resolved_capability_ids == ("subscription.count_active",)


def test_generic_internal_metadata_request_does_not_gain_subscription_activation():
    instance = runtime()
    engine, snapshot = conversation(instance)

    discovery = instance.capability_discovery.discover_for_conversation(
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        request_context=request_context(instance),
        discovered_at=NOW,
    )

    assert discovery.governance_outcome is GovernanceOutcome.FAIL_CLOSED
    assert discovery.capabilities == ()


def test_caller_created_copied_and_tampered_contexts_fail_closed():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context = issue_context(instance, engine, snapshot)
    caller_created = AstraGovernedMetadataContext(**context.model_dump())
    copied = context.model_copy()
    tampered = context.model_copy(update={"capability_id": "subscription.count_all"})

    for invalid in (caller_created, copied, tampered):
        assert not instance.validates_governed_metadata_context(
            invalid,
            observed_at=NOW,
            conversation_id=context.conversation_id,
            current_turn_reference=context.current_turn_reference,
            request_reference=context.request_reference,
            app_id=context.app_id,
            capability_scope=context.capability_scope,
            capability_id=context.capability_id,
            capability_version=context.capability_version,
        )
        assert_context_rejected(instance, engine, snapshot, invalid)


def test_foreign_runtime_conversation_turn_and_expired_contexts_fail_closed():
    instance = runtime("6")
    engine, snapshot = conversation(instance, "0001")
    context = issue_context(instance, engine, snapshot)
    foreign_runtime = runtime("7")
    foreign_engine, foreign_snapshot = conversation(foreign_runtime, "0002")

    assert_context_rejected(foreign_runtime, foreign_engine, foreign_snapshot, context)
    assert not instance.validates_governed_metadata_context(
        context,
        observed_at=NOW,
        conversation_id="conv_meta_bind_9999",
        current_turn_reference=context.current_turn_reference,
        request_reference=context.request_reference,
        app_id=context.app_id,
        capability_scope=context.capability_scope,
        capability_id=context.capability_id,
        capability_version=context.capability_version,
    )
    assert not instance.validates_governed_metadata_context(
        context,
        observed_at=NOW,
        conversation_id=context.conversation_id,
        current_turn_reference="turn_meta_bind_9999",
        request_reference=context.request_reference,
        app_id=context.app_id,
        capability_scope=context.capability_scope,
        capability_id=context.capability_id,
        capability_version=context.capability_version,
    )
    assert not instance.validates_governed_metadata_context(
        context,
        observed_at=NOW + timedelta(seconds=METADATA_CONTEXT_TTL_SECONDS + 1),
        conversation_id=context.conversation_id,
        current_turn_reference=context.current_turn_reference,
        request_reference=context.request_reference,
        app_id=context.app_id,
        capability_scope=context.capability_scope,
        capability_id=context.capability_id,
        capability_version=context.capability_version,
    )


def test_capability_discovery_rejects_stale_turn_and_request_contexts():
    instance = runtime()
    engine, snapshot_a = conversation(instance, "0001")
    context_a = issue_context(instance, engine, snapshot_a)
    conversation_id = snapshot_a.metadata.conversation_id

    snapshot_b = record_turn(engine, conversation_id, suffix="0002", received_at=NOW + timedelta(seconds=1))
    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.capability_discovery.discover_for_conversation(
            conversation_engine=engine,
            conversation_snapshot=snapshot_b,
            request_context=request_context(instance, context_a),
            discovered_at=NOW + timedelta(seconds=2),
        )
    assert not instance.validates_governed_metadata_context(
        context_a,
        observed_at=NOW + timedelta(seconds=2),
        conversation_id=snapshot_b.metadata.conversation_id,
        current_turn_reference=snapshot_b.current_turn.turn_id,
        request_reference=snapshot_b.current_turn.request_reference,
        app_id=context_a.app_id,
        capability_scope=context_a.capability_scope,
        capability_id=context_a.capability_id,
        capability_version=context_a.capability_version,
    )

    snapshot_c = record_turn(
        engine,
        conversation_id,
        suffix="0003",
        received_at=NOW + timedelta(seconds=3),
        turn_id=context_a.current_turn_reference,
        request_reference="request:meta-bind:stale-request",
    )
    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.capability_discovery.discover_for_conversation(
            conversation_engine=engine,
            conversation_snapshot=snapshot_c,
            request_context=request_context(instance, context_a),
            discovered_at=NOW + timedelta(seconds=4),
        )


def test_raw_metadata_entry_points_reject_stale_governed_context_replay():
    instance = runtime()
    engine, snapshot_a = conversation(instance, "0001")
    context_a = issue_context(instance, engine, snapshot_a)
    conversation_id = snapshot_a.metadata.conversation_id
    record_turn(engine, conversation_id, suffix="0002", received_at=NOW + timedelta(seconds=1))
    replay_context = raw_replay_request_context(instance, context_a)

    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.discover_capabilities(
            request_context=replay_context,
            discovered_at=NOW + timedelta(seconds=2),
        )
    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.get_capability(
            "cap_conversation_context_0001",
            request_context=replay_context,
            discovered_at=NOW + timedelta(seconds=2),
        )


@pytest.mark.parametrize(
    "terminal_state",
    (AstraConversationLifecycleState.CLOSED, AstraConversationLifecycleState.FAULTED),
)
def test_raw_metadata_entry_points_reject_closed_or_faulted_conversation_replay(terminal_state):
    instance = runtime()
    engine, snapshot = conversation(instance, f"{terminal_state.value}_0001")
    context = issue_context(instance, engine, snapshot)
    conversation_id = snapshot.metadata.conversation_id
    if terminal_state is AstraConversationLifecycleState.CLOSED:
        engine.transition_conversation(
            conversation_id,
            AstraConversationLifecycleState.CLOSING,
            transitioned_at=NOW + timedelta(seconds=1),
            summary_reference="conversation:closing",
            entry_id=f"ctx_meta_bind_closing_{terminal_state.value}",
        )
        transitioned_at = NOW + timedelta(seconds=2)
    else:
        transitioned_at = NOW + timedelta(seconds=1)
    engine.transition_conversation(
        conversation_id,
        terminal_state,
        transitioned_at=transitioned_at,
        summary_reference=f"conversation:{terminal_state.value}",
        entry_id=f"ctx_meta_bind_{terminal_state.value}",
    )
    replay_context = raw_replay_request_context(instance, context)

    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.discover_capabilities(
            request_context=replay_context,
            discovered_at=NOW + timedelta(seconds=3),
        )
    with pytest.raises(AstraCapabilityDiscoveryError):
        instance.get_capability(
            "cap_conversation_context_0001",
            request_context=replay_context,
            discovered_at=NOW + timedelta(seconds=3),
        )


def test_wrong_app_scope_capability_and_version_fail_closed():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context = issue_context(instance, engine, snapshot)

    with pytest.raises(AstraRuntimeError):
        issue_context(instance, engine, snapshot, capability_id="subscription.unknown")
    for invalid in (
        context.model_copy(update={"app_id": "expense_tracker"}),
        context.model_copy(update={"capability_scope": "expense_tracker:private_read"}),
        context.model_copy(update={"capability_version": "9.9.9"}),
    ):
        assert_context_rejected(instance, engine, snapshot, invalid)


def test_declared_capability_must_match_trusted_context():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context = issue_context(instance, engine, snapshot, "subscription.count_active")

    with pytest.raises(AstraIntentResolutionError):
        instance.intent_resolution.resolve(
            intent_request(instance, engine, snapshot, context, target="subscription.count_all"),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            requester_context=request_context(instance, context),
        )


def test_intent_resolution_requires_same_exact_context_as_capability_discovery():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context_a = issue_context(instance, engine, snapshot, "subscription.count_active")
    context_b = issue_context(instance, engine, snapshot, "subscription.count_all")

    with pytest.raises(AstraIntentResolutionError):
        instance.intent_resolution.resolve(
            intent_request(instance, engine, snapshot, context_a, target="subscription.count_active"),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            requester_context=request_context(instance, context_b),
        )

    request_without_context = intent_request(
        instance,
        engine,
        snapshot,
        context_a,
        target="subscription.count_active",
    ).model_copy(update={"governed_metadata_context": None})
    with pytest.raises(AstraIntentResolutionError):
        instance.intent_resolution.resolve(
            request_without_context,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            requester_context=request_context(instance, context_a),
        )


def test_context_from_subscription_manager_cannot_be_reused_for_another_app():
    instance = runtime()
    engine, snapshot = conversation(instance)
    context = issue_context(instance, engine, snapshot)
    reused = context.model_copy(update={"app_id": "expense_tracker"})

    assert_context_rejected(instance, engine, snapshot, reused)


def test_disabled_activation_cannot_issue_metadata_context():
    instance = runtime_without_activation()
    engine, snapshot = conversation(instance)

    with pytest.raises(AstraRuntimeError):
        issue_context(instance, engine, snapshot)


def test_caller_cannot_construct_runtime_owned_metadata_context_issuer():
    with pytest.raises(AstraMetadataActivationBindingError):
        AstraGovernedMetadataContextIssuer(
            runtime_instance_id=RUNTIME_ID,
            issuer_reference="caller:metadata-context",
            _runtime_authority=object(),
            _runtime_owner=object(),
        )
