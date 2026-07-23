"""Production readiness validation for the internal AI SEO compiler.

Phase 5 validates readiness evidence only. It does not write artifacts, expose
routes, change startup behavior, or make the compiler a production publisher.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from app.modules.ai_seo_compiler.integration import (
    ControlledIntegrationControl,
    ControlledIntegrationResult,
    compile_from_knowledge_artifacts,
    run_controlled_integration,
    stable_evidence_json,
)
from app.modules.ai_seo_compiler.pipeline import CompilerOutput
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.knowledge.publisher import PublicArtifacts
from app.modules.knowledge.registry import KnowledgeRegistry


class ReadinessStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ReadinessFinding:
    code: str
    message: str
    subject: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "subject": self.subject}


@dataclass(frozen=True)
class ReadinessReport:
    release_candidate_identifier: str
    readiness_status: ReadinessStatus
    validation_summary: dict[str, int]
    parity_summary: dict[str, object]
    rollback_summary: dict[str, object]
    blocked_items: tuple[ReadinessFinding, ...]
    recommendations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.readiness_status is ReadinessStatus.READY

    def _payload(self) -> dict[str, object]:
        return {
            "releaseCandidateIdentifier": self.release_candidate_identifier,
            "readinessStatus": self.readiness_status.value,
            "validationSummary": dict(sorted(self.validation_summary.items())),
            "paritySummary": self.parity_summary,
            "rollbackSummary": self.rollback_summary,
            "blockedItems": [finding.as_dict() for finding in self.blocked_items],
            "recommendations": list(self.recommendations),
        }

    def as_dict(self) -> dict[str, object]:
        payload = self._payload()
        return {**payload, "evidenceDigest": stable_digest(payload)}


def stable_readiness_json(report: ReadinessReport) -> str:
    return stable_json(report.as_dict())


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


def _finding(code: str, message: str, subject: str) -> ReadinessFinding:
    return ReadinessFinding(code=code, message=message, subject=subject)


def _release_candidate_identifier(result: ControlledIntegrationResult) -> str:
    if result.compiler_output and result.compiler_output.internal_manifest:
        return result.compiler_output.internal_manifest.release_id
    return "ai-seo-readiness-blocked"


def _validate_catalog(result: ControlledIntegrationResult) -> tuple[ReadinessFinding, ...]:
    findings: list[ReadinessFinding] = []
    knowledge = result.artifacts.knowledge
    if len(knowledge["apps"]) != 100:
        findings.append(_finding("catalog_app_count", "Current Knowledge output must contain exactly 100 apps", "knowledge.apps"))
    if len(knowledge["categories"]) != 14:
        findings.append(_finding("catalog_category_count", "Current Knowledge output must contain exactly 14 categories", "knowledge.categories"))
    if result.compiler_output is None:
        findings.append(_finding("compiler_execution", "Compiler execution must complete for readiness validation", "compiler"))
        return tuple(findings)
    if result.compiler_output.public_render_manifest is None:
        findings.append(_finding("public_manifest_missing", "Compiler must produce an internal public render manifest candidate", "publicRenderManifest"))
    if result.compiler_output.graph is None:
        findings.append(_finding("graph_missing", "Compiler must produce a graph candidate", "graph"))
    return tuple(findings)


def _validate_manifest(result: ControlledIntegrationResult) -> tuple[ReadinessFinding, ...]:
    output = result.compiler_output
    if output is None or output.public_render_manifest is None:
        return ()
    manifest = output.public_render_manifest
    findings: list[ReadinessFinding] = []
    bundles = manifest.page_bundles
    if len(bundles) != 100:
        findings.append(_finding("manifest_page_bundle_count", "Public render manifest must contain exactly 100 app page bundles", "pageBundles"))
    release_ids = {bundle.release_id for bundle in bundles}
    if release_ids != {manifest.release_id}:
        findings.append(_finding("manifest_release_identity", "Every page bundle must use the manifest release ID", "publicReleaseId"))
    routes = [bundle.route for bundle in bundles]
    canonicals = [bundle.canonical_url for bundle in bundles]
    if len(routes) != len(set(routes)):
        findings.append(_finding("manifest_duplicate_routes", "Public render manifest routes must be unique", "pageBundles.route"))
    if len(canonicals) != len(set(canonicals)):
        findings.append(_finding("manifest_duplicate_canonicals", "Public render manifest canonical URLs must be unique", "pageBundles.canonicalUrl"))
    if any(not route.startswith("/") or route.startswith("//") for route in routes):
        findings.append(_finding("manifest_invalid_route", "Public render manifest routes must be canonical internal routes", "pageBundles.route"))
    if any(not canonical.startswith("https://ansiversa.com/") for canonical in canonicals):
        findings.append(_finding("manifest_invalid_canonical", "Public render manifest canonical URLs must use ansiversa.com", "pageBundles.canonicalUrl"))
    return tuple(findings)


def _validate_graph(result: ControlledIntegrationResult) -> tuple[ReadinessFinding, ...]:
    output = result.compiler_output
    if output is None or output.graph is None:
        return ()
    graph_nodes = output.graph.nodes
    software_nodes = [node for node in graph_nodes if node.get("@type") == "SoftwareApplication"]
    ids = [str(node.get("@id")) for node in graph_nodes]
    findings: list[ReadinessFinding] = []
    if len(software_nodes) != 100:
        findings.append(_finding("graph_app_node_count", "Graph candidate must contain exactly 100 SoftwareApplication nodes", "graph"))
    if len(ids) != len(set(ids)):
        findings.append(_finding("graph_duplicate_ids", "Graph candidate @id values must be unique", "graph.@id"))
    return tuple(findings)


def _validate_metadata(result: ControlledIntegrationResult) -> tuple[ReadinessFinding, ...]:
    output = result.compiler_output
    if output is None or output.public_render_manifest is None:
        return ()
    findings: list[ReadinessFinding] = []
    for bundle in output.public_render_manifest.page_bundles:
        metadata = bundle.metadata
        if metadata.get("canonical") != bundle.canonical_url:
            findings.append(_finding("metadata_canonical_mismatch", "Metadata canonical must match the page bundle canonical URL", bundle.route))
        if not metadata.get("description"):
            findings.append(_finding("metadata_description_missing", "Metadata description is required for every app bundle", bundle.route))
    return tuple(findings)


def _validate_parity(result: ControlledIntegrationResult) -> tuple[ReadinessFinding, ...]:
    if result.comparison_report is None:
        return (_finding("parity_report_missing", "Readiness validation requires a shadow comparison report", "comparison"),)
    if not result.comparison_report.passed:
        return (_finding("parity_failed", "Shadow comparison must pass before production readiness", result.comparison_report.release_id),)
    return ()


def _rollback_summary(registry: KnowledgeRegistry | None, expected_artifact_digest: str) -> dict[str, object]:
    def failing_compiler(_artifacts: PublicArtifacts) -> CompilerOutput:
        raise RuntimeError("readiness rollback probe")

    failure_result = run_controlled_integration(
        registry=registry,
        control=ControlledIntegrationControl(enabled=True),
        compiler_executor=failing_compiler,
    )
    failure_digest = _artifacts_digest(failure_result.artifacts)
    return {
        "currentPublisherAvailable": True,
        "compilerArtifactsPublished": False,
        "failureKeepsCurrentArtifacts": failure_digest == expected_artifact_digest,
        "currentArtifactDigest": expected_artifact_digest,
        "failureArtifactDigest": failure_digest,
        "failureParityStatus": failure_result.evidence.parity_status.value,
    }


def _validate_determinism(
    registry: KnowledgeRegistry | None,
    compiler_executor: Callable[[PublicArtifacts], CompilerOutput],
    first_result: ControlledIntegrationResult,
) -> tuple[dict[str, object], tuple[ReadinessFinding, ...]]:
    second = run_controlled_integration(
        registry=registry,
        control=ControlledIntegrationControl(enabled=True),
        compiler_executor=compiler_executor,
    )
    first_release = _release_candidate_identifier(first_result)
    second_release = _release_candidate_identifier(second)
    first_report = first_result.comparison_report.as_dict() if first_result.comparison_report else None
    second_report = second.comparison_report.as_dict() if second.comparison_report else None
    checks = {
        "releaseIdentifierStable": first_release == second_release,
        "integrationEvidenceStable": stable_evidence_json(first_result.evidence) == stable_evidence_json(second.evidence),
        "comparisonReportStable": first_report == second_report,
        "artifactDigestStable": _artifacts_digest(first_result.artifacts) == _artifacts_digest(second.artifacts),
    }
    findings = tuple(
        _finding("determinism_failed", "Readiness evidence must be deterministic across repeated execution", key)
        for key, passed in checks.items()
        if not passed
    )
    return checks, findings


def _validation_summary(findings: tuple[ReadinessFinding, ...]) -> dict[str, int]:
    counts = Counter(finding.code for finding in findings)
    return {key: counts[key] for key in sorted(counts)}


def _recommendations(findings: tuple[ReadinessFinding, ...]) -> tuple[str, ...]:
    if not findings:
        return (
            "Keep the Knowledge publisher authoritative until a separate production enablement phase is approved.",
            "Use this readiness evidence for Astra source review before freezing Phase 5.",
        )
    return (
        "Do not authorize production enablement while readiness findings remain.",
        "Correct the blocked readiness items and repeat Phase 5 source review.",
    )


def validate_production_readiness(
    *,
    registry: KnowledgeRegistry | None = None,
    compiler_executor: Callable[[PublicArtifacts], CompilerOutput] = compile_from_knowledge_artifacts,
) -> ReadinessReport:
    result = run_controlled_integration(
        registry=registry,
        control=ControlledIntegrationControl(enabled=True),
        compiler_executor=compiler_executor,
    )
    artifact_digest = _artifacts_digest(result.artifacts)
    rollback_summary = _rollback_summary(registry, artifact_digest)
    determinism_summary, determinism_findings = _validate_determinism(registry, compiler_executor, result)
    findings = (
        *_validate_catalog(result),
        *_validate_manifest(result),
        *_validate_graph(result),
        *_validate_metadata(result),
        *_validate_parity(result),
        *determinism_findings,
    )
    if not rollback_summary["failureKeepsCurrentArtifacts"]:
        findings = (*findings, _finding("rollback_artifact_mismatch", "Compiler failure must preserve current Knowledge artifacts", "rollback"))
    parity_summary = {
        "status": result.evidence.parity_status.value,
        "comparison": result.comparison_report.as_dict()["summary"] if result.comparison_report else {},
        "determinism": determinism_summary,
    }
    ordered_findings = tuple(sorted(findings, key=lambda item: (item.code, item.subject)))
    return ReadinessReport(
        release_candidate_identifier=_release_candidate_identifier(result),
        readiness_status=ReadinessStatus.READY if not ordered_findings else ReadinessStatus.BLOCKED,
        validation_summary=_validation_summary(ordered_findings),
        parity_summary=parity_summary,
        rollback_summary=rollback_summary,
        blocked_items=ordered_findings,
        recommendations=_recommendations(ordered_findings),
    )
