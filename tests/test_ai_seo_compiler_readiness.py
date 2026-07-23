from __future__ import annotations

import copy

from app.modules.ai_seo_compiler.integration import compile_from_knowledge_artifacts
from app.modules.ai_seo_compiler.pipeline import CompilerOutput
from app.modules.ai_seo_compiler.readiness import (
    ReadinessStatus,
    stable_readiness_json,
    validate_production_readiness,
)
from app.modules.ai_seo_compiler.serialization import stable_digest
from app.modules.knowledge import builder
from app.modules.knowledge.publisher import PublicArtifacts, build_public_artifacts
from app.modules.knowledge.registry import KnowledgeRegistry


def _registry() -> KnowledgeRegistry:
    return KnowledgeRegistry(copy.deepcopy(builder.build_registry()[0]))


def test_readiness_validation_passes_for_full_catalog_candidate():
    report = validate_production_readiness(registry=_registry())
    payload = report.as_dict()
    assert report.passed
    assert payload["readinessStatus"] == ReadinessStatus.READY.value
    assert payload["blockedItems"] == []
    assert payload["paritySummary"]["status"] == "passed"
    assert payload["paritySummary"]["comparison"]["matchingEntities"] == 100
    assert payload["rollbackSummary"]["failureKeepsCurrentArtifacts"] is True
    assert payload["rollbackSummary"]["compilerArtifactsPublished"] is False


def test_readiness_validation_is_deterministic_for_repeated_execution():
    first = validate_production_readiness(registry=_registry())
    second = validate_production_readiness(registry=_registry())
    assert stable_readiness_json(first) == stable_readiness_json(second)
    assert first.as_dict()["releaseCandidateIdentifier"] == second.as_dict()["releaseCandidateIdentifier"]
    assert first.as_dict()["evidenceDigest"] == second.as_dict()["evidenceDigest"]


def test_readiness_validation_blocks_when_compiler_execution_fails():
    current = build_public_artifacts(_registry())

    def failing_compiler(_artifacts: PublicArtifacts) -> CompilerOutput:
        raise RuntimeError("readiness compiler failure")

    report = validate_production_readiness(registry=_registry(), compiler_executor=failing_compiler)
    payload = report.as_dict()
    assert not report.passed
    assert payload["readinessStatus"] == ReadinessStatus.BLOCKED.value
    assert any(item["code"] == "compiler_execution" for item in payload["blockedItems"])
    assert any(item["code"] == "parity_report_missing" for item in payload["blockedItems"])
    assert payload["rollbackSummary"]["failureKeepsCurrentArtifacts"] is True
    assert stable_digest(current.knowledge) == stable_digest(build_public_artifacts(_registry()).knowledge)


def test_readiness_validation_blocks_manifest_inconsistency():
    def missing_manifest_compiler(artifacts: PublicArtifacts) -> CompilerOutput:
        output = compile_from_knowledge_artifacts(artifacts)
        return CompilerOutput(
            internal_manifest=output.internal_manifest,
            public_render_manifest=None,
            validation_report=output.validation_report,
            graph=output.graph,
        )

    report = validate_production_readiness(registry=_registry(), compiler_executor=missing_manifest_compiler)
    payload = report.as_dict()
    assert not report.passed
    codes = {item["code"] for item in payload["blockedItems"]}
    assert "public_manifest_missing" in codes
    assert "parity_failed" in codes


def test_readiness_validation_blocks_missing_internal_manifest_only():
    def missing_internal_manifest_compiler(artifacts: PublicArtifacts) -> CompilerOutput:
        output = compile_from_knowledge_artifacts(artifacts)
        return CompilerOutput(
            internal_manifest=None,
            public_render_manifest=output.public_render_manifest,
            validation_report=output.validation_report,
            graph=output.graph,
        )

    report = validate_production_readiness(registry=_registry(), compiler_executor=missing_internal_manifest_compiler)
    payload = report.as_dict()
    assert not report.passed
    assert payload["releaseCandidateIdentifier"] == "ai-seo-readiness-blocked"
    assert any(item["code"] == "internal_manifest_missing" for item in payload["blockedItems"])


def test_readiness_validation_blocks_missing_category_node():
    def missing_category_node_compiler(artifacts: PublicArtifacts) -> CompilerOutput:
        output = compile_from_knowledge_artifacts(artifacts)
        graph = output.graph
        assert graph is not None
        nodes = tuple(
            node
            for node in graph.nodes
            if node.get("@id") != "https://ansiversa.com/apps/cat-business-and-uae#collection"
        )
        graph = type(graph)(nodes)
        return CompilerOutput(output.internal_manifest, output.public_render_manifest, output.validation_report, graph)

    report = validate_production_readiness(registry=_registry(), compiler_executor=missing_category_node_compiler)
    codes = {item["code"] for item in report.as_dict()["blockedItems"]}
    assert not report.passed
    assert "graph_category_node_count" in codes
    assert "graph_category_set_mismatch" in codes
    assert "internal_manifest_graph_digest_mismatch" in codes


def test_readiness_validation_blocks_duplicate_category_identity():
    def duplicate_category_identity_compiler(artifacts: PublicArtifacts) -> CompilerOutput:
        output = compile_from_knowledge_artifacts(artifacts)
        graph = output.graph
        assert graph is not None
        duplicate_name = "Business & UAE"
        changed = False
        nodes = []
        for node in graph.nodes:
            if not changed and node.get("@id") == "https://ansiversa.com/apps/cat-career#collection":
                node = {**node, "name": duplicate_name}
                changed = True
            nodes.append(node)
        graph = type(graph)(tuple(nodes))
        return CompilerOutput(output.internal_manifest, output.public_render_manifest, output.validation_report, graph)

    report = validate_production_readiness(registry=_registry(), compiler_executor=duplicate_category_identity_compiler)
    codes = {item["code"] for item in report.as_dict()["blockedItems"]}
    assert not report.passed
    assert "graph_duplicate_category_identities" in codes
    assert "graph_category_set_mismatch" in codes


def test_readiness_validation_blocks_unresolved_app_category():
    def unresolved_category_compiler(artifacts: PublicArtifacts) -> CompilerOutput:
        output = compile_from_knowledge_artifacts(artifacts)
        graph = output.graph
        assert graph is not None
        nodes = []
        changed = False
        for node in graph.nodes:
            if not changed and node.get("@type") == "SoftwareApplication":
                node = {**node, "applicationCategory": "Unknown Category"}
                changed = True
            nodes.append(node)
        graph = type(graph)(tuple(nodes))
        return CompilerOutput(output.internal_manifest, output.public_render_manifest, output.validation_report, graph)

    report = validate_production_readiness(registry=_registry(), compiler_executor=unresolved_category_compiler)
    codes = {item["code"] for item in report.as_dict()["blockedItems"]}
    assert not report.passed
    assert "graph_unresolved_app_category" in codes


def test_readiness_validation_blocks_rollback_probe_that_publishes_compiler_evidence():
    def successful_rollback_executor(artifacts: PublicArtifacts) -> CompilerOutput:
        return compile_from_knowledge_artifacts(artifacts)

    report = validate_production_readiness(registry=_registry(), rollback_executor=successful_rollback_executor)
    payload = report.as_dict()
    codes = {item["code"] for item in payload["blockedItems"]}
    assert not report.passed
    assert payload["rollbackSummary"]["failureKeepsCurrentArtifacts"] is True
    assert payload["rollbackSummary"]["compilerArtifactsPublished"] is True
    assert payload["rollbackSummary"]["compilerFailureRecorded"] is False
    assert "rollback_compiler_artifacts_published" in codes
    assert "rollback_failure_not_recorded" in codes
    assert "rollback_parity_not_failed" in codes


def test_readiness_validation_includes_rollback_readiness_without_replacing_artifacts():
    current = build_public_artifacts(_registry())
    report = validate_production_readiness(registry=_registry())
    rollback = report.as_dict()["rollbackSummary"]
    assert rollback["currentPublisherAvailable"] is True
    assert rollback["compilerArtifactsPublished"] is False
    assert rollback["failureKeepsCurrentArtifacts"] is True
    assert rollback["compilerFailureRecorded"] is True
    assert rollback["failureParityStatus"] == "failed"
    assert rollback["currentArtifactDigest"] == rollback["failureArtifactDigest"]
    assert rollback["currentArtifactDigest"] == stable_digest(
        {
            "knowledge": current.knowledge,
            "jsonld": current.jsonld,
            "metadata": current.metadata,
            "sitemap": current.sitemap,
            "llms": current.llms,
            "llmsFull": current.llms_full,
            "robots": current.robots,
        }
    )
