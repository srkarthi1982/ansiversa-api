from __future__ import annotations

import copy

from app.modules.ai_seo_compiler.integration import compile_from_knowledge_artifacts
from app.modules.ai_seo_compiler.operational import (
    OperationalStatus,
    stable_operational_json,
    validate_operational_behavior,
)
from app.modules.ai_seo_compiler.pipeline import CompilerOutput
from app.modules.ai_seo_compiler.serialization import stable_digest
from app.modules.knowledge import builder
from app.modules.knowledge.publisher import PublicArtifacts, build_public_artifacts
from app.modules.knowledge.registry import KnowledgeRegistry


def _registry() -> KnowledgeRegistry:
    return KnowledgeRegistry(copy.deepcopy(builder.build_registry()[0]))


def _artifacts_digest(artifacts: PublicArtifacts) -> str:
    return stable_digest(
        {
            "knowledge": artifacts.knowledge,
            "jsonld": artifacts.jsonld,
            "metadata": artifacts.metadata,
            "sitemap": artifacts.sitemap,
            "llms": artifacts.llms,
            "llmsFull": artifacts.llms_full,
            "robots": artifacts.robots,
        }
    )


def test_operational_validation_passes_for_repeated_execution():
    report = validate_operational_behavior(registry=_registry(), cycles=2)
    payload = report.as_dict()

    assert report.passed
    assert payload["operationalStatus"] == OperationalStatus.STABLE.value
    assert payload["executionCount"] == 2
    assert payload["findings"] == []
    assert payload["paritySummary"]["allParityPassed"] is True
    assert payload["operationalStability"]["allReadinessPassed"] is True
    assert payload["deterministicEvidenceSummary"]["minimumRepeatedExecutions"] is True
    assert payload["deterministicEvidenceSummary"]["readinessEvidenceDigestsStable"] is True
    assert payload["failureRecoverySummary"]["allRollbackFailuresRecorded"] is True
    assert payload["failureRecoverySummary"]["allRollbackPreserveCurrentArtifacts"] is True
    assert payload["failureRecoverySummary"]["noCompilerArtifactsPublishedDuringRollback"] is True


def test_operational_validation_is_deterministic_for_identical_inputs():
    first = validate_operational_behavior(registry=_registry(), cycles=2)
    second = validate_operational_behavior(registry=_registry(), cycles=2)

    assert stable_operational_json(first) == stable_operational_json(second)
    assert first.as_dict()["evidenceDigest"] == second.as_dict()["evidenceDigest"]


def test_operational_validation_requires_repeated_cycles():
    report = validate_operational_behavior(registry=_registry(), cycles=1)
    payload = report.as_dict()

    assert not report.passed
    assert payload["operationalStatus"] == OperationalStatus.UNSTABLE.value
    assert any(item["code"] == "execution_count_too_low" for item in payload["findings"])


def test_operational_validation_blocks_repeated_compiler_failure_without_leaking_message():
    def failing_compiler(_artifacts: PublicArtifacts) -> CompilerOutput:
        raise RuntimeError("DATABASE_URL=postgres://secret@host/private /Users/name/project/file.py")

    report = validate_operational_behavior(registry=_registry(), cycles=2, compiler_executor=failing_compiler)
    serialized = stable_operational_json(report)
    payload = report.as_dict()

    assert not report.passed
    assert payload["operationalStatus"] == OperationalStatus.UNSTABLE.value
    assert any(item["code"] == "readiness_cycle_blocked" for item in payload["findings"])
    assert any(item["code"] == "parity_cycle_failed" for item in payload["findings"])
    assert "DATABASE_URL" not in serialized
    assert "postgres://secret@host/private" not in serialized
    assert "/Users/name/project/file.py" not in serialized


def test_operational_failure_evidence_is_deterministic_across_exception_messages():
    def first_failure(_artifacts: PublicArtifacts) -> CompilerOutput:
        raise RuntimeError("first private failure detail")

    def second_failure(_artifacts: PublicArtifacts) -> CompilerOutput:
        raise RuntimeError("second private failure detail")

    first = validate_operational_behavior(registry=_registry(), cycles=2, compiler_executor=first_failure)
    second = validate_operational_behavior(registry=_registry(), cycles=2, compiler_executor=second_failure)

    assert stable_operational_json(first) == stable_operational_json(second)


def test_operational_validation_repeats_rollback_behavior():
    report = validate_operational_behavior(registry=_registry(), cycles=2)
    payload = report.as_dict()
    failure_summary = payload["failureRecoverySummary"]
    current_digests = {cycle["rollbackCurrentArtifactDigest"] for cycle in payload["cycles"]}
    failure_digests = {cycle["rollbackFailureArtifactDigest"] for cycle in payload["cycles"]}

    assert failure_summary["allRollbackFailuresRecorded"] is True
    assert failure_summary["allRollbackPreserveCurrentArtifacts"] is True
    assert failure_summary["rollbackCurrentArtifactDigestStable"] is True
    assert failure_summary["rollbackFailureArtifactDigestStable"] is True
    assert current_digests == failure_digests


def test_operational_validation_blocks_unsafe_rollback_probe():
    def successful_rollback_executor(artifacts: PublicArtifacts) -> CompilerOutput:
        return compile_from_knowledge_artifacts(artifacts)

    report = validate_operational_behavior(
        registry=_registry(),
        cycles=2,
        rollback_executor=successful_rollback_executor,
    )
    payload = report.as_dict()
    codes = {item["code"] for item in payload["findings"]}

    assert not report.passed
    assert payload["failureRecoverySummary"]["allRollbackFailuresRecorded"] is False
    assert payload["failureRecoverySummary"]["noCompilerArtifactsPublishedDuringRollback"] is False
    assert "readiness_cycle_blocked" in codes
    assert "rollback_failure_not_recorded" in codes
    assert "rollback_compiler_artifacts_exposed" in codes


def test_operational_validation_does_not_change_public_knowledge_artifacts():
    before = build_public_artifacts(_registry())
    before_digest = _artifacts_digest(before)

    report = validate_operational_behavior(registry=_registry(), cycles=2)

    after = build_public_artifacts(_registry())
    assert report.passed
    assert _artifacts_digest(after) == before_digest
