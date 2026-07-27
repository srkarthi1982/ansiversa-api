from __future__ import annotations

import inspect
import json

from validation.astra_val_001 import runner
from validation.astra_val_001.cli import main


def test_scenario_names_are_unique_and_deterministic():
    assert len(runner.SCENARIO_NAMES) == len(set(runner.SCENARIO_NAMES))
    assert tuple(result.scenario_name for result in runner.run_all()) == runner.SCENARIO_NAMES


def test_all_scenarios_pass_certified_fail_closed_expectations():
    results = runner.run_all()
    assert results
    assert all(item.passed for item in results)
    assert all(item.scenario_group.value == "certified_default" for item in results)
    assert all(item.successful_path_available is False for item in results)
    assert all(item.unavailability_reason == runner.UNAVAILABILITY_REASON for item in results)


def test_real_pipeline_reaches_invalid_intent_and_non_actionable_plan():
    result = runner.run_scenario("certified_default_fail_closed")
    assert result.intent_status == "invalid"
    assert result.plan_status == "governance_blocked"
    assert result.read_authorization_status == "not_reached"
    assert result.evidence_integrity_status.value == "passed"


def test_read_authorization_and_health_remain_unavailable():
    read = runner.run_scenario("read_request_without_proofs")
    health = runner.run_scenario("health_degraded")
    assert read.actual_outcome == "request_contract_rejected"
    assert read.read_authorization_status == "not_reached"
    assert read.failure_reference == "proofs_required_by_contract"
    assert health.actual_outcome == "degraded"


def test_tamper_freshness_and_foreign_runtime_scenarios_reject():
    for name in ("forged_intent_binding", "stale_turn", "foreign_runtime"):
        result = runner.run_scenario(name)
        assert result.actual_outcome == "rejected"
        assert result.passed


def test_evidence_failure_and_shutdown_release_no_success():
    evidence = runner.run_scenario("current_turn_evidence_atomicity")
    shutdown = runner.run_scenario("shutdown_invalidation")
    assert evidence.actual_outcome == "failed_operation_atomic"
    assert evidence.conversation_state == "active"
    assert evidence.failure_reference == "current_turn_evidence_append_capacity"
    assert shutdown.actual_outcome == "invalidated"
    assert shutdown.runtime_state == "stopped"


def test_every_result_preserves_operational_boundaries():
    for result in runner.run_all():
        assert result.database_connection_state == "not_authorized"
        assert result.sql_execution_state == "not_authorized"
        assert result.data_retrieval_state == "not_performed"
        assert result.data_mutation_state == "prohibited"
        assert result.schema_mutation_state == "prohibited"
        assert result.production_read_state == "not_approved"
        assert result.production_state == "unchanged"


def test_reports_are_bounded_and_contain_no_private_payload():
    forbidden = ("credential", "secret", "password", "raw_conversation", "query_result", "prompt")
    for result in runner.run_all():
        payload = result.stable_json().lower()
        assert not any(term in payload for term in forbidden)
        assert "validation_fixture" not in payload


def test_json_is_stable_and_semantically_matches_text_result():
    first = runner.run_scenario("certified_default_fail_closed")
    second = runner.run_scenario("certified_default_fail_closed")
    assert first.stable_json() == second.stable_json()
    parsed = json.loads(first.stable_json())
    assert parsed["scenario_name"] in first.text()
    assert parsed["actual_outcome"] == first.actual_outcome


def test_cli_list_text_json_and_all_exit_codes(capsys):
    assert main(["--list"]) == 0
    assert "certified_default_fail_closed" in capsys.readouterr().out
    assert main(["--scenario", "certified_default_fail_closed"]) == 0
    assert "unavailable by certified design" in capsys.readouterr().out
    assert main(["--scenario", "certified_default_fail_closed", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["successful_path_available"] is False
    assert main(["--all", "--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == len(runner.SCENARIO_NAMES)


def test_harness_contains_no_governance_monkeypatch_or_private_registry_mutation():
    source = inspect.getsource(runner)
    assert "evaluate_governance =" not in source
    assert "_registrations[" not in source
    assert "_read_authority_issuers" not in source
    assert "_registry." not in source
    assert "_issue_read_authority_issuer" not in source


def test_harness_has_no_product_or_external_surface():
    source = inspect.getsource(runner).lower()
    forbidden_imports = (
        "fastapi",
        "sqlalchemy",
        "openai",
        "apirouter",
        "create_engine",
        "database_url",
        "tool executor",
    )
    assert not any(term in source for term in forbidden_imports)
