from __future__ import annotations

import inspect
import json
from pathlib import Path

from validation.astra_val_002 import runner
from validation.astra_val_002.cli import main


def test_scenario_catalog_is_unique_fixed_and_deterministic():
    assert len(runner.SCENARIO_NAMES) == len(set(runner.SCENARIO_NAMES)) == 10
    assert tuple(item.scenario_name for item in runner.run_all()) == runner.SCENARIO_NAMES
    assert tuple(item.scenario_group.value for item in runner.run_all()) == (
        "determinism",
        "authority",
        "correlation",
        "evidence",
        "privacy",
        "completeness",
        "timeline",
        "atomicity",
        "lifecycle",
        "exposure",
    )


def test_all_scenarios_pass_fixed_certified_expectations():
    results = runner.run_all()
    assert results
    assert all(item.passed for item in results)
    assert all(item.expected_outcome == item.actual_outcome for item in results)
    assert all(item.completed_at == runner.NOW for item in results)
    assert all(item.validation_version == runner.VALIDATION_VERSION for item in results)


def test_deterministic_semantic_contract_is_narrow_and_meaningful():
    result = runner.run_scenario("deterministic_projection")
    assert result.deterministic_comparison_status == "exact_semantic_match"
    source = inspect.getsource(runner.semantic_projection)
    required = (
        "projection_kind",
        "completeness",
        "redaction_state",
        "component_states",
        "proof_state",
        "reason_codes",
        "digest_status",
        "timeline",
        "truncated",
        "exposure",
    )
    assert all(field in source for field in required)
    excluded_only = inspect.getdoc(runner.semantic_projection)
    assert "request/evidence identity and issuance time" in excluded_only


def test_authority_correlation_and_lifecycle_scenarios_enforce_certified_paths():
    authority = runner.run_scenario("authority_tamper_resistance")
    correlation = runner.run_scenario("correlation_integrity")
    lifecycle = runner.run_scenario("lifecycle_health")
    assert authority.actual_outcome == "all_rejected"
    assert authority.lifecycle_status == "exact_runtime_authority"
    assert correlation.correlation_status == "intent_plan_missing"
    assert correlation.timeline_status == "no_synthetic_gap"
    assert lifecycle.actual_outcome == "shutdown_invalidated"
    assert lifecycle.lifecycle_status == "stopped"


def test_evidence_integrity_never_overstates_digest_verification():
    result = runner.run_scenario("evidence_integrity")
    assert result.evidence_integrity_status == "resolved_structural"
    assert result.digest_status == "not_reproducible"
    assert "verified" not in result.stable_json()


def test_strict_redaction_recursively_removes_actual_protected_values():
    result = runner.run_scenario("strict_redaction_no_leak")
    assert result.completeness == "redacted"
    assert result.redaction_state == "redacted"
    payload = result.stable_json().lower()
    assert not any(value.lower() in payload for value in runner.PROTECTED_VALUES)
    assert not any(term in payload for term in runner.FORBIDDEN_LEAK_TERMS)


def test_completeness_timeline_and_atomicity_match_certified_precedence():
    completeness = runner.run_scenario("completeness_precedence")
    timeline = runner.run_scenario("timeline_bounds")
    atomicity = runner.run_scenario("evidence_atomicity")
    assert completeness.completeness == "complete_partial_unavailable_redacted"
    assert timeline.timeline_status == "truncated_at_50"
    assert timeline.completeness == "partial"
    assert atomicity.actual_outcome == "append_failure_atomic"
    assert atomicity.failure_reference == "projection_evidence_capacity"


def test_every_result_contract_is_bounded_and_contains_no_private_material():
    forbidden = (
        "authority_token",
        "credential",
        "password",
        "raw user",
        "prompt",
        "hidden reasoning",
        "database result",
        "runtime handle",
    )
    for result in runner.run_all():
        payload = result.stable_json().lower()
        assert len(payload) < 5000
        assert not any(term in payload for term in forbidden)
        assert result.exposure_boundary_status == "internal_only"


def test_cli_list_scenario_text_json_and_all_are_same_runner(capsys):
    assert main(["--list"]) == 0
    assert capsys.readouterr().out.splitlines() == list(runner.SCENARIO_NAMES)
    assert main(["--scenario", "strict_redaction_no_leak"]) == 0
    assert "strict_no_leak" in capsys.readouterr().out
    assert main(["--scenario", "deterministic_projection", "--format", "json"]) == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed == runner.run_scenario("deterministic_projection").model_dump(mode="json")
    assert main(["--all", "--format", "text"]) == 0
    assert capsys.readouterr().out.count("Scenario") == len(runner.SCENARIO_NAMES)
    assert main(["--all", "--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == len(runner.SCENARIO_NAMES)


def test_cli_exit_codes_and_json_are_stable(capsys):
    assert main(["--scenario", "unknown_scenario"]) == 2
    assert "unknown scenario" in capsys.readouterr().err.lower()
    assert main([]) == 2
    capsys.readouterr()
    first = runner.run_scenario("evidence_integrity").stable_json()
    second = runner.run_scenario("evidence_integrity").stable_json()
    assert first == second


def test_harness_has_no_monkeypatch_private_mutation_or_fixture_authority():
    source = inspect.getsource(runner)
    prohibited = (
        "monkeypatch",
        "unittest.mock",
        "evaluate_governance =",
        "_records[",
        "_requests[",
        "_certified_outputs",
        "_read_authority_issuers",
        "_issue_read_authority_issuer",
        "_register_runtime_output",
        "registration_authority",
    )
    assert not any(term in source for term in prohibited)


def test_harness_has_no_external_or_product_surface():
    source = inspect.getsource(runner).lower()
    prohibited = (
        "fastapi",
        "apirouter",
        "sqlalchemy",
        "create_engine",
        "database_url",
        "openai",
        "anthropic",
        "tool executor",
        "write_text",
        "write_bytes",
    )
    assert not any(term in source for term in prohibited)


def test_no_generated_reports_are_present():
    root = Path(__file__).parents[1]
    validation_root = root / "validation" / "astra_val_002"
    generated = tuple(
        path
        for path in validation_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".txt", ".report"}
    )
    assert generated == ()
