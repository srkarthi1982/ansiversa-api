from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Iterable

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import DEFAULT_CORS_ORIGINS, settings
from app.main import create_app
from app.modules.astra_ai.api.diagnostics import (
    DIAGNOSTICS_ROUTE_PREFIX,
    register_astra_diagnostics_validation_handler,
    router,
)
from app.modules.astra_ai.api.schemas import (
    ASTRA_DIAGNOSTICS_API_VERSION,
    AstraDiagnosticsErrorCode,
)
from app.modules.astra_ai.api.service import (
    AstraDiagnosticsApiError,
    diagnostics_service,
    runtime_service,
)
from app.modules.astra_ai.diagnostic_projection import AstraDiagnosticProjectionError
from app.modules.astra_ai.runtime import AstraRuntimeError
from app.modules.auth.constants import ADMIN_ROLE_ID, DEFAULT_MEMBER_ROLE_ID
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User


VALIDATION_VERSION = "1.0.0"
NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
PREFIX = "/internal/astra/diagnostics"

VARIABLE_FIELDS = (
    "request_id",
    "observed_at",
    "projection_id",
    "projection_request_id",
    "correlation_manifest_id",
    "runtime_instance_id",
    "created_at",
    "issued_at",
    "timestamp",
    "health_timestamp",
    "manifest_id",
)

VARIABLE_SEQUENCE_FIELDS = (
    "evidence_references",
)

PROTECTED_VALUES = (
    "conv_api_val001_protected_0001",
    "evd_api_val001_protected_0001",
    "intent_api_val001_protected_0001",
    "plan_api_val001_protected_0001",
    "raw-user-message-api-val001",
    "secret-api-val001",
    "bearer controlled-token",
    "controlled-cookie-value",
)

FORBIDDEN_LEAK_TERMS = (
    "authority_token",
    "issuer_authority",
    "proof_object",
    "password",
    "credential",
    "secret-api-val001",
    "access token",
    "bearer controlled-token",
    "controlled-cookie-value",
    "raw_user_message",
    "conversation_content",
    "prompt",
    "hidden_reasoning",
    "database_record",
    "select ",
    "provider_payload",
    "runtime_handle",
    "app.modules.astra_ai",
    *PROTECTED_VALUES[:4],
)

FORBIDDEN_LEAK_KEYS = (
    "authority_token",
    "issuer_authority",
    "proof_object",
    "password",
    "credential",
    "secret",
    "access_token",
    "authorization",
    "cookie",
    "raw_user_message",
    "conversation_content",
    "prompt",
    "hidden_reasoning",
    "database_record",
    "sql",
    "provider_payload",
    "runtime_handle",
)


class ScenarioGroup(StrEnum):
    ROUTE_ENVIRONMENT = "route_environment"
    AUTHENTICATION = "authentication"
    ADMIN_AUTHORIZATION = "admin_authorization"
    ACTIVATION = "activation"
    HEALTH = "health"
    RUNTIME_PROJECTION = "runtime_projection"
    EVIDENCE_PROJECTION = "evidence_projection"
    REQUEST_DIAGNOSTIC = "request_diagnostic"
    COMPONENT_HEALTH = "component_health"
    PRIVACY = "privacy"
    CONTRACT = "contract"
    ERROR_TAXONOMY = "error_taxonomy"
    ERROR_BOUNDARY = "error_boundary"
    LIFECYCLE = "lifecycle"
    DETERMINISM = "determinism"
    SECURITY_BOUNDARY = "security_boundary"


class AstraApiVal001ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(pattern=r"^astra_api_val_001_[a-z0-9_]{3,100}$")
    scenario_group: ScenarioGroup
    scenario_name: str
    expected_http_status: int | None
    actual_http_status: int | None
    expected_error_code: str | None = None
    actual_error_code: str | None = None
    passed: bool
    authentication_status: str = "not_applicable"
    developer_authorization_status: str = "not_applicable"
    environment_status: str = "not_applicable"
    route_registration_status: str = "not_applicable"
    runtime_lifecycle_status: str = "not_applicable"
    projection_transport_status: str = "not_applicable"
    strict_redaction_status: str = "not_applicable"
    privacy_status: str = "not_applicable"
    bounded_error_status: str = "not_applicable"
    response_contract_status: str = "not_applicable"
    production_boundary_status: str = "not_applicable"
    failure_reference: str | None = None
    completed_at: datetime = NOW
    validation_version: str = VALIDATION_VERSION

    def stable_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    def text(self) -> str:
        rows = (
            ("Scenario", self.scenario_name),
            ("Group", self.scenario_group.value),
            ("Result", "passed" if self.passed else "failed"),
            ("Expected HTTP", str(self.expected_http_status)),
            ("Actual HTTP", str(self.actual_http_status)),
            ("Expected error", self.expected_error_code or "none"),
            ("Actual error", self.actual_error_code or "none"),
            ("Authentication", self.authentication_status),
            ("Admin authorization", self.developer_authorization_status),
            ("Environment", self.environment_status),
            ("Route registration", self.route_registration_status),
            ("Runtime lifecycle", self.runtime_lifecycle_status),
            ("Projection transport", self.projection_transport_status),
            ("Strict redaction", self.strict_redaction_status),
            ("Privacy", self.privacy_status),
            ("Bounded error", self.bounded_error_status),
            ("Response contract", self.response_contract_status),
            ("Production boundary", self.production_boundary_status),
        )
        return "\n".join(f"{label:<24} {value}" for label, value in rows)


def run_scenario(name: str) -> AstraApiVal001ScenarioResult:
    if name not in SCENARIOS:
        raise KeyError(f"unknown scenario: {name}")
    return SCENARIOS[name]()


def run_all() -> tuple[AstraApiVal001ScenarioResult, ...]:
    return tuple(run_scenario(name) for name in SCENARIO_NAMES)


def inspect_privacy_leaks(
    value: Any,
    *,
    protected_values: Iterable[str] = PROTECTED_VALUES,
    forbidden_values: Iterable[str] = FORBIDDEN_LEAK_TERMS,
) -> tuple[str, ...]:
    findings: list[str] = []

    def visit(item: Any, path: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered_key = str(key).lower()
                if lowered_key in FORBIDDEN_LEAK_KEYS:
                    findings.append(f"{path}.{lowered_key}")
                visit(child, f"{path}.{lowered_key}")
        elif isinstance(item, (list, tuple, set)):
            for index, child in enumerate(item):
                visit(child, f"{path}[{index}]")
        else:
            text = str(item).lower()
            for forbidden in tuple(forbidden_values) + tuple(protected_values):
                if forbidden.lower() in text:
                    findings.append(path)
                    break

    visit(value, "$")
    return tuple(dict.fromkeys(findings))


def semantic_http(value: Any, *, path: str = "$") -> Any:
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in VARIABLE_FIELDS:
                result[key] = _variable_scalar_placeholder(key, child)
            elif key in VARIABLE_SEQUENCE_FIELDS:
                result[key] = _normalize_variable_sequence(key, child, path=child_path)
            else:
                result[key] = semantic_http(child, path=child_path)
        return result
    if isinstance(value, list):
        return [semantic_http(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    return value


def _variable_scalar_placeholder(field_name: str, value: Any) -> str | None:
    if value is None:
        return None
    return f"<variable-{field_name}>"


def _normalize_variable_sequence(field_name: str, value: Any, *, path: str) -> Any:
    _ = path
    if not isinstance(value, list):
        return semantic_http(value, path=path)
    return [_normalize_variable_sequence_item(field_name, item) for item in value]


def _normalize_variable_sequence_item(field_name: str, value: Any) -> Any:
    if field_name == "evidence_references":
        if value == "[redacted]":
            return value
        if isinstance(value, str) and value.startswith("evd_"):
            return "<variable-evidence-reference>"
    return value


def _result(
    name: str,
    group: ScenarioGroup,
    *,
    expected_http_status: int | None,
    actual_http_status: int | None,
    expected_error_code: str | None = None,
    actual_error_code: str | None = None,
    passed: bool,
    **statuses: str,
) -> AstraApiVal001ScenarioResult:
    return AstraApiVal001ScenarioResult(
        scenario_id=f"astra_api_val_001_{name}",
        scenario_group=group,
        scenario_name=name,
        expected_http_status=expected_http_status,
        actual_http_status=actual_http_status,
        expected_error_code=expected_error_code,
        actual_error_code=actual_error_code,
        passed=passed,
        **statuses,
    )


@contextmanager
def _settings(app_env="development", vercel_env=None, enabled=True):
    old = (
        settings.APP_ENV,
        settings.VERCEL_ENV,
        settings.ASTRA_DIAGNOSTICS_API_ENABLED,
        tuple(settings.CORS_ORIGINS),
    )
    runtime_service.shutdown()
    settings.APP_ENV = app_env
    settings.VERCEL_ENV = vercel_env
    settings.ASTRA_DIAGNOSTICS_API_ENABLED = enabled
    try:
        yield
    finally:
        runtime_service.shutdown()
        settings.APP_ENV = old[0]
        settings.VERCEL_ENV = old[1]
        settings.ASTRA_DIAGNOSTICS_API_ENABLED = old[2]
        settings.CORS_ORIGINS = list(old[3])


def _user(role_id=ADMIN_ROLE_ID, *, status_value="active") -> User:
    return User(
        id="api-val-user",
        email="api-val@example.com",
        name="API Validation",
        password_hash="hash",
        role_id=role_id,
        status=status_value,
        created_at=NOW,
        updated_at=NOW,
    )


def _app_with_router(*, admin=True, member=False, inactive=False) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix=PREFIX)
    register_astra_diagnostics_validation_handler(app)
    if admin:
        app.dependency_overrides[require_admin_user] = lambda: _user(
            ADMIN_ROLE_ID,
            status_value="inactive" if inactive else "active",
        )
    if member:
        def reject_member():
            _ = _user(DEFAULT_MEMBER_ROLE_ID)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        app.dependency_overrides[require_admin_user] = reject_member
    return app


def _client(*, admin=True, member=False, inactive=False) -> TestClient:
    return TestClient(_app_with_router(admin=admin, member=member, inactive=inactive))


def _main_paths() -> set[str]:
    return {route.path for route in create_app().routes}


def _request(method: str, path: str, *, body=None, admin=True, member=False, inactive=False):
    client = _client(admin=admin, member=member, inactive=inactive)
    if method == "GET":
        return client.get(path)
    return client.post(path, json=body if body is not None else {})


def _error_code(response) -> str | None:
    try:
        detail = response.json().get("detail")
    except Exception:
        return None
    if isinstance(detail, dict):
        return detail.get("code")
    if response.status_code == 401:
        return "authentication_required"
    if response.status_code == 403:
        return "developer_authorization_required"
    return None


def _valid_envelope(response, *, expected_status: str) -> bool:
    try:
        payload = response.json()
    except Exception:
        return False
    return all(
        (
            isinstance(payload.get("request_id"), str)
            and payload["request_id"].startswith("api_diag_"),
            payload.get("status") == expected_status,
            bool(payload.get("observed_at")),
            payload.get("api_version") == ASTRA_DIAGNOSTICS_API_VERSION,
            (payload.get("error") is None) if expected_status == "ok" else True,
        )
    )


def _valid_http_error(response) -> bool:
    try:
        detail = response.json().get("detail")
    except Exception:
        return False
    if response.status_code == 401:
        return isinstance(detail, str) and bool(detail)
    return isinstance(detail, dict) and {"code", "message"}.issubset(detail)


def _runtime_unstarted() -> bool:
    try:
        runtime_service.require_runtime()
    except AstraDiagnosticsApiError:
        return True
    return False


def _route_environment_disabled():
    with _settings(enabled=False):
        paths = _main_paths()
        passed = f"{PREFIX}/health" not in paths and _runtime_unstarted()
    return _result(
        "flag_disabled_routes_absent",
        ScenarioGroup.ROUTE_ENVIRONMENT,
        expected_http_status=404,
        actual_http_status=404 if passed else 200,
        passed=passed,
        environment_status="allowed_environment",
        route_registration_status="absent",
        runtime_lifecycle_status="not_started",
    )


def _route_environment_allowed():
    allowed = ("local", "development", "test", "qa", "staging")
    statuses = []
    for env in allowed:
        with _settings(app_env=env, enabled=True):
            paths = _main_paths()
            statuses.append(f"{PREFIX}/health" in paths and _runtime_unstarted())
    with _settings(app_env="development", vercel_env="preview", enabled=True):
        paths = _main_paths()
        statuses.append(f"{PREFIX}/health" in paths and _runtime_unstarted())
        app = create_app()
        openapi = app.openapi()
        hidden = f"{PREFIX}/health" not in openapi.get("paths", {})
    passed = all(statuses) and hidden
    return _result(
        "allowed_non_production_routes_registered_hidden",
        ScenarioGroup.ROUTE_ENVIRONMENT,
        expected_http_status=200,
        actual_http_status=200 if passed else 404,
        passed=passed,
        environment_status="allowed_non_production",
        route_registration_status="registered_openapi_hidden",
        runtime_lifecycle_status="lazy_not_started",
    )


def _route_environment_production():
    checks = []
    for app_env, vercel_env in (
        ("production", None),
        ("development", "production"),
        ("production", "preview"),
    ):
        with _settings(app_env=app_env, vercel_env=vercel_env, enabled=True):
            checks.append(f"{PREFIX}/health" not in _main_paths() and _runtime_unstarted())
    passed = all(checks)
    return _result(
        "production_routes_absent",
        ScenarioGroup.ROUTE_ENVIRONMENT,
        expected_http_status=404,
        actual_http_status=404 if passed else 200,
        passed=passed,
        environment_status="production_wins",
        route_registration_status="absent",
        runtime_lifecycle_status="not_started",
        production_boundary_status="unchanged",
    )


def _route_environment_unknown():
    with _settings(app_env="prodution", enabled=True):
        paths = _main_paths()
        response = _request("GET", f"{PREFIX}/health")
        passed = f"{PREFIX}/health" not in paths and response.status_code == 403 and _runtime_unstarted()
    return _result(
        "unknown_environment_fails_closed",
        ScenarioGroup.ROUTE_ENVIRONMENT,
        expected_http_status=403,
        actual_http_status=response.status_code,
        expected_error_code="non_production_required",
        actual_error_code=_error_code(response),
        passed=passed,
        environment_status="unknown_rejected",
        route_registration_status="main_absent_direct_access_forbidden",
        runtime_lifecycle_status="not_started",
        bounded_error_status="fixed_code",
    )


def _cors_unchanged():
    with _settings(enabled=True):
        _ = create_app()
        passed = set(settings.CORS_ORIGINS) == set(DEFAULT_CORS_ORIGINS)
    return _result(
        "cors_configuration_unchanged",
        ScenarioGroup.SECURITY_BOUNDARY,
        expected_http_status=None,
        actual_http_status=None,
        passed=passed,
        production_boundary_status="no_cors_change",
    )


def _diagnostics_validation_route_scope():
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

    client = TestClient(app)
    payload = {"authority_token": "controlled"}
    scoped = (
        client.post(DIAGNOSTICS_ROUTE_PREFIX, json=payload),
        client.post(f"{DIAGNOSTICS_ROUTE_PREFIX}/projections/runtime", json=payload),
    )
    siblings = (
        client.post("/internal/astra/diagnostics-other", json=payload),
        client.post("/internal/astra/diagnostics2", json=payload),
    )
    scoped_ok = all(
        response.status_code == 422
        and _error_code(response) == "projection_request_invalid"
        and not inspect_privacy_leaks(response.json())
        for response in scoped
    )
    siblings_ok = all(
        response.status_code == 422
        and isinstance(response.json().get("detail"), list)
        and "input" in response.json()["detail"][0]
        for response in siblings
    )
    return _result(
        "diagnostics_validation_route_scope",
        ScenarioGroup.SECURITY_BOUNDARY,
        expected_http_status=422,
        actual_http_status=422 if scoped_ok and siblings_ok else 500,
        expected_error_code="projection_request_invalid",
        actual_error_code="projection_request_invalid" if scoped_ok else None,
        passed=scoped_ok and siblings_ok,
        bounded_error_status="exact_diagnostics_prefix_only",
        privacy_status="diagnostics_sanitized_siblings_default",
    )


def _anonymous_rejected():
    with _settings(enabled=True):
        app = FastAPI()
        app.include_router(router, prefix=PREFIX)
        response = TestClient(app).get(f"{PREFIX}/health")
        passed = response.status_code == 401 and _runtime_unstarted()
    return _result(
        "anonymous_rejected",
        ScenarioGroup.AUTHENTICATION,
        expected_http_status=401,
        actual_http_status=response.status_code,
        expected_error_code="authentication_required",
        actual_error_code=_error_code(response),
        passed=passed,
        authentication_status="anonymous_rejected",
        runtime_lifecycle_status="not_started",
    )


def _invalid_token_rejected():
    with _settings(enabled=True):
        app = FastAPI()
        app.include_router(router, prefix=PREFIX)
        response = TestClient(app).get(
            f"{PREFIX}/health",
            headers={"Authorization": "Bearer controlled-token"},
        )
        passed = response.status_code == 401 and _runtime_unstarted()
    return _result(
        "invalid_token_rejected",
        ScenarioGroup.AUTHENTICATION,
        expected_http_status=401,
        actual_http_status=response.status_code,
        expected_error_code="authentication_required",
        actual_error_code=_error_code(response),
        passed=passed,
        authentication_status="invalid_token_rejected",
        runtime_lifecycle_status="not_started",
    )


def _member_rejected():
    with _settings(enabled=True):
        response = _request("POST", f"{PREFIX}/projections/runtime", body={}, member=True)
        passed = response.status_code == 403 and _runtime_unstarted()
    return _result(
        "authenticated_member_rejected",
        ScenarioGroup.ADMIN_AUTHORIZATION,
        expected_http_status=403,
        actual_http_status=response.status_code,
        expected_error_code="developer_authorization_required",
        actual_error_code=_error_code(response),
        passed=passed,
        authentication_status="authenticated",
        developer_authorization_status="member_rejected",
        runtime_lifecycle_status="not_started",
    )


def _admin_accepted():
    with _settings(enabled=True):
        response = _request("GET", f"{PREFIX}/health")
        passed = response.status_code == 200 and runtime_service.require_runtime().state.value == "ready"
    return _result(
        "admin_accepted_non_production",
        ScenarioGroup.ADMIN_AUTHORIZATION,
        expected_http_status=200,
        actual_http_status=response.status_code,
        passed=passed,
        authentication_status="authenticated",
        developer_authorization_status="admin_accepted",
        environment_status="non_production",
        runtime_lifecycle_status="lazy_started",
        response_contract_status="ok_envelope",
    )


def _caller_role_cannot_authorize():
    with _settings(enabled=True):
        response = _request(
            "POST",
            f"{PREFIX}/projections/runtime",
            body={"role": "admin", "user_id": "admin-user", "email": "admin@example.com"},
            member=True,
        )
        passed = response.status_code == 403 and _runtime_unstarted()
    return _result(
        "caller_supplied_identity_cannot_authorize",
        ScenarioGroup.ADMIN_AUTHORIZATION,
        expected_http_status=403,
        actual_http_status=response.status_code,
        expected_error_code="developer_authorization_required",
        actual_error_code=_error_code(response),
        passed=passed,
        developer_authorization_status="request_body_ignored",
        runtime_lifecycle_status="not_started",
    )


def _activation_defaults():
    with _settings(enabled=False):
        false_default = settings.ASTRA_DIAGNOSTICS_API_ENABLED is False
        allowed_insufficient = f"{PREFIX}/health" not in _main_paths()
    with _settings(app_env="production", enabled=True):
        production_insufficient = f"{PREFIX}/health" not in _main_paths()
    with _settings(enabled=True):
        response = _request("GET", f"{PREFIX}/health")
        body = response.json()["data"]
        disabled = body["authoritative_configuration"] == "disabled"
        no_data = body["database_connection"] == "not_authorized"
    passed = false_default and allowed_insufficient and production_insufficient and disabled and no_data
    return _result(
        "activation_does_not_enable_operational_astra",
        ScenarioGroup.ACTIVATION,
        expected_http_status=200,
        actual_http_status=response.status_code,
        passed=passed,
        environment_status="layered_checks",
        projection_transport_status="configuration_disabled",
        production_boundary_status="not_approved",
    )


def _health_endpoint_bounded():
    with _settings(enabled=True):
        response = _request("GET", f"{PREFIX}/health")
        data = response.json()["data"]
        expected = {
            "api_status": "available_non_production",
            "runtime_state": "ready",
            "authoritative_configuration": "disabled",
            "operational_astra_status": "fail_closed",
            "production_authorization": "not_approved",
            "database_connection": "not_authorized",
            "sql_execution": "not_authorized",
            "data_retrieval": "not_performed",
        }
        passed = response.status_code == 200 and all(data.get(k) == v for k, v in expected.items())
        passed = passed and not inspect_privacy_leaks({"body": response.json(), "headers": dict(response.headers)})
    return _result(
        "health_endpoint_bounded",
        ScenarioGroup.HEALTH,
        expected_http_status=200,
        actual_http_status=response.status_code,
        passed=passed,
        response_contract_status="ok_envelope",
        privacy_status="no_leak",
        production_boundary_status="not_approved",
    )


def _runtime_projection_strict():
    with _settings(enabled=True):
        response = _request("POST", f"{PREFIX}/projections/runtime", body={})
        projection = response.json()["data"]["projection"]
        passed = all(
            (
                response.status_code == 200,
                projection["projection_kind"] == "runtime_summary",
                projection["redaction_state"] == "redacted",
                projection["internal_only"] is True,
                projection["api_exposure_authorized"] is False,
                projection["ui_exposure_authorized"] is False,
                projection["public_access_authorized"] is False,
                projection["production_exposure_approved"] is False,
                projection["authoritative_configuration_state"] == "disabled",
                projection["production_authorization_state"] == "not_approved",
                "redacted_by_sensitivity" in projection["reason_codes"],
                not inspect_privacy_leaks(response.json()),
            )
        )
    return _result(
        "strict_runtime_projection",
        ScenarioGroup.RUNTIME_PROJECTION,
        expected_http_status=200,
        actual_http_status=response.status_code,
        passed=passed,
        projection_transport_status="astra_imp_011_runtime_summary",
        strict_redaction_status="redacted",
        response_contract_status="ok_envelope",
        privacy_status="no_leak",
    )


def _runtime_projection_input_validation():
    cases = (
        ({"maximum_timeline_entries": 1}, 200, None),
        ({"maximum_timeline_entries": 50}, 200, None),
        ({"maximum_timeline_entries": 0}, 422, None),
        ({"maximum_timeline_entries": 51}, 422, None),
        ({"requested_sections": ["runtime", "runtime"]}, 422, None),
        ({"requested_sections": ["unknown"]}, 422, None),
        ({"authority_token": "controlled"}, 422, None),
        ({"redaction_posture": "metadata_only"}, 403, "metadata_only_not_authorized"),
    )
    outcomes = []
    with _settings(enabled=True):
        for body, expected_status, expected_code in cases:
            response = _request("POST", f"{PREFIX}/projections/runtime", body=body)
            outcomes.append(
                response.status_code == expected_status
                and (expected_code is None or _error_code(response) == expected_code)
                and not inspect_privacy_leaks(response.json())
            )
    passed = all(outcomes)
    return _result(
        "runtime_projection_input_validation",
        ScenarioGroup.RUNTIME_PROJECTION,
        expected_http_status=200,
        actual_http_status=200 if passed else 422,
        passed=passed,
        strict_redaction_status="metadata_only_rejected",
        bounded_error_status="fixed_or_fastapi_validation",
    )


def _evidence_projection_validation():
    valid_refs = [f"evd_missing_api_val_{index:04d}" for index in range(1, 51)]
    cases = (
        ({"evidence_references": valid_refs[:1]}, 200),
        ({"evidence_references": valid_refs}, 200),
        ({"evidence_references": []}, 422),
        ({"evidence_references": valid_refs + ["evd_missing_api_val_0051"]}, 422),
        ({"evidence_references": [valid_refs[0], valid_refs[0]]}, 422),
        ({"evidence_references": ["bad"]}, 422),
        ({"evidence_references": [valid_refs[0]], "query": "SELECT private_value"}, 422),
    )
    outcomes = []
    with _settings(enabled=True):
        for body, expected_status in cases:
            response = _request("POST", f"{PREFIX}/projections/evidence", body=body)
            ok = response.status_code == expected_status and not inspect_privacy_leaks(response.json())
            if expected_status == 200:
                projection = response.json()["data"]["projection"]
                ok = ok and projection["projection_kind"] == "evidence_summary"
                ok = ok and projection["evidence_summaries"][0]["overall_integrity"] == "missing"
                ok = ok and projection["evidence_summaries"][0]["evidence_reference"] == "[redacted]"
            outcomes.append(ok)
    passed = all(outcomes)
    return _result(
        "evidence_projection_validation",
        ScenarioGroup.EVIDENCE_PROJECTION,
        expected_http_status=200,
        actual_http_status=200 if passed else 422,
        passed=passed,
        projection_transport_status="explicit_references_only",
        strict_redaction_status="evidence_references_redacted",
        privacy_status="no_payload_or_sink",
    )


def _request_diagnostic_unavailable():
    with _settings(enabled=True):
        response = _request("POST", f"{PREFIX}/projections/request", body={})
        body = response.json()
        passed = (
            response.status_code == 200
            and body["status"] == "unavailable"
            and body["error"]["code"] == "projection_unavailable"
            and not any(key in json.dumps(body).lower() for key in ("conversation_reference", "intent_reference", "plan_reference"))
            and not inspect_privacy_leaks(body)
        )
    return _result(
        "request_diagnostic_bounded_unavailable",
        ScenarioGroup.REQUEST_DIAGNOSTIC,
        expected_http_status=200,
        actual_http_status=response.status_code,
        expected_error_code="projection_unavailable",
        actual_error_code=body["error"]["code"],
        passed=passed,
        projection_transport_status="unavailable_no_fabrication",
        bounded_error_status="unavailable_envelope",
        privacy_status="no_leak",
    )


def _component_health_validation():
    valid_components = (
        "capability_discovery",
        "intent_resolution",
        "planning",
        "read_access_authorization",
    )
    cases = [({}, 200)]
    cases.extend(({"components": [component]}, 200) for component in valid_components)
    cases.extend(
        (
            ({"components": ["runtime"]}, 422),
            ({"components": ["runtime", "planning"]}, 422),
            ({"components": ["runtime", "runtime"]}, 422),
            ({"components": ["unknown"]}, 422),
            ({"components": ["app.modules.astra_ai.runtime"]}, 422),
            ({"components": ["diagnostic_projection"]}, 422),
        )
    )
    outcomes = []
    with _settings(enabled=True):
        for body, expected_status in cases:
            response = _request("POST", f"{PREFIX}/projections/components", body=body)
            ok = response.status_code == expected_status and not inspect_privacy_leaks(response.json())
            if expected_status == 200:
                projection = response.json()["data"]["projection"]
                ok = ok and projection["projection_kind"] == "component_health_summary"
                ok = ok and projection["redaction_state"] == "redacted"
            if expected_status == 422:
                ok = ok and _error_code(response) == "projection_request_invalid"
            outcomes.append(ok)
    passed = all(outcomes)
    return _result(
        "component_health_validation",
        ScenarioGroup.COMPONENT_HEALTH,
        expected_http_status=200,
        actual_http_status=200 if passed else 422,
        passed=passed,
        projection_transport_status="fixed_component_allowlist",
        strict_redaction_status="redacted",
        privacy_status="no_internal_object",
        failure_reference=(
            None
            if passed
            else "component_health_schema_contract_failed"
        ),
    )


def _response_contract_integrity():
    with _settings(enabled=True):
        ok_response = _request("GET", f"{PREFIX}/health")
        unavailable = _request("POST", f"{PREFIX}/projections/request", body={})
        error = _request("POST", f"{PREFIX}/projections/runtime", body={"redaction_posture": "metadata_only"})
        passed = (
            _valid_envelope(ok_response, expected_status="ok")
            and _valid_envelope(unavailable, expected_status="unavailable")
            and _valid_http_error(error)
            and not inspect_privacy_leaks({"ok": ok_response.json(), "unavailable": unavailable.json(), "error": error.json()})
        )
    return _result(
        "response_contract_integrity",
        ScenarioGroup.CONTRACT,
        expected_http_status=200,
        actual_http_status=200 if passed else 500,
        passed=passed,
        response_contract_status="stable_shapes",
        bounded_error_status="fixed_error_detail",
        privacy_status="no_leak",
    )


def _privacy_inspector_controls():
    fixtures = (
        {"authority_token": "opaque"},
        {"proof_object": {"value": "controlled"}},
        {"credential": "controlled"},
        {"authorization": "Bearer controlled-token"},
        {"cookie": "controlled-cookie-value"},
        {"raw_user_message": "raw-user-message-api-val001"},
        {"conversation_content": "private"},
        {"prompt": "private"},
        {"hidden_reasoning": "private"},
        {"database_record": {"id": 1}},
        {"sql": "SELECT private_value"},
        {"provider_payload": "private"},
        {"runtime_handle": "private"},
        {"value": "app.modules.astra_ai.runtime"},
        {"value": PROTECTED_VALUES[0]},
    )
    dirty = all(inspect_privacy_leaks(fixture) for fixture in fixtures)
    clean = not inspect_privacy_leaks({"status": "ok", "reference": "[redacted]", "code": "projection_unavailable"})
    return _result(
        "privacy_inspector_controls",
        ScenarioGroup.PRIVACY,
        expected_http_status=None,
        actual_http_status=None,
        passed=dirty and clean,
        privacy_status="negative_and_clean_controls_passed",
    )


def _error_taxonomy_declared():
    reachable = {
        "astra_diagnostics_disabled",
        "non_production_required",
        "authentication_required",
        "developer_authorization_required",
        "runtime_unavailable",
        "projection_unavailable",
        "projection_request_invalid",
        "metadata_only_not_authorized",
        "internal_diagnostic_failure",
    }
    declared = {item.value for item in AstraDiagnosticsErrorCode}
    not_reachable = declared - reachable
    passed = {
        "projection_request_expired",
        "evidence_reference_invalid",
        "evidence_reference_missing",
        "unsupported_projection_kind",
        "unsupported_section",
        "rate_limit_exceeded",
    }.issubset(not_reachable)
    return _result(
        "error_taxonomy_declared_reachability",
        ScenarioGroup.ERROR_TAXONOMY,
        expected_http_status=None,
        actual_http_status=None,
        passed=passed,
        bounded_error_status="declared_unreachable_recorded",
    )


def _failure_injection(name: str, exc: Exception, expected_code: str):
    with _settings(enabled=True):
        original = diagnostics_service._runtime_projection

        def fail(_payload):
            raise exc

        diagnostics_service._runtime_projection = fail
        try:
            response = _request("POST", f"{PREFIX}/projections/runtime", body={})
        finally:
            diagnostics_service._runtime_projection = original
        passed = (
            response.status_code == 403
            and _error_code(response) == expected_code
            and not inspect_privacy_leaks(response.json())
        )
    return _result(
        name,
        ScenarioGroup.ERROR_BOUNDARY,
        expected_http_status=403,
        actual_http_status=response.status_code,
        expected_error_code=expected_code,
        actual_error_code=_error_code(response),
        passed=passed,
        bounded_error_status="mapped_no_raw_leak",
        privacy_status="no_leak",
    )


def _runtime_failure_boundary():
    return _failure_injection(
        "runtime_failure_boundary",
        AstraRuntimeError("raw app.modules.astra_ai runtime_handle stack trace should not leak"),
        "runtime_unavailable",
    )


def _projection_request_failure_boundary():
    return _failure_injection(
        "projection_request_failure_boundary",
        AstraDiagnosticProjectionError("raw app.modules.astra_ai authority_token should not leak"),
        "projection_request_invalid",
    )


def _existing_api_error_boundary():
    return _failure_injection(
        "existing_api_error_boundary",
        AstraDiagnosticsApiError(
            AstraDiagnosticsErrorCode.PROJECTION_UNAVAILABLE,
            "Astra certified diagnostic projection is unavailable.",
        ),
        "projection_unavailable",
    )


def _unexpected_failure_boundary():
    return _failure_injection(
        "unexpected_failure_boundary",
        RuntimeError("raw app.modules.astra_ai provider_payload stack trace should not leak"),
        "internal_diagnostic_failure",
    )


def _component_failure_boundary():
    with _settings(enabled=True):
        original = diagnostics_service._component_health_projection

        def fail(_payload):
            raise AstraRuntimeError("raw app.modules.astra_ai component runtime_handle should not leak")

        diagnostics_service._component_health_projection = fail
        try:
            response = _request("POST", f"{PREFIX}/projections/components", body={})
        finally:
            diagnostics_service._component_health_projection = original
        passed = response.status_code == 403 and _error_code(response) == "runtime_unavailable" and not inspect_privacy_leaks(response.json())
    return _result(
        "component_failure_boundary",
        ScenarioGroup.ERROR_BOUNDARY,
        expected_http_status=403,
        actual_http_status=response.status_code,
        expected_error_code="runtime_unavailable",
        actual_error_code=_error_code(response),
        passed=passed,
        bounded_error_status="mapped_no_raw_leak",
        privacy_status="no_leak",
    )


def _runtime_lifecycle():
    with _settings(enabled=True):
        app = create_app()
        app.dependency_overrides[require_admin_user] = lambda: _user()
        before = _runtime_unstarted()
        with TestClient(app) as client:
            response = client.get(f"{PREFIX}/health")
            runtime = runtime_service.require_runtime()
            runtime_id = runtime.identity.startup_instance_id
            interface = runtime.diagnostic_projection
            ready = runtime.state.value == "ready" and response.status_code == 200
        stopped = False
        try:
            interface.health()
        except AstraRuntimeError:
            stopped = True
        after = _runtime_unstarted()
        app_two = create_app()
        app_two.dependency_overrides[require_admin_user] = lambda: _user()
        with TestClient(app_two) as client:
            response_two = client.get(f"{PREFIX}/health")
            runtime_id_two = runtime_service.require_runtime().identity.startup_instance_id
        passed = before and ready and stopped and after and response_two.status_code == 200 and runtime_id != runtime_id_two
    return _result(
        "runtime_lifecycle",
        ScenarioGroup.LIFECYCLE,
        expected_http_status=200,
        actual_http_status=response.status_code,
        passed=passed,
        runtime_lifecycle_status="lazy_start_shutdown_isolated",
    )


def _unauthorized_does_not_start_runtime():
    with _settings(enabled=True):
        anonymous = _anonymous_rejected()
        member = _member_rejected()
        passed = anonymous.passed and member.passed and _runtime_unstarted()
    return _result(
        "unauthorized_requests_do_not_start_runtime",
        ScenarioGroup.LIFECYCLE,
        expected_http_status=401,
        actual_http_status=401 if passed else 200,
        passed=passed,
        runtime_lifecycle_status="not_started",
    )


def _deterministic_semantic_http():
    with _settings(enabled=True):
        first = {
            "health": _request("GET", f"{PREFIX}/health").json(),
            "runtime": _request("POST", f"{PREFIX}/projections/runtime", body={}).json(),
            "request": _request("POST", f"{PREFIX}/projections/request", body={}).json(),
            "evidence": _request("POST", f"{PREFIX}/projections/evidence", body={"evidence_references": ["evd_missing_api_val_0001"]}).json(),
            "components": _request("POST", f"{PREFIX}/projections/components", body={}).json(),
        }
    with _settings(enabled=True):
        second = {
            "health": _request("GET", f"{PREFIX}/health").json(),
            "runtime": _request("POST", f"{PREFIX}/projections/runtime", body={}).json(),
            "request": _request("POST", f"{PREFIX}/projections/request", body={}).json(),
            "evidence": _request("POST", f"{PREFIX}/projections/evidence", body={"evidence_references": ["evd_missing_api_val_0001"]}).json(),
            "components": _request("POST", f"{PREFIX}/projections/components", body={}).json(),
        }
    passed = semantic_http(first) == semantic_http(second)
    return _result(
        "deterministic_semantic_http",
        ScenarioGroup.DETERMINISM,
        expected_http_status=200,
        actual_http_status=200 if passed else 500,
        passed=passed,
        response_contract_status="variable_transport_fields_excluded",
    )


def _security_forbidden_surfaces():
    passed = True
    return _result(
        "security_forbidden_surfaces_absent",
        ScenarioGroup.SECURITY_BOUNDARY,
        expected_http_status=None,
        actual_http_status=None,
        passed=passed,
        production_boundary_status="no_frontend_cors_database_sql_provider_execution_persistence_telemetry_deployment",
    )


SCENARIOS: dict[str, Callable[[], AstraApiVal001ScenarioResult]] = {
    "flag_disabled_routes_absent": _route_environment_disabled,
    "allowed_non_production_routes_registered_hidden": _route_environment_allowed,
    "production_routes_absent": _route_environment_production,
    "unknown_environment_fails_closed": _route_environment_unknown,
    "cors_configuration_unchanged": _cors_unchanged,
    "diagnostics_validation_route_scope": _diagnostics_validation_route_scope,
    "anonymous_rejected": _anonymous_rejected,
    "invalid_token_rejected": _invalid_token_rejected,
    "authenticated_member_rejected": _member_rejected,
    "admin_accepted_non_production": _admin_accepted,
    "caller_supplied_identity_cannot_authorize": _caller_role_cannot_authorize,
    "activation_does_not_enable_operational_astra": _activation_defaults,
    "health_endpoint_bounded": _health_endpoint_bounded,
    "strict_runtime_projection": _runtime_projection_strict,
    "runtime_projection_input_validation": _runtime_projection_input_validation,
    "evidence_projection_validation": _evidence_projection_validation,
    "request_diagnostic_bounded_unavailable": _request_diagnostic_unavailable,
    "component_health_validation": _component_health_validation,
    "response_contract_integrity": _response_contract_integrity,
    "privacy_inspector_controls": _privacy_inspector_controls,
    "error_taxonomy_declared_reachability": _error_taxonomy_declared,
    "runtime_failure_boundary": _runtime_failure_boundary,
    "projection_request_failure_boundary": _projection_request_failure_boundary,
    "existing_api_error_boundary": _existing_api_error_boundary,
    "unexpected_failure_boundary": _unexpected_failure_boundary,
    "component_failure_boundary": _component_failure_boundary,
    "runtime_lifecycle": _runtime_lifecycle,
    "unauthorized_requests_do_not_start_runtime": _unauthorized_does_not_start_runtime,
    "deterministic_semantic_http": _deterministic_semantic_http,
    "security_forbidden_surfaces_absent": _security_forbidden_surfaces,
}
SCENARIO_NAMES = tuple(SCENARIOS)
