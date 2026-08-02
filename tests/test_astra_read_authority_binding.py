from __future__ import annotations

import inspect
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.modules.astra_ai.capability_discovery import default_capabilities
from app.modules.astra_ai.capability_discovery import AstraCapabilityExecutionAuthority
from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, GovernanceOutcome
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.intent_resolution import AstraIntentRequest, AstraIntentStatus
from app.modules.astra_ai.read_access_authorization import (
    AstraNamedReadCapabilityRegistry,
    AstraReadAuthorizationError,
    AstraReadDecisionStatus,
)
import app.modules.astra_ai.read_authority_binding as read_authority_binding_module
from app.modules.astra_ai.read_authority_binding import (
    AstraReadAuthorityBindingError,
    certified_subscription_manager_read_registry,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads


NOW = datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "5" * 32


def runtime() -> AstraRuntime:
    instance = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
    instance.startup()
    force_allow(instance)
    return instance


def force_allow(instance: AstraRuntime) -> None:
    original = instance.evaluate_governance

    def evaluate(contract):
        result = original(contract)
        return result.model_copy(
            update={"decision": result.decision.model_copy(update={"outcome": GovernanceOutcome.ALLOW})}
        )

    instance.evaluate_governance = evaluate


def conversation(instance: AstraRuntime):
    engine = AstraConversationContextEngine(runtime=instance)
    engine.create_conversation(conversation_id="conv_read_auth_0001", created_at=NOW)
    engine.transition_conversation(
        "conv_read_auth_0001",
        AstraConversationLifecycleState.ACTIVE,
        transitioned_at=NOW,
        summary_reference="conversation:active",
        entry_id="ctx_read_auth_active_0001",
    )
    turn = AstraCurrentTurnContext(
        turn_id="turn_read_auth_0001",
        received_at=NOW,
        request_reference="request:read-auth:0001",
        turn_kind=AstraConversationTurnKind.USER_REQUEST,
        route_reference="route:/astra/read-authority",
    )
    engine.record_current_turn(
        "conv_read_auth_0001",
        turn,
        history_entry_id="ctx_read_auth_turn_0001",
        summary_reference="read-authority:declared",
    )
    return engine, engine.get_conversation("conv_read_auth_0001")


def resolved_intent(instance: AstraRuntime, engine: AstraConversationContextEngine, snapshot):
    binding = engine.issue_declared_intent_binding(
        conversation_snapshot=snapshot,
        declared_action="get_information",
        declared_subject="subscription_manager",
    )
    request = AstraIntentRequest(
        intent_request_id="intent_req_read_auth_0001",
        runtime_instance_id=instance.identity.startup_instance_id,
        conversation_id=snapshot.metadata.conversation_id,
        current_turn_reference=snapshot.current_turn.turn_id,
        request_reference=snapshot.current_turn.request_reference,
        declared_action="get_information",
        declared_subject="subscription_manager",
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
    result = instance.intent_resolution.resolve(
        request,
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        requester_context=instance.capability_discovery.internal_request_context(),
    )
    assert result.intent_status is AstraIntentStatus.RESOLVED
    return result


def test_runtime_bootstraps_exact_subscription_manager_read_capabilities():
    instance = runtime()
    summaries = instance.read_authority.capabilities()
    assert {item.adapter_capability_id for item in summaries} == {
        definition.capability_id for definition in subscription_reads.capability_catalog()
    }
    assert {item.owning_app_id for item in summaries} == {"subscription_manager"}
    assert len(summaries) == 10
    assert tuple(item.capability_id for item in default_capabilities()) == (
        "cap_conversation_context_0001",
        "cap_evidence_metadata_0001",
        "cap_governance_metadata_0001",
    )
    assert all(item.execution_authority is AstraCapabilityExecutionAuthority.METADATA_ONLY for item in default_capabilities())


def test_registry_rejects_duplicates_and_remains_sealed():
    capabilities = subscription_reads.read_authorization_capabilities()
    with pytest.raises(AstraReadAuthorizationError):
        AstraNamedReadCapabilityRegistry((capabilities[0], capabilities[0]))

    registry = certified_subscription_manager_read_registry()
    with pytest.raises(TypeError):
        registry._items["read_cap_foreign_0001"] = capabilities[0]


def test_runtime_owns_required_issuers_and_rejects_duplicate_or_foreign_binding():
    instance = runtime()
    engine = instance._read_access_authorization
    assert set(engine._issuers) == {
        "principal",
        "user",
        "tenant",
        "app",
        "record",
        "field",
        "purpose",
        "owner_acceptance",
    }

    with pytest.raises(AstraRuntimeError):
        instance._issue_read_authority_issuer("principal", "owner:duplicate")

    foreign = AstraRuntime(created_at=NOW, startup_instance_id="astra_rt_" + "6" * 32)
    foreign.startup()
    foreign_issuer = foreign._read_access_authorization._issuers["principal"]
    with pytest.raises(AstraReadAuthorizationError):
        engine.bind_certified_issuer("principal", foreign_issuer)
    foreign.shutdown()


def test_normal_runtime_path_authorizes_subscription_read_without_private_fixture_mutation():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    user = SimpleNamespace(id="user-a")

    with patch.object(instance._read_execution_bridge, "register_read_authorization_decision") as register:
        bound = instance.read_authority.authorize_subscription_manager_read(
            authenticated_user=user,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent,
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    assert bound.authorization_decision.decision_status is AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY
    assert bound.authorization_decision.owning_app_id == "subscription_manager"
    assert bound.authorization_request.plan_reference is None
    assert bound.app_read_grant.capability_id == "subscription.count_active"
    register.assert_called_once_with(
        bound.authorization_decision,
        registration_authority=instance._read_execution_registration_authority,
    )


def test_authority_binding_rejects_mismatches_and_uses_no_database_surface():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    user = SimpleNamespace(id="user-a")

    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_user=SimpleNamespace(id="user-b"),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent.model_copy(update={"intent_status": AstraIntentStatus.UNSUPPORTED}),
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_user=user,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent,
            adapter_capability_id="subscription.unknown",
            requested_at=NOW,
        )

    source = inspect.getsource(read_authority_binding_module)
    assert "sqlalchemy" not in source.lower()
    assert "Session" not in source
    assert ".execute(" not in source
    assert "select(" not in source


def test_runtime_shutdown_invalidates_read_authority_interface():
    instance = runtime()
    interface = instance.read_authority
    instance.shutdown()
    with pytest.raises(AstraRuntimeError):
        interface.capabilities()
