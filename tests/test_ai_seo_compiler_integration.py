from __future__ import annotations

import copy

from app.modules.ai_seo_compiler.integration import (
    AI_SEO_CONTROLLED_INTEGRATION_DEFAULT,
    ControlledFailureCode,
    ControlledFailureStage,
    ControlledIntegrationControl,
    ControlledIntegrationStatus,
    ControlledParityStatus,
    run_controlled_integration,
    stable_evidence_json,
)
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.knowledge import builder
from app.modules.knowledge.publisher import build_public_artifacts
from app.modules.knowledge.registry import KnowledgeRegistry


def _registry() -> KnowledgeRegistry:
    return KnowledgeRegistry(copy.deepcopy(builder.build_registry()[0]))


def test_controlled_integration_defaults_to_disabled_execution():
    result = run_controlled_integration(registry=_registry())
    evidence = result.evidence.as_dict()
    assert AI_SEO_CONTROLLED_INTEGRATION_DEFAULT.enabled is False
    assert result.compiler_output is None
    assert result.comparison_report is None
    assert evidence["compilerExecutionSummary"]["status"] == ControlledIntegrationStatus.DISABLED.value
    assert evidence["compilerExecutionSummary"]["attempted"] is False
    assert evidence["parityStatus"] == ControlledParityStatus.NOT_RUN.value
    assert result.artifacts.knowledge["platform"]["appCount"] == 100


def test_controlled_integration_can_run_internal_shadow_execution_when_enabled():
    result = run_controlled_integration(registry=_registry(), control=ControlledIntegrationControl(enabled=True))
    evidence = result.evidence.as_dict()
    assert result.compiler_output is not None
    assert result.comparison_report is not None
    assert result.comparison_report.passed
    assert evidence["compilerExecutionSummary"]["status"] == ControlledIntegrationStatus.COMPLETED.value
    assert evidence["compilerExecutionSummary"]["attempted"] is True
    assert evidence["compilerExecutionSummary"]["succeeded"] is True
    assert evidence["parityStatus"] == ControlledParityStatus.PASSED.value
    assert evidence["comparisonSummary"]["matchingEntities"] == 100
    assert evidence["validationSummary"]["blocker"] == 0


def test_controlled_integration_preserves_publisher_artifacts_when_compiler_fails():
    expected = build_public_artifacts(_registry())

    def failing_compiler(_artifacts):
        raise RuntimeError("compiler candidate failed")

    result = run_controlled_integration(
        registry=_registry(),
        control=ControlledIntegrationControl(enabled=True),
        compiler_executor=failing_compiler,
    )
    evidence = result.evidence.as_dict()
    assert result.artifacts == expected
    assert result.compiler_output is None
    assert result.comparison_report is None
    assert evidence["compilerExecutionSummary"]["status"] == ControlledIntegrationStatus.FAILED.value
    assert evidence["compilerExecutionSummary"]["failureCode"] == ControlledFailureCode.COMPILER_EXECUTION_FAILED.value
    assert evidence["compilerExecutionSummary"]["failureStage"] == ControlledFailureStage.CANDIDATE_COMPILATION.value
    assert "failureMessage" not in evidence["compilerExecutionSummary"]
    assert "compiler candidate failed" not in stable_json(evidence)
    assert evidence["parityStatus"] == ControlledParityStatus.FAILED.value
    assert evidence["validationSummary"]["blocker"] == 1


def test_controlled_integration_evidence_is_deterministic_for_identical_inputs():
    control = ControlledIntegrationControl(enabled=True, execution_duration_ms=0)
    first = run_controlled_integration(registry=_registry(), control=control)
    second = run_controlled_integration(registry=_registry(), control=control)
    assert stable_evidence_json(first.evidence) == stable_evidence_json(second.evidence)
    assert first.comparison_report is not None
    assert second.comparison_report is not None
    assert first.comparison_report.as_dict() == second.comparison_report.as_dict()


def test_controlled_integration_does_not_replace_public_artifacts():
    current = build_public_artifacts(_registry())
    result = run_controlled_integration(registry=_registry(), control=ControlledIntegrationControl(enabled=True))
    assert result.artifacts == current
    assert stable_digest(result.artifacts.knowledge) == stable_digest(current.knowledge)
    assert stable_digest(result.artifacts.metadata) == stable_digest(current.metadata)
    assert stable_digest(result.artifacts.jsonld) == stable_digest(current.jsonld)


def test_controlled_integration_sanitizes_sensitive_exception_text_from_evidence():
    sensitive_message = "DATABASE_URL=postgres://secret@host/private /Users/name/project/file.py"

    def failing_compiler(_artifacts):
        raise RuntimeError(sensitive_message)

    result = run_controlled_integration(
        registry=_registry(),
        control=ControlledIntegrationControl(enabled=True),
        compiler_executor=failing_compiler,
    )
    evidence_json = stable_json(result.evidence.as_dict())
    assert "DATABASE_URL" not in evidence_json
    assert "postgres://secret@host/private" not in evidence_json
    assert "/Users/name/project/file.py" not in evidence_json
    assert sensitive_message not in evidence_json
    assert "compiler_execution_failed" in evidence_json
    assert "candidate_compilation" in evidence_json


def test_controlled_integration_failure_evidence_is_deterministic_for_different_messages():
    def first_failing_compiler(_artifacts):
        raise RuntimeError("first uncontrolled error message")

    def second_failing_compiler(_artifacts):
        raise RuntimeError("second uncontrolled error message")

    control = ControlledIntegrationControl(enabled=True)
    first = run_controlled_integration(registry=_registry(), control=control, compiler_executor=first_failing_compiler)
    second = run_controlled_integration(registry=_registry(), control=control, compiler_executor=second_failing_compiler)
    assert stable_evidence_json(first.evidence) == stable_evidence_json(second.evidence)
    assert first.artifacts == second.artifacts
