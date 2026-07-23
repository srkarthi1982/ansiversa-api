"""Controlled AI SEO compiler integration for internal build evidence.

Phase 4 keeps the current Knowledge publisher authoritative. The compiler can
participate only through an explicit disabled-by-default control object, and
failures are captured as internal evidence without replacing public artifacts.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.modules.ai_seo_compiler.entities import AppEntity, CategoryEntity
from app.modules.ai_seo_compiler.inventory import SourceInventory
from app.modules.ai_seo_compiler.pipeline import CompilerInput, CompilerOutput, compile_candidate
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.ai_seo_compiler.shadow import (
    ShadowComparisonReport,
    compare_shadow_snapshots,
    snapshot_from_compiler_output,
    snapshot_from_knowledge_artifacts,
)
from app.modules.ai_seo_compiler.validation import Severity
from app.modules.knowledge.publisher import PublicArtifacts, build_public_artifacts
from app.modules.knowledge.registry import KnowledgeRegistry


class ControlledIntegrationStatus(StrEnum):
    DISABLED = "disabled"
    COMPLETED = "completed"
    FAILED = "failed"


class ControlledParityStatus(StrEnum):
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"


class ControlledFailureCode(StrEnum):
    COMPILER_EXECUTION_FAILED = "compiler_execution_failed"


class ControlledFailureStage(StrEnum):
    CANDIDATE_COMPILATION = "candidate_compilation"


@dataclass(frozen=True)
class ControlledIntegrationControl:
    enabled: bool = False
    execution_duration_ms: int = 0


@dataclass(frozen=True)
class ControlledCompilerExecutionSummary:
    status: ControlledIntegrationStatus
    attempted: bool
    succeeded: bool
    failure_code: ControlledFailureCode | None = None
    failure_stage: ControlledFailureStage | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "attempted": self.attempted,
            "succeeded": self.succeeded,
            "failureCode": self.failure_code.value if self.failure_code else None,
            "failureStage": self.failure_stage.value if self.failure_stage else None,
        }


@dataclass(frozen=True)
class ControlledIntegrationEvidence:
    release_identifier: str
    compiler_execution: ControlledCompilerExecutionSummary
    comparison_summary: dict[str, object]
    validation_summary: dict[str, int]
    parity_status: ControlledParityStatus
    execution_duration_ms: int

    def _payload(self) -> dict[str, object]:
        return {
            "releaseIdentifier": self.release_identifier,
            "compilerExecutionSummary": self.compiler_execution.as_dict(),
            "comparisonSummary": self.comparison_summary,
            "validationSummary": self.validation_summary,
            "parityStatus": self.parity_status.value,
            "executionDurationMs": self.execution_duration_ms,
        }

    def as_dict(self) -> dict[str, object]:
        payload = self._payload()
        return {**payload, "evidenceDigest": stable_digest(payload)}


@dataclass(frozen=True)
class ControlledIntegrationResult:
    artifacts: PublicArtifacts
    evidence: ControlledIntegrationEvidence
    comparison_report: ShadowComparisonReport | None = None
    compiler_output: CompilerOutput | None = None


AI_SEO_CONTROLLED_INTEGRATION_DEFAULT = ControlledIntegrationControl()


def _empty_validation_summary() -> dict[str, int]:
    return {severity.value: 0 for severity in Severity}


def _disabled_evidence() -> ControlledIntegrationEvidence:
    return ControlledIntegrationEvidence(
        release_identifier="ai-seo-controlled-integration-disabled",
        compiler_execution=ControlledCompilerExecutionSummary(
            status=ControlledIntegrationStatus.DISABLED,
            attempted=False,
            succeeded=False,
        ),
        comparison_summary={
            "matchingItems": 0,
            "matchingEntities": 0,
            "mismatches": 0,
            "missingItems": 0,
            "unexpectedItems": 0,
            "findings": 0,
        },
        validation_summary=_empty_validation_summary(),
        parity_status=ControlledParityStatus.NOT_RUN,
        execution_duration_ms=0,
    )


def _failure_evidence(*, execution_duration_ms: int) -> ControlledIntegrationEvidence:
    summary = _empty_validation_summary()
    summary[Severity.BLOCKER.value] = 1
    return ControlledIntegrationEvidence(
        release_identifier="ai-seo-controlled-integration-failed",
        compiler_execution=ControlledCompilerExecutionSummary(
            status=ControlledIntegrationStatus.FAILED,
            attempted=True,
            succeeded=False,
            failure_code=ControlledFailureCode.COMPILER_EXECUTION_FAILED,
            failure_stage=ControlledFailureStage.CANDIDATE_COMPILATION,
        ),
        comparison_summary={
            "matchingItems": 0,
            "matchingEntities": 0,
            "mismatches": 0,
            "missingItems": 0,
            "unexpectedItems": 0,
            "findings": 1,
        },
        validation_summary=summary,
        parity_status=ControlledParityStatus.FAILED,
        execution_duration_ms=execution_duration_ms,
    )


def _evidence_from_report(report: ShadowComparisonReport, *, execution_duration_ms: int) -> ControlledIntegrationEvidence:
    report_dict = report.as_dict()
    return ControlledIntegrationEvidence(
        release_identifier=report.release_id,
        compiler_execution=ControlledCompilerExecutionSummary(
            status=ControlledIntegrationStatus.COMPLETED,
            attempted=True,
            succeeded=True,
        ),
        comparison_summary=dict(report_dict["summary"]),
        validation_summary=dict(report_dict["severitySummary"]),
        parity_status=ControlledParityStatus.PASSED if report.passed else ControlledParityStatus.FAILED,
        execution_duration_ms=execution_duration_ms,
    )


def compiler_input_from_knowledge_artifacts(artifacts: PublicArtifacts) -> CompilerInput:
    categories = tuple(
        CategoryEntity(
            category_id=str(category["id"]),
            name=str(category["name"]),
            slug=str(category["id"]).replace("_", "-"),
        )
        for category in artifacts.knowledge["categories"]
    )
    apps = tuple(
        AppEntity(
            app_id=str(app["id"]),
            number=int(app["number"]),
            name=str(app["name"]),
            slug=str(app["slug"]),
            category_id=str(app["categoryId"]),
            category_name=str(app["category"]),
            purpose=str(app["purpose"]),
            short_description=str(app["description"]),
            route=str(app["route"]),
            aliases=tuple(str(alias) for alias in app["aliases"]),
            capabilities=tuple(str(capability) for capability in app["capabilities"]),
        )
        for app in artifacts.knowledge["apps"]
    )
    return CompilerInput(
        source_inventory=SourceInventory.from_items(()),
        parsed_claims=(),
        apps=apps,
        categories=categories,
    )


def compile_from_knowledge_artifacts(artifacts: PublicArtifacts) -> CompilerOutput:
    return compile_candidate(compiler_input_from_knowledge_artifacts(artifacts))


def run_controlled_integration(
    *,
    registry: KnowledgeRegistry | None = None,
    control: ControlledIntegrationControl = AI_SEO_CONTROLLED_INTEGRATION_DEFAULT,
    compiler_executor: Callable[[PublicArtifacts], CompilerOutput] = compile_from_knowledge_artifacts,
) -> ControlledIntegrationResult:
    artifacts = build_public_artifacts(registry)
    if not control.enabled:
        return ControlledIntegrationResult(artifacts=artifacts, evidence=_disabled_evidence())

    try:
        compiler_output = compiler_executor(artifacts)
        current = snapshot_from_knowledge_artifacts(artifacts)
        candidate = snapshot_from_compiler_output(compiler_output)
        report = compare_shadow_snapshots(current, candidate)
    except Exception:
        return ControlledIntegrationResult(
            artifacts=artifacts,
            evidence=_failure_evidence(execution_duration_ms=control.execution_duration_ms),
        )

    return ControlledIntegrationResult(
        artifacts=artifacts,
        evidence=_evidence_from_report(report, execution_duration_ms=control.execution_duration_ms),
        comparison_report=report,
        compiler_output=compiler_output,
    )


def stable_evidence_json(evidence: ControlledIntegrationEvidence) -> str:
    return stable_json(evidence.as_dict())
