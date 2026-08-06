from __future__ import annotations

import inspect
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app.core.config import Settings, settings
from app.core.database import ParentBase, get_parent_db
from app.main import create_app
from app.modules.astra_ai.activation import load_runtime_activation
from app.modules.astra_ai import configuration as configuration_module
from app.modules.astra_ai.api.chat import chat_runtime_service, should_register_astra_chat_routes
from app.modules.astra_ai.chat_gateway import (
    AstraChatDeclaredIntent,
    AstraChatDeclaredParameter,
    AstraChatGateway,
    AstraChatRequest,
    AstraChatStatus,
)
import app.modules.astra_ai.chat_gateway as chat_gateway_module
from app.modules.astra_ai.configuration import _validate_astra_configuration_candidate, get_astra_configuration
from app.modules.astra_ai.runtime import AstraRuntime
from app.modules.auth.models import Role, User
from app.modules.auth.service import create_user_token, get_authenticated_user_context
from app.modules.subscription_manager.db import SubscriptionManagerBase, get_subscription_manager_db
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord


NOW = datetime(2026, 8, 2, 13, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "d" * 32


def setup_function():
    chat_runtime_service.shutdown()
    configuration_module._authoritative_astra_configuration.cache_clear()
    settings.APP_ENV = "development"
    settings.VERCEL_ENV = None
    settings.ASTRA_NONPROD_READ_ENABLED = "true"


def teardown_function():
    chat_runtime_service.shutdown()
    configuration_module._authoritative_astra_configuration.cache_clear()
    settings.APP_ENV = "development"
    settings.VERCEL_ENV = None
    settings.ASTRA_NONPROD_READ_ENABLED = "false"


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


def user(user_id: str = "user-a", *, status: str = "active") -> User:
    return User(
        id=user_id,
        email=f"{user_id}@example.com",
        name="User",
        password_hash="hash",
        status=status,
    )


def auth_db_user(user_id: str = "user-a", *, status: str = "active"):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    ParentBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(Role(id=2, name="Member", key="member"))
    db.add(user(user_id, status=status))
    db.commit()
    return db, db.get(User, user_id)


def auth_context(user_id: str = "user-a", *, status: str = "active"):
    db, authenticated_user = auth_db_user(user_id, status=status)
    assert authenticated_user is not None
    token = create_user_token(authenticated_user).access_token
    request = Request({"type": "http", "headers": []})
    return get_authenticated_user_context(request, bearer_token=token, db=db)


def subscription_db(
    owner_id: str = "user-a",
    *,
    active_name: str = "Netflix",
    active_provider: str = "Netflix",
):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SubscriptionManagerBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    category = SubscriptionCategory(id=f"cat-{owner_id}", owner_id=owner_id, name="Streaming")
    db.add_all(
        [
            category,
            SubscriptionRecord(
                id=f"sub-active-{owner_id}",
                owner_id=owner_id,
                category_id=category.id,
                name=active_name,
                provider=active_provider,
                billing_amount=10,
                currency_code="AED",
                billing_frequency="monthly",
                next_billing_date="2026-08-10",
                status="active",
            ),
            SubscriptionRecord(
                id=f"sub-paused-{owner_id}",
                owner_id=owner_id,
                category_id=category.id,
                name="Paused",
                provider="Paused",
                billing_amount=5,
                currency_code="AED",
                billing_frequency="monthly",
                next_billing_date="2026-08-11",
                status="paused",
            ),
        ]
    )
    db.commit()
    return db


def chat_request(capability_id: str = "subscription.count_active", **values) -> AstraChatRequest:
    return AstraChatRequest(
        declared_intent=AstraChatDeclaredIntent(capability_id=capability_id),
        **values,
    )


def gateway():
    return AstraChatGateway(runtime=runtime())


def http_client(parent_db, subscriptions_db) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_parent_db] = lambda: parent_db
    app.dependency_overrides[get_subscription_manager_db] = lambda: subscriptions_db
    return TestClient(app)


def test_authenticated_declared_subscription_intent_executes_real_governed_path():
    instance = runtime()
    chat = AstraChatGateway(runtime=instance)
    context = auth_context("user-a")
    db = subscription_db("user-a")

    response = chat.handle(
        chat_request("subscription.count_active"),
        authenticated_context=context,
        subscription_manager_db=db,
    )

    assert response.status is AstraChatStatus.OK
    assert response.capability_id == "subscription.count_active"
    assert response.structured_result is not None
    assert response.structured_result["summary"]["count"] == 1
    assert response.authorization_decision_reference
    assert response.governance_decision_reference
    assert response.resolved_intent
    assert response.structured_result["records"] == []
    assert "astra_chat_orchestration" in response.reason_codes
    assert "governed_read_execution_bridge" in response.reason_codes


def test_chat_uses_one_exact_runtime_issued_metadata_context_for_discovery_and_intent():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    with (
        patch.object(
            chat.runtime,
            "issue_subscription_manager_governed_metadata_context",
            wraps=chat.runtime.issue_subscription_manager_governed_metadata_context,
        ) as issue_context,
        patch.object(
            chat.runtime._capability_discovery,
            "discover_for_conversation",
            wraps=chat.runtime._capability_discovery.discover_for_conversation,
        ) as discover,
        patch.object(
            chat.runtime,
            "resolve_intent",
            wraps=chat.runtime.resolve_intent,
        ) as resolve,
    ):
        response = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )

    assert response.status is AstraChatStatus.OK
    intent_request = resolve.call_args.args[0]
    issued_context = intent_request.governed_metadata_context
    requester_context = resolve.call_args.kwargs["requester_context"]
    discovery_context = discover.call_args.kwargs["request_context"]
    assert issue_context.call_count == 1
    assert intent_request.governed_metadata_context is issued_context
    assert requester_context.governed_metadata_context is issued_context
    assert discovery_context.governed_metadata_context is issued_context


def test_positive_path_uses_no_governance_monkeypatch_or_force_allow_fixture():
    source = inspect.getsource(chat_gateway_module)
    assert "force_allow" not in source.lower()
    assert "monkeypatch" not in source.lower()
    assert "evaluate_governance = " not in source


def test_conversation_is_bound_to_exact_authenticated_principal():
    chat = gateway()
    db = subscription_db("user-a")
    context_a = auth_context("user-a")
    first = chat.handle(
        chat_request("subscription.count_active"),
        authenticated_context=context_a,
        subscription_manager_db=db,
    )
    second = chat.handle(
        chat_request("subscription.count_all", conversation_id=first.conversation_id),
        authenticated_context=context_a,
        subscription_manager_db=db,
    )
    assert second.status is AstraChatStatus.OK
    assert second.conversation_id == first.conversation_id

    context_b = auth_context("user-b")
    denied = chat.handle(
        chat_request("subscription.count_all", conversation_id=first.conversation_id),
        authenticated_context=context_b,
        subscription_manager_db=db,
    )
    assert denied.status is AstraChatStatus.DENIED
    assert "foreign_or_stale_conversation" in denied.reason_codes


def test_missing_declared_intent_returns_clarification_without_guessing():
    response = gateway().handle(
        AstraChatRequest(),
        authenticated_context=auth_context("user-a"),
        subscription_manager_db=subscription_db("user-a"),
    )

    assert response.status is AstraChatStatus.CLARIFICATION_REQUIRED
    assert response.clarification_required is True
    assert "natural_language_inference_not_enabled" in response.reason_codes


def test_unsupported_intent_app_or_capability_returns_bounded_unavailable_response():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    unsupported_capability = chat.handle(
        chat_request("subscription.unknown"),
        authenticated_context=context,
        subscription_manager_db=db,
    )
    assert unsupported_capability.status is AstraChatStatus.CAPABILITY_UNAVAILABLE
    assert "unsupported_capability" in unsupported_capability.reason_codes

    unsupported_app = chat.handle(
        AstraChatRequest(
            declared_intent=AstraChatDeclaredIntent(
                app_id="expense_tracker",
                capability_id="subscription.count_active",
            ),
        ),
        authenticated_context=context,
        subscription_manager_db=db,
    )
    assert unsupported_app.status is AstraChatStatus.CAPABILITY_UNAVAILABLE
    assert "unsupported_app" in unsupported_app.reason_codes


def test_chat_gateway_has_no_direct_sql_database_or_subscription_repository_surface():
    source = inspect.getsource(chat_gateway_module)
    lowered = source.lower()
    assert "sqlalchemy" not in lowered
    assert "repository" not in lowered
    assert "session" not in lowered
    assert "db.execute(" not in source
    assert "select(" not in source
    assert "execute_read_capability" not in source


def test_chat_gateway_cannot_bypass_read_authority_or_read_execution():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    with patch.object(chat.runtime, "authorize_subscription_manager_read", side_effect=RuntimeError("blocked")):
        denied = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )
    assert denied.status is AstraChatStatus.DENIED
    assert "governed_read_denied" in denied.reason_codes

    with patch.object(chat.runtime, "execute_read", side_effect=RuntimeError("blocked")):
        denied = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )
    assert denied.status is AstraChatStatus.DENIED
    assert "governed_read_denied" in denied.reason_codes


def test_exact_resolved_capability_lineage_is_required_for_read_authority():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")
    original = chat.runtime.resolve_intent

    def mismatched_resolution(*args, **kwargs):
        resolution = original(*args, **kwargs)
        return resolution.model_copy(update={"resolved_capability_ids": ("subscription.count_all",)})

    with patch.object(chat.runtime, "resolve_intent", side_effect=mismatched_resolution):
        denied = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )

    assert denied.status is AstraChatStatus.DENIED
    assert "governed_read_denied" in denied.reason_codes


def test_reusing_resolved_intent_for_another_subscription_capability_fails_closed():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    with patch.object(chat.runtime.read_authority, "authorize_subscription_manager_read") as authorize:
        authorize.side_effect = lambda **values: chat.runtime.authorize_subscription_manager_read(
            **(values | {"adapter_capability_id": "subscription.count_all"})
        )
        denied = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )

    assert denied.status is AstraChatStatus.DENIED
    assert "governed_read_denied" in denied.reason_codes


def test_caller_supplied_user_or_owner_id_cannot_change_ownership():
    with pytest.raises(ValidationError):
        AstraChatRequest.model_validate(
            {
                "declared_intent": {"capability_id": "subscription.count_active"},
                "owner_id": "user-b",
            }
        )
    with pytest.raises(ValidationError):
        AstraChatRequest.model_validate(
            {
                "declared_intent": {
                    "capability_id": "subscription.count_active",
                    "caller_supplied_user_id": "user-b",
                },
            }
        )

    response = gateway().handle(
        chat_request("subscription.count_active"),
        authenticated_context=auth_context("user-b"),
        subscription_manager_db=subscription_db("user-a"),
    )
    assert response.status is AstraChatStatus.OK
    assert response.structured_result["summary"]["count"] == 0


def test_legitimate_business_values_are_not_rejected_by_keyword_scanning():
    response = gateway().handle(
        chat_request("subscription.list_active"),
        authenticated_context=auth_context("user-a"),
        subscription_manager_db=subscription_db("user-a", active_name="1Password", active_provider="SQL Server"),
    )

    assert response.status is AstraChatStatus.OK
    assert response.structured_result is not None
    record = response.structured_result["records"][0]
    assert record["name"] == "1Password"
    assert record["provider"] == "SQL Server"


def test_response_projection_failure_returns_bounded_non_success():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")
    original = chat.runtime.read_execution.execute

    def unsupported_projection(*args, **kwargs):
        result = original(*args, **kwargs)
        return result.model_copy(update={"summary": dict(result.summary) | {"runtime_handle": "private"}})

    with patch.object(chat.runtime.read_execution, "execute", side_effect=unsupported_projection):
        response = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )

    assert response.status is AstraChatStatus.DENIED
    assert response.response_kind.value == "governed_denial"
    assert "governed_read_denied" in response.reason_codes


def test_parameter_field_and_row_limit_escalation_fail_closed():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    for request in (
        chat_request("subscription.count_active", requested_field_references=("subscription.secret",)),
        chat_request("subscription.count_active", requested_row_limit=100),
        AstraChatRequest(
            declared_intent=AstraChatDeclaredIntent(
                capability_id="subscription.count_active",
                parameters=(AstraChatDeclaredParameter(name="days", value=30),),
            ),
        ),
    ):
        response = chat.handle(request, authenticated_context=context, subscription_manager_db=db)
        assert response.status is AstraChatStatus.DENIED
        assert "governed_read_denied" in response.reason_codes


def test_read_authorization_or_governance_denial_returns_bounded_non_success():
    chat = gateway()
    context = auth_context("user-a")
    db = subscription_db("user-a")

    with patch.object(chat.runtime, "authorize_read_access", side_effect=RuntimeError("governance denied")):
        response = chat.handle(
            chat_request("subscription.count_active"),
            authenticated_context=context,
            subscription_manager_db=db,
        )

    assert response.status is AstraChatStatus.DENIED
    assert response.structured_result is None
    assert "governed_read_denied" in response.reason_codes


def test_no_provider_model_nlp_or_natural_language_path_exists():
    source = inspect.getsource(chat_gateway_module).lower()
    assert "openai" not in source
    assert "llm" not in source
    assert "embedding" not in source
    assert "vector" not in source
    assert "prompt" not in source
    assert "provider_payload" not in source


def test_unauthenticated_api_request_fails_before_chat_gateway_authority():
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/astra/chat",
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 401


def test_malformed_auth_api_request_fails_before_chat_gateway_authority():
    response = TestClient(create_app()).post(
        "/api/v1/astra/chat",
        headers={"Authorization": "Bearer malformed-token"},
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("blocked_status", ["disabled", "inactive", "suspended"])
def test_blocked_user_api_request_fails_at_authenticated_boundary(blocked_status):
    parent_db, blocked_user = auth_db_user(f"user-{blocked_status}", status=blocked_status)
    token = create_user_token(blocked_user).access_token
    client = http_client(parent_db, subscription_db(blocked_user.id))

    response = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 401


def test_authenticated_http_chat_success_uses_real_dependency_wiring():
    parent_db, authenticated_user = auth_db_user("user-http")
    token = create_user_token(authenticated_user).access_token
    subscriptions = subscription_db(
        "user-http",
        active_name="1Password",
        active_provider="SQL Server",
    )
    client = http_client(parent_db, subscriptions)

    response = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"declared_intent": {"capability_id": "subscription.list_active"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["capability_id"] == "subscription.list_active"
    assert body["structured_result"]["returned_count"] == 1
    assert body["structured_result"]["records"][0]["name"] == "1Password"
    assert body["structured_result"]["records"][0]["provider"] == "SQL Server"
    assert body["authorization_decision_reference"]
    assert body["governance_decision_reference"]


def test_authenticated_http_chat_answer_tracks_subscription_database_mutation():
    parent_db, authenticated_user = auth_db_user("user-http-db-proof")
    token = create_user_token(authenticated_user).access_token
    subscriptions = subscription_db("user-http-db-proof")
    client = http_client(parent_db, subscriptions)
    request = {
        "declared_intent": {
            "app_id": "subscription_manager",
            "declared_action": "get_information",
            "declared_subject": "subscription",
            "capability_id": "subscription.count_all",
        }
    }

    first = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json=request,
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["status"] == "ok"
    assert first_body["message"] == "Subscriptions: 2."
    assert first_body["structured_result"]["summary"]["count"] == 2

    subscriptions.add(
        SubscriptionRecord(
            id="sub-db-proof-added",
            owner_id="user-http-db-proof",
            category_id="cat-user-http-db-proof",
            name="Database Proof",
            provider="Database Proof",
            billing_amount=25,
            currency_code="AED",
            billing_frequency="monthly",
            next_billing_date="2026-08-20",
            status="active",
        )
    )
    subscriptions.commit()

    second = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json=request,
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["status"] == "ok"
    assert second_body["message"] == "Subscriptions: 3."
    assert second_body["structured_result"]["summary"]["count"] == 3
    assert second_body["authorization_decision_reference"]
    assert second_body["governance_decision_reference"]


def test_http_chat_disabled_activation_fails_closed_without_success():
    settings.ASTRA_NONPROD_READ_ENABLED = "false"
    configuration_module._authoritative_astra_configuration.cache_clear()
    parent_db, authenticated_user = auth_db_user("user-disabled")
    token = create_user_token(authenticated_user).access_token
    client = http_client(parent_db, subscription_db("user-disabled"))

    response = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] != "ok"
    assert body["structured_result"] is None


def test_http_chat_production_route_is_not_registered():
    chat_runtime_service.shutdown()
    settings.APP_ENV = "production"
    settings.VERCEL_ENV = None
    configuration_module._authoritative_astra_configuration.cache_clear()

    assert not should_register_astra_chat_routes(settings)
    response = TestClient(create_app()).post(
        "/api/v1/astra/chat",
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 404


def test_authenticated_http_chat_does_not_return_foreign_user_data():
    parent_db, authenticated_user = auth_db_user("user-http-foreign")
    token = create_user_token(authenticated_user).access_token
    client = http_client(parent_db, subscription_db("other-user"))

    response = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"declared_intent": {"capability_id": "subscription.count_active"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["structured_result"]["summary"]["count"] == 0


def test_authenticated_http_chat_unsupported_capability_is_bounded():
    parent_db, authenticated_user = auth_db_user("user-http-unsupported")
    token = create_user_token(authenticated_user).access_token
    client = http_client(parent_db, subscription_db("user-http-unsupported"))

    response = client.post(
        "/api/v1/astra/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"declared_intent": {"capability_id": "subscription.unknown"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "capability_unavailable"
    assert "unsupported_capability" in body["reason_codes"]
