from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

from validation.astra_api_val_001 import runner
from validation.astra_api_val_001.cli import main


def test_scenario_catalog_is_unique_fixed_and_covers_required_groups():
    assert len(runner.SCENARIO_NAMES) == len(set(runner.SCENARIO_NAMES)) == 30
    assert tuple(item.scenario_name for item in runner.run_all()) == runner.SCENARIO_NAMES
    assert {item.scenario_group.value for item in runner.run_all()} == {
        "route_environment",
        "authentication",
        "admin_authorization",
        "activation",
        "health",
        "runtime_projection",
        "evidence_projection",
        "request_diagnostic",
        "component_health",
        "privacy",
        "contract",
        "error_taxonomy",
        "error_boundary",
        "lifecycle",
        "determinism",
        "security_boundary",
    }


def test_all_scenarios_pass_fixed_expectations():
    results = runner.run_all()
    assert results
    assert all(item.passed for item in results)
    assert all(item.completed_at == runner.NOW for item in results)
    assert all(item.validation_version == runner.VALIDATION_VERSION for item in results)
    assert all(
        item.expected_http_status == item.actual_http_status
        or item.scenario_name in {
            "runtime_projection_input_validation",
            "evidence_projection_validation",
            "component_health_validation",
            "response_contract_integrity",
            "deterministic_semantic_http",
        "security_forbidden_surfaces_absent",
        "diagnostics_validation_route_scope",
    }
        for item in results
    )


def test_route_auth_admin_environment_endpoint_and_lifecycle_results():
    expected = {
        "flag_disabled_routes_absent": ("route_environment", "absent"),
        "allowed_non_production_routes_registered_hidden": (
            "route_environment",
            "registered_openapi_hidden",
        ),
        "production_routes_absent": ("route_environment", "absent"),
        "anonymous_rejected": ("authentication", "anonymous_rejected"),
        "invalid_token_rejected": ("authentication", "invalid_token_rejected"),
        "authenticated_member_rejected": ("admin_authorization", "member_rejected"),
        "admin_accepted_non_production": ("admin_authorization", "admin_accepted"),
        "runtime_lifecycle": ("lifecycle", "lazy_start_shutdown_isolated"),
    }
    for name, (group, status_value) in expected.items():
        result = runner.run_scenario(name)
        assert result.scenario_group.value == group
        assert result.passed
        assert status_value in result.model_dump(mode="json").values()


def test_projection_privacy_and_error_scenarios():
    runtime_projection = runner.run_scenario("strict_runtime_projection")
    evidence = runner.run_scenario("evidence_projection_validation")
    request = runner.run_scenario("request_diagnostic_bounded_unavailable")
    component = runner.run_scenario("component_health_validation")
    taxonomy = runner.run_scenario("error_taxonomy_declared_reachability")
    unexpected = runner.run_scenario("unexpected_failure_boundary")

    assert runtime_projection.strict_redaction_status == "redacted"
    assert evidence.projection_transport_status == "explicit_references_only"
    assert request.actual_error_code == "projection_unavailable"
    assert component.projection_transport_status == "fixed_component_allowlist"
    assert taxonomy.bounded_error_status == "declared_unreachable_recorded"
    assert unexpected.actual_error_code == "internal_diagnostic_failure"


def test_recursive_privacy_inspector_detects_controlled_leaks_and_clean_control():
    controlled = (
        {"authority_token": "opaque"},
        {"issuer_authority": "opaque"},
        {"proof_object": {"kind": "controlled"}},
        {"password": "controlled"},
        {"credential": "controlled"},
        {"secret": "secret-api-val001"},
        {"authorization": "Bearer controlled-token"},
        {"cookie": "controlled-cookie-value"},
        {"raw_user_message": "raw-user-message-api-val001"},
        {"conversation_content": "private"},
        {"prompt": "private"},
        {"hidden_reasoning": "private"},
        {"database_record": {"id": 1}},
        {"sql": "SELECT controlled_private_value"},
        {"provider_payload": "private"},
        {"runtime_handle": "private"},
        {"nested": {"module": "app.modules.astra_ai.runtime"}},
        {"conversation_reference": "conv_api_val001_protected_0001"},
        {"evidence_reference": "evd_api_val001_protected_0001"},
        {"intent_reference": "intent_api_val001_protected_0001"},
        {"plan_reference": "plan_api_val001_protected_0001"},
    )
    assert all(runner.inspect_privacy_leaks(value) for value in controlled)
    assert runner.inspect_privacy_leaks(
        {"status": "ok", "reference": "[redacted]", "code": "projection_unavailable"}
    ) == ()


def test_result_contracts_are_bounded_and_private_data_free():
    forbidden = (
        "authority_token",
        "credential",
        "password",
        "raw-user-message-api-val001",
        "prompt",
        "hidden_reasoning",
        "database_record",
        "provider_payload",
        "runtime_handle",
        "app.modules.astra_ai",
    )
    for result in runner.run_all():
        payload = result.stable_json().lower()
        assert len(payload) < 5000
        assert not any(term in payload for term in forbidden)


def test_deterministic_semantic_comparison_contract_is_explicit():
    source = inspect.getsource(runner.semantic_http)
    assert "VARIABLE_FIELDS" in source
    for field in (
        "request_id",
        "observed_at",
        "projection_id",
        "projection_request_id",
        "evidence_references",
    ):
        assert field in runner.VARIABLE_FIELDS
    result = runner.run_scenario("deterministic_semantic_http")
    assert result.passed
    assert result.response_contract_status == "variable_transport_fields_excluded"


def test_cli_list_text_json_all_and_exit_codes_are_stable(capsys):
    assert main(["--list"]) == 0
    assert capsys.readouterr().out.splitlines() == list(runner.SCENARIO_NAMES)

    assert main(["--scenario", "anonymous_rejected"]) == 0
    text = capsys.readouterr().out
    assert "anonymous_rejected" in text
    assert "Authentication" in text

    assert main(["--scenario", "strict_runtime_projection", "--format", "json"]) == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed == runner.run_scenario("strict_runtime_projection").model_dump(mode="json")

    assert main(["--all", "--format", "text"]) == 0
    assert capsys.readouterr().out.count("Scenario") == len(runner.SCENARIO_NAMES)

    assert main(["--all", "--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == len(runner.SCENARIO_NAMES)

    assert main(["--scenario", "unknown_scenario"]) == 2
    assert "unknown scenario" in capsys.readouterr().err.lower()
    assert main([]) == 2


def test_runner_and_cli_outputs_are_semantically_equivalent(capsys):
    name = "request_diagnostic_bounded_unavailable"
    expected = runner.run_scenario(name).model_dump(mode="json")

    assert main(["--scenario", name, "--format", "json"]) == 0
    actual = json.loads(capsys.readouterr().out)

    assert actual == expected


def test_no_generated_reports_are_present():
    root = Path(__file__).parents[1]
    generated = tuple(
        path
        for path in (root / "validation" / "astra_api_val_001").rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".txt", ".report"}
    )
    assert generated == ()


def test_validation_harness_does_not_modify_certified_parent_sources():
    root = Path(__file__).parents[1]
    paths = (
        "app/modules/astra_ai/api",
        "app/main.py",
        "app/core/config.py",
        "app/modules/auth",
        "app/modules/astra_ai/runtime.py",
        "app/modules/astra_ai/diagnostic_projection.py",
        "validation/astra_val_001",
        "validation/astra_val_002",
    )
    diff = subprocess.run(
        ["git", "diff", "--", *paths],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert diff.stdout == ""


def test_validation_harness_has_no_disallowed_runtime_mutation_or_api_surface():
    source = inspect.getsource(runner)
    prohibited = (
        "._registry",
        "._requests[",
        "._certified_outputs",
        "._records",
        "._evidence_sink",
        "_register_runtime_output",
        "registration_authority",
        "create_engine",
        "sqlalchemy",
        "write_text",
        "write_bytes",
    )
    assert not any(term in source for term in prohibited)
