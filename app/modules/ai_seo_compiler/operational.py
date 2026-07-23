"""Operational validation for repeated internal AI SEO compiler execution.

Phase 6 validates repeated operational behavior only. It does not publish
compiler artifacts, expose APIs, change startup behavior, or replace the
current Knowledge publisher.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from app.modules.ai_seo_compiler.integration import compile_from_knowledge_artifacts
from app.modules.ai_seo_compiler.pipeline import CompilerOutput
from app.modules.ai_seo_compiler.readiness import (
    ReadinessReport,
    ReadinessStatus,
    stable_readiness_json,
    validate_production_readiness,
)
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.knowledge.publisher import PublicArtifacts
from app.modules.knowledge.registry import KnowledgeRegistry


class OperationalStatus(StrEnum):
    STABLE = "stable"
    UNSTABLE = "unstable"


@dataclass(frozen=True)
class OperationalFinding:
    code: str
    message: str
    subject: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "subject": self.subject}


@dataclass(frozen=True)
class OperationalCycleEvidence:
    cycle: int
    release_candidate_identifier: str
    readiness_status: ReadinessStatus
    readiness_evidence_digest: str
    parity_status: str
    parity_matching_entities: int
    blocked_item_count: int
    rollback_current_artifact_digest: str
    rollback_failure_artifact_digest: str
    rollback_failure_recorded: bool
    rollback_preserved_current_artifacts: bool
    rollback_exposed_compiler_artifacts: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "cycle": self.cycle,
            "releaseCandidateIdentifier": self.release_candidate_identifier,
            "readinessStatus": self.readiness_status.value,
            "readinessEvidenceDigest": self.readiness_evidence_digest,
            "parityStatus": self.parity_status,
            "parityMatchingEntities": self.parity_matching_entities,
            "blockedItemCount": self.blocked_item_count,
            "rollbackCurrentArtifactDigest": self.rollback_current_artifact_digest,
            "rollbackFailureArtifactDigest": self.rollback_failure_artifact_digest,
            "rollbackFailureRecorded": self.rollback_failure_recorded,
            "rollbackPreservedCurrentArtifacts": self.rollback_preserved_current_artifacts,
            "rollbackExposedCompilerArtifacts": self.rollback_exposed_compiler_artifacts,
        }


@dataclass(frozen=True)
class OperationalReport:
    execution_count: int
    operational_status: OperationalStatus
    parity_summary: dict[str, object]
    operational_stability: dict[str, object]
    deterministic_evidence_summary: dict[str, object]
    failure_recovery_summary: dict[str, object]
    readiness_recommendation: str
    cycles: tuple[OperationalCycleEvidence, ...]
    findings: tuple[OperationalFinding, ...]

    @property
    def passed(self) -> bool:
        return self.operational_status is OperationalStatus.STABLE

    def _payload(self) -> dict[str, object]:
        return {
            "executionCount": self.execution_count,
            "operationalStatus": self.operational_status.value,
            "paritySummary": self.parity_summary,
            "operationalStability": self.operational_stability,
            "deterministicEvidenceSummary": self.deterministic_evidence_summary,
            "failureRecoverySummary": self.failure_recovery_summary,
            "readinessRecommendation": self.readiness_recommendation,
            "cycles": [cycle.as_dict() for cycle in self.cycles],
            "findings": [finding.as_dict() for finding in self.findings],
        }

    def as_dict(self) -> dict[str, object]:
        payload = self._payload()
        return {**payload, "evidenceDigest": stable_digest(payload)}


def stable_operational_json(report: OperationalReport) -> str:
    return stable_json(report.as_dict())


def _finding(code: str, message: str, subject: str) -> OperationalFinding:
    return OperationalFinding(code=code, message=message, subject=subject)


def _readiness_report(
    *,
    registry: KnowledgeRegistry | None,
    compiler_executor: Callable[[PublicArtifacts], CompilerOutput],
    rollback_executor: Callable[[PublicArtifacts], CompilerOutput] | None,
) -> ReadinessReport:
    if rollback_executor is None:
        return validate_production_readiness(registry=registry, compiler_executor=compiler_executor)
    return validate_production_readiness(
        registry=registry,
        compiler_executor=compiler_executor,
        rollback_executor=rollback_executor,
    )


def _cycle_evidence(cycle: int, report: ReadinessReport) -> OperationalCycleEvidence:
    payload = report.as_dict()
    parity_summary = payload["paritySummary"]
    comparison = parity_summary["comparison"] if isinstance(parity_summary, dict) else {}
    rollback = payload["rollbackSummary"]
    return OperationalCycleEvidence(
        cycle=cycle,
        release_candidate_identifier=str(payload["releaseCandidateIdentifier"]),
        readiness_status=report.readiness_status,
        readiness_evidence_digest=str(payload["evidenceDigest"]),
        parity_status=str(parity_summary.get("status", "failed")) if isinstance(parity_summary, dict) else "failed",
        parity_matching_entities=int(comparison.get("matchingEntities", 0)) if isinstance(comparison, dict) else 0,
        blocked_item_count=len(payload["blockedItems"]),
        rollback_current_artifact_digest=str(rollback["currentArtifactDigest"]),
        rollback_failure_artifact_digest=str(rollback["failureArtifactDigest"]),
        rollback_failure_recorded=bool(rollback["compilerFailureRecorded"]),
        rollback_preserved_current_artifacts=bool(rollback["failureKeepsCurrentArtifacts"]),
        rollback_exposed_compiler_artifacts=bool(rollback["compilerArtifactsPublished"]),
    )


def _all_same(values: tuple[object, ...]) -> bool:
    return len(set(values)) <= 1


def _summaries(
    *,
    reports: tuple[ReadinessReport, ...],
    readiness_jsons: tuple[str, ...],
    cycles: tuple[OperationalCycleEvidence, ...],
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    parity_statuses = tuple(cycle.parity_status for cycle in cycles)
    matching_entities = tuple(cycle.parity_matching_entities for cycle in cycles)
    readiness_statuses = tuple(cycle.readiness_status.value for cycle in cycles)
    blocked_counts = tuple(cycle.blocked_item_count for cycle in cycles)
    release_ids = tuple(cycle.release_candidate_identifier for cycle in cycles)
    evidence_digests = tuple(cycle.readiness_evidence_digest for cycle in cycles)
    rollback_current_digests = tuple(cycle.rollback_current_artifact_digest for cycle in cycles)
    rollback_failure_digests = tuple(cycle.rollback_failure_artifact_digest for cycle in cycles)
    parity_summary = {
        "allParityPassed": all(status == "passed" for status in parity_statuses),
        "parityStatuses": list(parity_statuses),
        "matchingEntityCounts": list(matching_entities),
        "matchingEntityCountsStable": _all_same(matching_entities),
    }
    operational_stability = {
        "allReadinessPassed": all(report.passed for report in reports),
        "readinessStatuses": list(readiness_statuses),
        "blockedItemCounts": list(blocked_counts),
        "blockedItemCountsStable": _all_same(blocked_counts),
        "noBlockedItems": all(count == 0 for count in blocked_counts),
    }
    deterministic_evidence_summary = {
        "minimumRepeatedExecutions": len(cycles) >= 2,
        "releaseCandidateIdentifiersStable": _all_same(release_ids),
        "readinessEvidenceDigestsStable": _all_same(evidence_digests),
        "readinessJsonStable": _all_same(readiness_jsons),
    }
    failure_recovery_summary = {
        "allRollbackFailuresRecorded": all(cycle.rollback_failure_recorded for cycle in cycles),
        "allRollbackPreserveCurrentArtifacts": all(cycle.rollback_preserved_current_artifacts for cycle in cycles),
        "noCompilerArtifactsPublishedDuringRollback": not any(cycle.rollback_exposed_compiler_artifacts for cycle in cycles),
        "rollbackCurrentArtifactDigestStable": _all_same(rollback_current_digests),
        "rollbackFailureArtifactDigestStable": _all_same(rollback_failure_digests),
    }
    return parity_summary, operational_stability, deterministic_evidence_summary, failure_recovery_summary


def _findings(
    *,
    parity_summary: dict[str, object],
    operational_stability: dict[str, object],
    deterministic_evidence_summary: dict[str, object],
    failure_recovery_summary: dict[str, object],
) -> tuple[OperationalFinding, ...]:
    findings: list[OperationalFinding] = []
    if not deterministic_evidence_summary["minimumRepeatedExecutions"]:
        findings.append(_finding("execution_count_too_low", "Operational validation requires repeated execution", "executionCount"))
    if not operational_stability["allReadinessPassed"]:
        findings.append(_finding("readiness_cycle_blocked", "Every operational cycle must pass Phase 5 readiness", "readiness"))
    if not operational_stability["blockedItemCountsStable"]:
        findings.append(_finding("blocked_item_count_unstable", "Blocked readiness item counts must remain stable across cycles", "blockedItems"))
    if not parity_summary["allParityPassed"]:
        findings.append(_finding("parity_cycle_failed", "Every operational cycle must preserve shadow comparison parity", "parity"))
    if not parity_summary["matchingEntityCountsStable"]:
        findings.append(_finding("parity_entity_count_unstable", "Matching entity counts must remain stable across cycles", "parity.matchingEntities"))
    if not deterministic_evidence_summary["releaseCandidateIdentifiersStable"]:
        findings.append(_finding("release_identity_unstable", "Release candidate identity must remain stable across cycles", "releaseCandidateIdentifier"))
    if not deterministic_evidence_summary["readinessEvidenceDigestsStable"]:
        findings.append(_finding("readiness_evidence_unstable", "Readiness evidence digests must remain stable across cycles", "readiness.evidenceDigest"))
    if not deterministic_evidence_summary["readinessJsonStable"]:
        findings.append(_finding("readiness_json_unstable", "Serialized readiness evidence must remain stable across cycles", "readiness"))
    if not failure_recovery_summary["allRollbackFailuresRecorded"]:
        findings.append(_finding("rollback_failure_not_recorded", "Every rollback probe must record compiler failure evidence", "rollback"))
    if not failure_recovery_summary["allRollbackPreserveCurrentArtifacts"]:
        findings.append(_finding("rollback_artifacts_not_preserved", "Every rollback probe must preserve current Knowledge artifacts", "rollback"))
    if not failure_recovery_summary["noCompilerArtifactsPublishedDuringRollback"]:
        findings.append(_finding("rollback_compiler_artifacts_exposed", "Rollback probes must not expose compiler output or comparison reports", "rollback"))
    if not failure_recovery_summary["rollbackCurrentArtifactDigestStable"]:
        findings.append(_finding("rollback_current_digest_unstable", "Current artifact digest must remain stable across rollback probes", "rollback.currentArtifactDigest"))
    if not failure_recovery_summary["rollbackFailureArtifactDigestStable"]:
        findings.append(_finding("rollback_failure_digest_unstable", "Failure artifact digest must remain stable across rollback probes", "rollback.failureArtifactDigest"))
    return tuple(findings)


def validate_operational_behavior(
    *,
    registry: KnowledgeRegistry | None = None,
    cycles: int = 3,
    compiler_executor: Callable[[PublicArtifacts], CompilerOutput] = compile_from_knowledge_artifacts,
    rollback_executor: Callable[[PublicArtifacts], CompilerOutput] | None = None,
) -> OperationalReport:
    reports = tuple(
        _readiness_report(
            registry=registry,
            compiler_executor=compiler_executor,
            rollback_executor=rollback_executor,
        )
        for _ in range(cycles)
    )
    readiness_jsons = tuple(stable_readiness_json(report) for report in reports)
    cycles_evidence = tuple(_cycle_evidence(index + 1, report) for index, report in enumerate(reports))
    parity_summary, operational_stability, deterministic_summary, failure_summary = _summaries(
        reports=reports,
        readiness_jsons=readiness_jsons,
        cycles=cycles_evidence,
    )
    findings = _findings(
        parity_summary=parity_summary,
        operational_stability=operational_stability,
        deterministic_evidence_summary=deterministic_summary,
        failure_recovery_summary=failure_summary,
    )
    return OperationalReport(
        execution_count=cycles,
        operational_status=OperationalStatus.STABLE if not findings else OperationalStatus.UNSTABLE,
        parity_summary=parity_summary,
        operational_stability=operational_stability,
        deterministic_evidence_summary=deterministic_summary,
        failure_recovery_summary=failure_summary,
        readiness_recommendation=(
            "Keep the Knowledge publisher authoritative until a separate production enablement phase is approved."
            if not findings
            else "Do not authorize production enablement while operational validation findings remain."
        ),
        cycles=cycles_evidence,
        findings=tuple(sorted(findings, key=lambda item: (item.code, item.subject))),
    )
