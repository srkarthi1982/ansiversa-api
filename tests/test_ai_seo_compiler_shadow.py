from __future__ import annotations

import copy

from app.modules.ai_seo_compiler.entities import AppEntity, CategoryEntity
from app.modules.ai_seo_compiler.inventory import SourceInventory
from app.modules.ai_seo_compiler.pipeline import CompilerInput, compile_candidate
from app.modules.ai_seo_compiler.shadow import (
    CANONICAL_MANIFEST_KEY,
    ShadowComparableItem,
    ShadowItemKind,
    ShadowSnapshot,
    compare_shadow_snapshots,
    snapshot_from_compiler_output,
    snapshot_from_knowledge_artifacts,
    stable_report_json,
)
from app.modules.ai_seo_compiler.validation import Severity
from app.modules.knowledge import builder
from app.modules.knowledge.publisher import build_public_artifacts
from app.modules.knowledge.registry import KnowledgeRegistry


def _item(kind: ShadowItemKind, key: str, payload: dict[str, object], *, digest: str | None = None) -> ShadowComparableItem:
    return ShadowComparableItem.from_payload(kind=kind, key=key, payload=payload, digest=digest)


def _entity(route: str = "/app-001", *, canonical_url: str = "https://ansiversa.com/app-001", name: str = "App 001") -> ShadowComparableItem:
    return _item(
        ShadowItemKind.ENTITY,
        route,
        {
            "route": route,
            "canonicalUrl": canonical_url,
            "visibleContent": {
                "name": name,
                "summary": "Approved public summary.",
                "capabilities": ["Capability"],
            },
        },
    )


def _metadata(route: str = "/app-001", *, canonical: str = "https://ansiversa.com/app-001", title: str = "App 001") -> ShadowComparableItem:
    return _item(
        ShadowItemKind.METADATA,
        route,
        {
            "route": route,
            "canonical": canonical,
            "title": title,
            "description": "Approved public summary.",
        },
    )


def _graph(node_id: str = "https://ansiversa.com/app-001#software", *, name: str = "App 001") -> ShadowComparableItem:
    return _item(
        ShadowItemKind.GRAPH,
        node_id,
        {
            "@id": node_id,
            "@type": "SoftwareApplication",
            "name": name,
            "url": "https://ansiversa.com/app-001",
        },
    )


def _manifest(*, digest: str = "entity-digest") -> ShadowComparableItem:
    return _item(
        ShadowItemKind.MANIFEST,
        CANONICAL_MANIFEST_KEY,
        {
            "releaseId": "release-001",
            "entityDigest": digest,
            "schemaVersion": 1,
        },
    )


def _compiler_output_from_knowledge_artifacts(artifacts):
    categories = tuple(
        CategoryEntity(category_id=category["id"], name=category["name"], slug=str(category["id"]).replace("_", "-"))
        for category in artifacts.knowledge["categories"]
    )
    apps = tuple(
        AppEntity(
            app_id=app["id"],
            number=app["number"],
            name=app["name"],
            slug=app["slug"],
            category_id=app["categoryId"],
            category_name=app["category"],
            purpose=app["purpose"],
            short_description=app["description"],
            route=app["route"],
            aliases=tuple(app["aliases"]),
            capabilities=tuple(app["capabilities"]),
        )
        for app in artifacts.knowledge["apps"]
    )
    return compile_candidate(CompilerInput(source_inventory=SourceInventory.from_items(()), parsed_claims=(), apps=apps, categories=categories))


def _snapshot(*items: ShadowComparableItem, name: str = "current", passed: bool = True, major: int = 0) -> ShadowSnapshot:
    return ShadowSnapshot(
        source_name=name,
        release_id=f"{name}-release",
        items=items,
        validation_summary={
            Severity.BLOCKER.value: 0,
            Severity.CRITICAL.value: 0,
            Severity.MAJOR.value: major,
            Severity.MINOR.value: 0,
            Severity.INFO.value: 0,
        },
        validation_passed=passed,
    )


def test_shadow_comparison_passes_for_identical_outputs():
    current = _snapshot(_entity(), _metadata(), _graph(), _manifest())
    candidate = _snapshot(_entity(), _metadata(), _graph(), _manifest(), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert report.passed
    assert report.as_dict()["recommendation"] == "pass"
    assert report.as_dict()["summary"]["matchingEntities"] == 1
    assert report.as_dict()["summary"]["findings"] == 0


def test_shadow_comparison_detects_metadata_differences():
    current = _snapshot(_metadata())
    candidate = _snapshot(_metadata(title="Changed title"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.mismatches[0].code.value == "metadata_difference"


def test_shadow_comparison_detects_graph_differences():
    current = _snapshot(_graph())
    candidate = _snapshot(_graph(name="Changed graph name"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.mismatches[0].code.value == "graph_difference"


def test_shadow_comparison_detects_entity_differences():
    current = _snapshot(_entity())
    candidate = _snapshot(_entity(name="Changed App"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.mismatches[0].code.value == "entity_difference"


def test_shadow_comparison_detects_canonical_url_differences():
    current = _snapshot(_entity())
    candidate = _snapshot(_entity(canonical_url="https://ansiversa.com/changed"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.mismatches[0].code.value == "canonical_url_difference"


def test_shadow_comparison_detects_digest_mismatches():
    payload = {"releaseId": "release-001", "entityDigest": "entity-digest", "schemaVersion": 1}
    current = _snapshot(_item(ShadowItemKind.MANIFEST, "public-render-manifest", payload, digest="digest-a"))
    candidate = _snapshot(_item(ShadowItemKind.MANIFEST, "public-render-manifest", payload, digest="digest-b"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.mismatches[0].code.value == "digest_mismatch"


def test_shadow_comparison_detects_missing_and_unexpected_entities():
    current = _snapshot(_entity("/app-001"), _entity("/app-002", canonical_url="https://ansiversa.com/app-002"))
    candidate = _snapshot(_entity("/app-001"), _entity("/app-003", canonical_url="https://ansiversa.com/app-003"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    codes = {finding.code.value for finding in report.findings}
    assert not report.passed
    assert {"missing_item", "unexpected_item"} <= codes
    assert report.as_dict()["summary"]["missingItems"] == 1
    assert report.as_dict()["summary"]["unexpectedItems"] == 1


def test_shadow_comparison_detects_duplicate_entities():
    current = _snapshot(_entity(), _entity())
    candidate = _snapshot(_entity(), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert any(finding.code.value == "duplicate_item" for finding in report.findings)


def test_shadow_comparison_detects_ordering_differences():
    current = _snapshot(_entity("/app-001"), _metadata("/app-001"))
    candidate = _snapshot(_metadata("/app-001"), _entity("/app-001"), name="candidate")
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert any(finding.code.value == "ordering_difference" for finding in report.findings)


def test_shadow_comparison_detects_validation_severity_differences():
    current = _snapshot(_entity())
    candidate = _snapshot(_entity(), name="candidate", major=1)
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert any(finding.code.value == "validation_severity_difference" for finding in report.findings)


def test_shadow_comparison_is_deterministic():
    current = _snapshot(_entity(), _metadata(), _graph(), _manifest())
    candidate = _snapshot(_entity(), _metadata(), _graph(), _manifest(), name="candidate")
    first = compare_shadow_snapshots(current, candidate)
    second = compare_shadow_snapshots(current, candidate)
    assert stable_report_json(first) == stable_report_json(second)


def test_shadow_comparison_fails_closed_when_candidate_validation_failed():
    current = _snapshot(_entity())
    candidate = _snapshot(_entity(), name="candidate", passed=False)
    report = compare_shadow_snapshots(current, candidate)
    assert not report.passed
    assert report.as_dict()["recommendation"] == "fail_closed"
    assert any(finding.code.value == "release_blocked" for finding in report.findings)


def test_shadow_snapshot_from_knowledge_artifacts_is_internal_and_deterministic():
    registry_data = builder.build_registry()[0]
    artifacts = build_public_artifacts(KnowledgeRegistry(copy.deepcopy(registry_data)))
    first = snapshot_from_knowledge_artifacts(artifacts)
    second = snapshot_from_knowledge_artifacts(artifacts)
    report = compare_shadow_snapshots(first, second)
    assert first.as_dict() == second.as_dict()
    assert report.passed
    assert len([item for item in first.items if item.kind is ShadowItemKind.ENTITY]) == 100
    assert any(item.kind is ShadowItemKind.MANIFEST for item in first.items)


def test_shadow_adapters_compare_equivalent_knowledge_and_compiler_outputs_without_false_positives():
    registry_data = builder.build_registry()[0]
    artifacts = build_public_artifacts(KnowledgeRegistry(copy.deepcopy(registry_data)))
    compiler_output = _compiler_output_from_knowledge_artifacts(artifacts)
    current = snapshot_from_knowledge_artifacts(artifacts)
    candidate = snapshot_from_compiler_output(compiler_output)
    report = compare_shadow_snapshots(current, candidate)
    assert compiler_output.public_render_manifest is not None
    assert current.ordered_identities() == candidate.ordered_identities()
    assert report.passed
    assert report.as_dict()["summary"]["findings"] == 0


def test_shadow_adapters_detect_intentional_metadata_difference_without_structural_false_positive():
    registry_data = builder.build_registry()[0]
    artifacts = build_public_artifacts(KnowledgeRegistry(copy.deepcopy(registry_data)))
    compiler_output = _compiler_output_from_knowledge_artifacts(artifacts)
    current = snapshot_from_knowledge_artifacts(artifacts)
    candidate = snapshot_from_compiler_output(compiler_output)
    changed_items: list[ShadowComparableItem] = []
    changed = False
    for item in candidate.items:
        if not changed and item.identity == "metadata:/bill-splitter":
            payload = dict(item.payload)
            payload["description"] = "Intentional metadata difference."
            changed_items.append(ShadowComparableItem.from_payload(kind=item.kind, key=item.key, payload=payload))
            changed = True
        else:
            changed_items.append(item)
    changed_candidate = ShadowSnapshot(
        source_name=candidate.source_name,
        release_id=candidate.release_id,
        items=tuple(changed_items),
        validation_summary=candidate.validation_summary,
        validation_passed=candidate.validation_passed,
    )
    report = compare_shadow_snapshots(current, changed_candidate)
    assert changed
    assert not report.passed
    assert [finding.code.value for finding in report.findings] == ["metadata_difference"]
    assert report.findings[0].subject == "metadata:/bill-splitter"
