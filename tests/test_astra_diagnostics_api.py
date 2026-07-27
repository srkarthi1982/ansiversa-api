from __future__ import annotations

import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from app.modules.astra_ai.api.diagnostics import (
    DIAGNOSTICS_ROUTE_PREFIX,
    register_astra_diagnostics_validation_handler,
    router,
)
from app.modules.astra_ai.api.service import (
    AstraDiagnosticsApiError,
    diagnostics_service,
    runtime_service,
    should_register_diagnostics_routes,
)
from app.modules.astra_ai.api.schemas import AstraDiagnosticsErrorCode
from app.modules.astra_ai.diagnostic_projection import (
    AstraDiagnosticProjectionError,
    AstraDiagnosticProjectionKind,
    AstraDiagnosticRedactionPosture,
    AstraDiagnosticSection,
)
from app.modules.astra_ai.runtime import AstraRuntimeError
from app.modules.auth.constants import ADMIN_ROLE_ID, DEFAULT_MEMBER_ROLE_ID
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User


def _client_with_admin() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/internal/astra/diagnostics")
    register_astra_diagnostics_validation_handler(app)
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


def _main_app_with_admin() -> FastAPI:
    app = create_app()
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
    return app


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


def test_diagnostics_validation_errors_are_bounded_without_rejected_input():
    cases = [
        (
            "/internal/astra/diagnostics/projections/runtime",
            {"authority_token": "controlled"},
        ),
        (
            "/internal/astra/diagnostics/projections/evidence",
            {
                "evidence_references": ["evd_missing_diag_0001"],
                "query": "SELECT private_value FROM secrets",
            },
        ),
        (
            "/internal/astra/diagnostics/projections/runtime",
            {
                "provider_payload": {
                    "messages": [
                        {"role": "user", "content": "prompt text with credential secret"}
                    ]
                }
            },
        ),
        (
            "/internal/astra/diagnostics/projections/evidence",
            {"evidence_references": ["credential-secret-reference"]},
        ),
        (
            "/internal/astra/diagnostics/projections/components",
            {"components": ["app.modules.astra_ai.runtime"]},
        ),
    ]

    client = _client_with_admin()
    for path, payload in cases:
        response = client.post(path, json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        body = response.json()
        assert body == {
            "detail": {
                "code": "projection_request_invalid",
                "message": "Astra diagnostics request validation failed.",
            }
        }
        _assert_no_member_named_input(body)
        _assert_no_private_material(body)


def test_diagnostics_validation_handler_does_not_change_unrelated_api_validation():
    app = FastAPI()
    register_astra_diagnostics_validation_handler(app)

    @app.post(DIAGNOSTICS_ROUTE_PREFIX)
    def diagnostics_root(payload: AstraRuntimeProjectionRequest):
        return payload

    @app.post(f"{DIAGNOSTICS_ROUTE_PREFIX}/projections/runtime")
    def diagnostics_nested(payload: AstraRuntimeProjectionRequest):
        return payload

    @app.post("/internal/astra/diagnostics-other")
    def diagnostics_other(payload: AstraRuntimeProjectionRequest):
        return payload

    @app.post("/internal/astra/diagnostics2")
    def diagnostics2(payload: AstraRuntimeProjectionRequest):
        return payload

    @app.post("/unrelated")
    def unrelated(payload: AstraRuntimeProjectionRequest):
        return payload

    client = TestClient(app)
    for path in (DIAGNOSTICS_ROUTE_PREFIX, f"{DIAGNOSTICS_ROUTE_PREFIX}/projections/runtime"):
        response = client.post(path, json={"authority_token": "controlled"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": {
                "code": "projection_request_invalid",
                "message": "Astra diagnostics request validation failed.",
            }
        }

    for path in (
        "/internal/astra/diagnostics-other",
        "/internal/astra/diagnostics2",
        "/unrelated",
    ):
        response = client.post(path, json={"authority_token": "controlled"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert isinstance(response.json()["detail"], list)
        assert "input" in response.json()["detail"][0]


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
        "component_health_1",
        "component_health_2",
        "component_health_3",
    }
    _assert_no_private_material(projection)


def test_component_health_rejects_runtime_scope_and_unsupported_components():
    client = _client_with_admin()
    cases = [
        {"components": ["runtime"]},
        {"components": ["runtime", "planning"]},
        {"components": ["planning", "planning"]},
        {"components": ["unknown_component"]},
    ]

    for payload in cases:
        response = client.post("/internal/astra/diagnostics/projections/components", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        body = response.json()
        assert body["detail"]["code"] == "projection_request_invalid"
        assert body["detail"]["message"] == "Astra diagnostics request validation failed."
        _assert_no_member_named_input(body)
        _assert_no_private_material(body)


def test_each_component_health_scope_individually_succeeds():
    client = _client_with_admin()
    for component in (
        "capability_discovery",
        "intent_resolution",
        "planning",
        "read_access_authorization",
    ):
        response = client.post(
            "/internal/astra/diagnostics/projections/components",
            json={"components": [component]},
        )

        assert response.status_code == status.HTTP_200_OK
        projection = response.json()["data"]["projection"]
        assert projection["projection_kind"] == "component_health_summary"
        assert any(
            item["component_name"] == "component_health_1"
            for item in projection["component_states"]
        )
        _assert_no_private_material(projection)


def test_main_app_does_not_register_diagnostics_in_production():
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True
    settings.APP_ENV = "production"
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/internal/astra/diagnostics/health" not in paths


def test_enabled_app_shutdown_stops_runtime_and_invalidates_captured_interface():
    app = _main_app_with_admin()

    with TestClient(app) as client:
        response = client.get("/internal/astra/diagnostics/health")
        assert response.status_code == status.HTTP_200_OK
        captured_interface = runtime_service.require_runtime().diagnostic_projection

    with pytest_raises_runtime_error():
        captured_interface.health()
    with pytest_raises_api_error("runtime_unavailable"):
        runtime_service.require_runtime()


def test_issued_projection_request_cannot_be_reused_after_app_shutdown():
    app = _main_app_with_admin()

    with TestClient(app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_200_OK
        runtime = runtime_service.require_runtime()
        observed_at = datetime.now().astimezone()
        runtime_health = runtime.health(observed_at=observed_at)
        issued_request = runtime.diagnostic_projection.issue_request(
            projection_request_id="diag_req_api_shutdown_reuse_0001",
            projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
            requested_sections=(AstraDiagnosticSection.RUNTIME,),
            maximum_timeline_entries=10,
            requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
            requested_at=observed_at,
            runtime_health=runtime_health,
        )
        captured_interface = runtime.diagnostic_projection

    with pytest_raises_runtime_error():
        captured_interface.project(issued_request, created_at=datetime.now().astimezone())


def test_disabled_and_production_apps_do_not_start_diagnostics_runtime():
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = False
    disabled_app = create_app()
    with TestClient(disabled_app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_404_NOT_FOUND
    with pytest_raises_api_error("runtime_unavailable"):
        runtime_service.require_runtime()

    settings.ASTRA_DIAGNOSTICS_API_ENABLED = True
    settings.APP_ENV = "production"
    production_app = create_app()
    with TestClient(production_app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_404_NOT_FOUND
    with pytest_raises_api_error("runtime_unavailable"):
        runtime_service.require_runtime()


def test_multiple_app_lifecycles_do_not_retain_runtime_state():
    first_app = _main_app_with_admin()
    with TestClient(first_app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_200_OK
        first_runtime_id = runtime_service.require_runtime().identity.startup_instance_id
    with pytest_raises_api_error("runtime_unavailable"):
        runtime_service.require_runtime()

    second_app = _main_app_with_admin()
    with TestClient(second_app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_200_OK
        second_runtime_id = runtime_service.require_runtime().identity.startup_instance_id

    assert first_runtime_id != second_runtime_id


def test_shutdown_is_idempotent():
    app = _main_app_with_admin()
    with TestClient(app) as client:
        assert client.get("/internal/astra/diagnostics/health").status_code == status.HTTP_200_OK

    runtime_service.shutdown()
    runtime_service.shutdown()
    with pytest_raises_api_error("runtime_unavailable"):
        runtime_service.require_runtime()


def test_request_issuance_failure_returns_bounded_error(monkeypatch):
    def fail(_payload):
        raise AstraDiagnosticProjectionError(
            "raw app.modules.astra_ai authority_token stack trace should not leak"
        )

    monkeypatch.setattr(diagnostics_service, "_runtime_projection", fail)

    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/runtime",
        json={},
    )

    assert_bounded_failure(response, "projection_request_invalid")


def test_runtime_lifecycle_failure_returns_bounded_error(monkeypatch):
    def fail():
        raise AstraRuntimeError(
            "raw app.modules.astra_ai runtime handle stack trace should not leak"
        )

    monkeypatch.setattr(diagnostics_service, "_health", fail)

    response = _client_with_admin().get("/internal/astra/diagnostics/health")

    assert_bounded_failure(response, "runtime_unavailable")


def test_component_health_failure_returns_bounded_error(monkeypatch):
    def fail(_payload):
        raise AstraRuntimeError(
            "raw app.modules.astra_ai component authority state should not leak"
        )

    monkeypatch.setattr(diagnostics_service, "_component_health_projection", fail)

    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/components",
        json={},
    )

    assert_bounded_failure(response, "runtime_unavailable")


def test_projection_creation_failure_returns_bounded_error(monkeypatch):
    def fail(_runtime, _request, *, observed_at):
        raise AstraDiagnosticsApiError(
            code=AstraDiagnosticsErrorCode.PROJECTION_UNAVAILABLE,
            message="Astra certified diagnostic projection is unavailable.",
        )

    monkeypatch.setattr("app.modules.astra_ai.api.service._projection_envelope", fail)

    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/runtime",
        json={},
    )

    assert_bounded_failure(response, "projection_unavailable")


def test_unexpected_service_exception_returns_internal_failure(monkeypatch):
    def fail(_payload):
        raise RuntimeError(
            "raw app.modules.astra_ai provider_payload stack trace should not leak"
        )

    monkeypatch.setattr(diagnostics_service, "_runtime_projection", fail)

    response = _client_with_admin().post(
        "/internal/astra/diagnostics/projections/runtime",
        json={},
    )

    assert_bounded_failure(response, "internal_diagnostic_failure")


def assert_bounded_failure(response, expected_code: str):
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["detail"]["code"] == expected_code
    _assert_no_private_material(body)


class pytest_raises_api_error:
    def __init__(self, expected_code: str) -> None:
        self.expected_code = expected_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, _traceback):
        assert exc_type is AstraDiagnosticsApiError
        assert exc_value.code.value == self.expected_code
        return True


class pytest_raises_runtime_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, _exc_value, _traceback):
        assert exc_type is AstraRuntimeError
        return True


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


def _assert_no_member_named_input(value):
    if isinstance(value, dict):
        assert "input" not in value
        for item in value.values():
            _assert_no_member_named_input(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_member_named_input(item)
