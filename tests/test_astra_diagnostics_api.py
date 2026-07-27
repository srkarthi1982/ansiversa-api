from __future__ import annotations

import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from app.modules.astra_ai.api.diagnostics import router
from app.modules.astra_ai.api.service import (
    diagnostics_service,
    runtime_service,
    should_register_diagnostics_routes,
)
from app.modules.auth.constants import ADMIN_ROLE_ID, DEFAULT_MEMBER_ROLE_ID
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User


def _client_with_admin() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/internal/astra/diagnostics")
    app.dependency_overrides[require_admin_user] = lambda: User(
        id="admin-user",
        email="admin@example.com",
        name="Admin",
        password_hash="hash",
        role_id=ADMIN_ROLE_ID,
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return TestClient(app)


def setup_function():
    runtime_service.shutdown()
    settings.APP_ENV = "development"
    settings.VERCEL_ENV = None
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True


def teardown_function():
    runtime_service.shutdown()
    settings.APP_ENV = "development"
    settings.VERCEL_ENV = None
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = False


def test_anonymous_caller_is_rejected_before_diagnostics_access():
    app = FastAPI()
    app.include_router(router, prefix="/internal/astra/diagnostics")

    response = TestClient(app).get("/internal/astra/diagnostics/health")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_non_admin_cannot_self_authorize_with_payload_role():
    app = FastAPI()
    app.include_router(router, prefix="/internal/astra/diagnostics")

    def reject_member():
        user = User(
            id="member-user",
            email="member@example.com",
            name="Member",
            password_hash="hash",
            role_id=DEFAULT_MEMBER_ROLE_ID,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        if user.role_id != ADMIN_ROLE_ID:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )
        return user

    app.dependency_overrides[require_admin_user] = reject_member

    response = TestClient(app).post(
        "/internal/astra/diagnostics/projections/runtime",
        json={"redaction_posture": "strict", "role": "admin"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_disabled_production_and_unknown_environment_fail_closed():
    client = _client_with_admin()
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = False
    disabled = client.get("/internal/astra/diagnostics/health")
    assert disabled.status_code == status.HTTP_404_NOT_FOUND
    assert disabled.json()["detail"]["code"] == "astra_diagnostics_disabled"

    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True
    settings.APP_ENV = "production"
    production = client.get("/internal/astra/diagnostics/health")
    assert production.status_code == status.HTTP_403_FORBIDDEN
    assert production.json()["detail"]["code"] == "non_production_required"

    settings.APP_ENV = "prodution"
    settings.VERCEL_ENV = None
    unknown = client.get("/internal/astra/diagnostics/health")
    assert unknown.status_code == status.HTTP_403_FORBIDDEN
    assert unknown.json()["detail"]["code"] == "non_production_required"


def test_route_registration_is_non_production_and_enabled_only():
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = False
    settings.APP_ENV = "development"
    assert not should_register_diagnostics_routes(settings)

    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True
    settings.APP_ENV = "development"
    assert should_register_diagnostics_routes(settings)

    settings.APP_ENV = "production"
    assert not should_register_diagnostics_routes(settings)


def test_runtime_projection_uses_strict_certified_projection_transport():
    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/runtime",
        json={"maximum_timeline_entries": 10},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    projection = body["data"]["projection"]
    assert body["status"] == "ok"
    assert projection["projection_kind"] == "runtime_summary"
    assert projection["redaction_state"] == "redacted"
    assert projection["authoritative_configuration_state"] == "disabled"
    assert projection["production_authorization_state"] == "not_approved"
    assert projection["api_exposure_authorized"] is False
    assert projection["production_exposure_approved"] is False
    _assert_no_private_material(body)


def test_metadata_only_redaction_is_not_authorized():
    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/runtime",
        json={"redaction_posture": "metadata_only"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"]["code"] == "metadata_only_not_authorized"


def test_evidence_projection_rejects_duplicates_and_preserves_missing_state():
    duplicate = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/evidence",
        json={"evidence_references": ["evd_missing_diag_0001", "evd_missing_diag_0001"]},
    )
    assert duplicate.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/evidence",
        json={"evidence_references": ["evd_missing_diag_0001"]},
    )

    assert response.status_code == status.HTTP_200_OK
    projection = response.json()["data"]["projection"]
    assert projection["projection_kind"] == "evidence_summary"
    assert projection["completeness"] in {"redacted", "unavailable"}
    assert projection["evidence_summaries"][0]["overall_integrity"] == "missing"
    assert projection["evidence_summaries"][0]["evidence_reference"] == "[redacted]"


def test_request_diagnostic_endpoint_is_bounded_unavailable():
    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/request",
        json={},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["error"]["code"] == "projection_unavailable"
    assert "correlation lookup service" in body["error"]["message"]
    _assert_no_private_material(body)


def test_component_health_projection_uses_fixed_allowlist_and_strict_output():
    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/components",
        json={
            "components": [
                "runtime",
                "capability_discovery",
                "intent_resolution",
                "planning",
                "read_access_authorization",
            ]
        },
    )

    assert response.status_code == status.HTTP_200_OK
    projection = response.json()["data"]["projection"]
    assert projection["projection_kind"] == "component_health_summary"
    assert projection["redaction_state"] == "redacted"
    assert {item["component_name"] for item in projection["component_states"]} >= {
        "runtime",
        "component_health_1",
        "component_health_2",
        "component_health_3",
        "component_health_4",
    }
    _assert_no_private_material(projection)


def test_main_app_does_not_register_diagnostics_in_production():
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True
    settings.APP_ENV = "production"
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/internal/astra/diagnostics/health" not in paths


def _assert_no_private_material(value):
    payload = json.dumps(value, sort_keys=True).lower()
    forbidden = (
        "authority_token",
        "proof_object",
        "credential",
        "password",
        "raw conversation",
        "prompt",
        "hidden reasoning",
        "select ",
        "provider_payload",
        "runtime handle",
        "app.modules.astra_ai",
    )
    assert not any(term in payload for term in forbidden)
