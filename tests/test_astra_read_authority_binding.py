from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.core.database import ParentBase
from app.modules.astra_ai.activation import load_runtime_activation
from app.modules.astra_ai.capability_discovery import default_capabilities
from app.modules.astra_ai.capability_discovery import AstraCapabilityExecutionAuthority
from app.modules.astra_ai.configuration import _validate_astra_configuration_candidate, get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference, FailurePosture, GovernanceOutcome
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationTurnKind,
    AstraCurrentTurnContext,
)
from app.modules.astra_ai.intent_resolution import (
    AstraIntentCategory,
    AstraIntentConfidence,
    AstraIntentResolution,
    AstraIntentStatus,
)
from app.modules.astra_ai.read_access_authorization import (
    AstraNamedReadCapabilityRegistry,
    AstraReadAuthorizationError,
    AstraReadDecisionStatus,
    AstraReadPurpose,
)
from app.modules.auth.models import User
from app.modules.auth.models import Role
from app.modules.auth.service import issue_authenticated_user_context
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
        instance = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        instance.startup()
    return instance


def _stage_zero_test_configuration():
    candidate = get_astra_configuration().configuration.model_dump(mode="json")
    return _validate_astra_configuration_candidate(candidate, loaded_at=NOW)


def user(user_id: str = "user-a") -> User:
    return User(id=user_id, email=f"{user_id}@example.com", name="User A", password_hash="hash", status="active")


def auth_context(user_id: str = "user-a"):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    ParentBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(Role(id=2, name="Member", key="member"))
    db.add(user(user_id))
    db.commit()
    authenticated_user = db.get(User, user_id)
    return issue_authenticated_user_context(authenticated_user, issued_at=NOW)


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
    return AstraIntentResolution(
        intent_id="intent_" + "1" * 24,
        intent_request_id="intent_req_read_auth_0001",
        runtime_instance_id=instance.identity.startup_instance_id,
        conversation_id=snapshot.metadata.conversation_id,
        current_turn_reference=snapshot.current_turn.turn_id,
        intent_status=AstraIntentStatus.RESOLVED,
        intent_confidence=AstraIntentConfidence.EXACT_MATCH,
        intent_category=AstraIntentCategory.INFORMATION_REQUEST,
        resolved_capability_ids=(),
        clarification_required=False,
        planning_eligible=False,
        governance_outcome=GovernanceOutcome.ALLOW,
        governance_decision_reference="read-auth-bind:intent-fixture",
        evidence_references=(),
        failure_posture=FailurePosture.NO_OP,
        resolved_at=NOW,
        version="1.0.0",
    )


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
    authenticated_context = auth_context()

    with patch.object(instance._read_execution_bridge, "register_read_authorization_decision") as register:
        bound = instance.read_authority.authorize_subscription_manager_read(
            authenticated_context=authenticated_context,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent,
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    assert bound.authorization_decision.decision_status is AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY
    assert bound.authorization_decision.governance_outcome.value == "allow"
    assert bound.authorization_decision.owning_app_id == "subscription_manager"
    assert bound.authorization_request.plan_reference is None
    assert bound.app_read_grant.capability_id == "subscription.count_active"
    assert (
        bound.app_read_grant.astra_authorization_reference.authorization_id
        == bound.authorization_decision.authorization_decision_id
    )
    assert (
        bound.app_read_grant.astra_authorization_reference.governance_decision_reference
        == bound.authorization_decision.governance_decision_reference
    )
    register.assert_called_once_with(
        bound.authorization_decision,
        registration_authority=instance._read_execution_registration_authority,
    )


def test_authority_binding_rejects_mismatches_and_uses_no_database_surface():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    authenticated_context = auth_context()

    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_context=authenticated_context,
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent.model_copy(update={"intent_status": AstraIntentStatus.UNSUPPORTED}),
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_context=authenticated_context,
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
    assert "._issuers" not in source
    assert "._evaluate_scope" not in source


def test_fake_user_and_foreign_principal_cannot_establish_authentication_authority():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_context=user("victim-user"),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent,
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    with pytest.raises(AstraReadAuthorityBindingError):
        instance.read_authority.authorize_subscription_manager_read(
            authenticated_context=SimpleNamespace(id="user-a"),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            intent_resolution=intent,
            adapter_capability_id="subscription.count_active",
            requested_at=NOW,
        )

    acceptance = subscription_reads.issue_owner_acceptance(
        authenticated_user=user("user-a"),
        principal_reference="principal:user-a",
        capability_id="subscription.count_active",
        read_capability_id=subscription_reads.read_capability_id_for_adapter("subscription.count_active"),
        request_reference="subscription/read-authority/foreign-principal",
        requested_fields=subscription_reads.default_read_fields_for_adapter("subscription.count_active"),
        requested_purpose=subscription_reads.default_read_purpose_for_adapter("subscription.count_active"),
        requested_maximum_result_count=50,
        parameters=(),
        observed_at=NOW,
    )
    assert not subscription_reads.default_read_grant_issuer().validates_owner_acceptance(
        acceptance,
        authenticated_user=user("user-b"),
        observed_at=NOW,
    )


def test_owner_acceptance_rejects_copy_expiry_and_foreign_app_tampering():
    authenticated_user = user()
    acceptance = subscription_reads.issue_owner_acceptance(
        authenticated_user=authenticated_user,
        principal_reference="principal:user-a",
        capability_id="subscription.count_active",
        read_capability_id=subscription_reads.read_capability_id_for_adapter("subscription.count_active"),
        request_reference="subscription/read-authority/tamper",
        requested_fields=subscription_reads.default_read_fields_for_adapter("subscription.count_active"),
        requested_purpose=subscription_reads.default_read_purpose_for_adapter("subscription.count_active"),
        requested_maximum_result_count=50,
        parameters=(),
        observed_at=NOW,
    )
    issuer = subscription_reads.default_read_grant_issuer()
    assert not issuer.validates_owner_acceptance(acceptance.model_copy(), authenticated_user=authenticated_user, observed_at=NOW)
    assert not issuer.validates_owner_acceptance(
        acceptance,
        authenticated_user=authenticated_user,
        observed_at=NOW + timedelta(minutes=16),
    )
    assert not issuer.validates_owner_acceptance(
        acceptance.model_copy(update={"app_scope": "app:foreign"}),
        authenticated_user=authenticated_user,
        observed_at=NOW,
    )


@pytest.mark.parametrize(
    ("patch_values", "error"),
    (
        ({"accepted_tenant_scope": "current_tenant"}, "tenant"),
        ({"request_reference": "subscription/read-authority/other"}, "request reference"),
        ({"capability_id": "subscription.count_all"}, "capability"),
        ({"capability_version": "9.9.9"}, "version"),
        ({"accepted_record_scope": "all_records"}, "record"),
        ({"accepted_field_references": ("subscription.count", "subscription.secret")}, "field"),
        ({"accepted_purpose": AstraReadPurpose.COMPLIANCE_REVIEW}, "purpose"),
        ({"accepted_parameters": (subscription_reads.SubscriptionAstraParameter(name="days", value=7),)}, "parameter"),
        ({"maximum_result_count": 1}, "limit"),
    ),
)
def test_app_authority_scope_escalation_is_rejected(patch_values, error):
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    authenticated_context = auth_context()
    original = subscription_reads.issue_owner_acceptance

    def tampered_acceptance(**values):
        return original(**values).model_copy(update=patch_values)

    with patch.object(subscription_reads, "issue_owner_acceptance", side_effect=tampered_acceptance):
        with pytest.raises((AstraReadAuthorityBindingError, Exception), match=error):
            instance.read_authority.authorize_subscription_manager_read(
                authenticated_context=authenticated_context,
                conversation_engine=engine,
                conversation_snapshot=snapshot,
                intent_resolution=intent,
                adapter_capability_id="subscription.count_active",
                requested_at=NOW,
            )


def test_copied_or_tampered_read_decision_cannot_issue_app_grant():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    authenticated_context = auth_context()

    def tampered_authorize(*args, **kwargs):
        decision = original_authorize(*args, **kwargs)
        return decision.model_copy(update={"governance_decision_reference": "READ-AUTH-GOV-FORGED"})

    original_authorize = instance.authorize_read_access
    with patch.object(instance, "authorize_read_access", side_effect=tampered_authorize):
        with pytest.raises(AstraReadAuthorityBindingError, match="exact issued"):
            instance.read_authority.authorize_subscription_manager_read(
                authenticated_context=authenticated_context,
                conversation_engine=engine,
                conversation_snapshot=snapshot,
                intent_resolution=intent,
                adapter_capability_id="subscription.count_active",
                requested_at=NOW,
            )


def test_static_matching_strings_without_app_owner_acceptance_do_not_authorize():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    authenticated_context = auth_context()

    with patch.object(subscription_reads, "issue_owner_acceptance", side_effect=RuntimeError("no app authority")):
        with pytest.raises(AstraReadAuthorityBindingError):
            instance.read_authority.authorize_subscription_manager_read(
                authenticated_context=authenticated_context,
                conversation_engine=engine,
                conversation_snapshot=snapshot,
                intent_resolution=intent,
                adapter_capability_id="subscription.count_active",
                requested_at=NOW,
            )


def test_field_purpose_and_parameter_escalation_rejected_before_authorization():
    instance = runtime()
    engine, snapshot = conversation(instance)
    intent = resolved_intent(instance, engine, snapshot)
    authenticated_context = auth_context()

    for values in (
        {"requested_field_references": ("subscription.secret",)},
        {"declared_purpose": AstraReadPurpose.COMPLIANCE_REVIEW},
        {"adapter_capability_id": "subscription.count_active", "parameters": (subscription_reads.SubscriptionAstraParameter(name="days", value=30),)},
    ):
        with pytest.raises(AstraReadAuthorityBindingError):
            instance.read_authority.authorize_subscription_manager_read(
                authenticated_context=authenticated_context,
                conversation_engine=engine,
                conversation_snapshot=snapshot,
                intent_resolution=intent,
                adapter_capability_id=values.pop("adapter_capability_id", "subscription.count_active"),
                requested_at=NOW,
                **values,
            )


def test_runtime_shutdown_invalidates_read_authority_interface():
    instance = runtime()
    interface = instance.read_authority
    instance.shutdown()
    with pytest.raises(AstraRuntimeError):
        interface.capabilities()
