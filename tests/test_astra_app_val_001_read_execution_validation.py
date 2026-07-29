from __future__ import annotations

import json
import subprocess
import sys

from validation.astra_app_val_001.runner import run_all, run_scenario, scenario_names


def test_all_astra_app_val_001_scenarios_pass():
    results = run_all()
    assert len(results) == 8
    assert all(result.passed for result in results)
    assert "database_session_boundary_proof" in scenario_names()


def test_database_session_boundary_scenario_records_adapter_only_use():
    result = run_scenario("database_session_boundary_proof")
    assert result.passed
    assert result.session_boundary_status == "opaque_until_registered_adapter"
    assert result.app_read_status == "adapter_only_session_use"


def test_fail_closed_scenario_covers_invalid_execution_surfaces():
    result = run_scenario("unauthorized_and_malformed_fail_closed")
    assert result.passed
    assert result.fail_closed_status == "copied_reused_context_write_subject_rejected"


def test_validation_output_is_stable_json_and_text_cli_matches_runner():
    result = run_scenario("response_is_validated_and_redacted")
    payload = json.loads(result.stable_json())
    assert payload["passed"] is True
    assert payload["privacy_status"] == "no_forbidden_material"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "validation.astra_app_val_001.cli",
            "--scenario",
            "response_is_validated_and_redacted",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Scenario" in completed.stdout
    assert "response_is_validated_and_redacted" in completed.stdout
    assert "no_forbidden_material" in completed.stdout


def test_validation_json_cli_runs_all_scenarios():
    completed = subprocess.run(
        [sys.executable, "-m", "validation.astra_app_val_001.cli", "--all", "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert len(payload) == len(scenario_names())
    assert all(item["passed"] for item in payload)
