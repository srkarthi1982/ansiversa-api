from __future__ import annotations

import json

import pytest

from app.modules.ai_seo_compiler.entities import AppEntity, CategoryEntity, PublicPageEntity, resolve_entities
from app.modules.ai_seo_compiler.graph import compile_graph, validate_graph_nodes
from app.modules.ai_seo_compiler.inventory import SourceInventory, SourceInventoryItem, SourceRepository, SourceVisibility
from app.modules.ai_seo_compiler.manifests import (
    PublicPageBundle,
    PublicRenderManifest,
    build_internal_manifest,
    build_public_render_manifest,
    validate_public_manifest_boundary,
)
from app.modules.ai_seo_compiler.normalization import canonical_url, normalize_route, normalize_slug, stable_list
from app.modules.ai_seo_compiler.parser import parse_json_source, parse_markdown_source, parse_source
from app.modules.ai_seo_compiler.pipeline import CompilerInput, compile_candidate
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.ai_seo_compiler.validation import Severity, detect_conflicts, validate_fixtures
from app.modules.ai_seo_compiler.fixtures import ValidationFixture


def _categories() -> tuple[CategoryEntity, ...]:
    return tuple(
        CategoryEntity(category_id=f"cat_{index:02d}", name=f"Category {index:02d}", slug=f"category-{index:02d}")
        for index in range(1, 15)
    )


def _apps(*, count: int = 100, related: bool = False) -> tuple[AppEntity, ...]:
    categories = _categories()
    apps = []
    for index in range(1, count + 1):
        category = categories[(index - 1) % len(categories)]
        related_ids = ("app_002",) if related and index == 1 and count >= 2 else ()
        apps.append(
            AppEntity(
                app_id=f"app_{index:03d}",
                number=index,
                name=f"App {index:03d}",
                slug=f"app-{index:03d}",
                category_id=category.category_id,
                category_name=category.name,
                purpose=f"App {index:03d} provides approved public purpose.",
                short_description=f"Approved public summary for App {index:03d}.",
                route=f"/app-{index:03d}",
                aliases=(f"App {index:03d}", f"app {index:03d}", "shared alias" if index == 1 else f"unique {index}"),
                capabilities=(f"Capability {index:03d}",),
                related_app_ids=related_ids,
            )
        )
    return tuple(apps)


def _inventory() -> SourceInventory:
    return SourceInventory.from_items(
        [
            SourceInventoryItem(
                repository=SourceRepository.BACKEND,
                path="app/modules/content/data/overview/app-001.json",
                section="hero.description",
                field_name="purpose",
            ),
            SourceInventoryItem(
                repository=SourceRepository.BACKEND,
                path="app/modules/app_001/story.md",
                section="capabilities",
                field_name="currentCapabilities",
            ),
        ]
    )


def test_parser_uses_strict_json_and_preserves_provenance():
    item = SourceInventoryItem(
        repository=SourceRepository.BACKEND,
        path="app/modules/content/data/overview/app-001.json",
        section="hero.description",
        field_name="purpose",
    )
    claim = parse_json_source(item, '{"hero": {"description": "  Approved\\n public purpose. "}}')
    assert claim.value == "Approved public purpose."
    assert claim.provenance.as_dict()["path"] == "app/modules/content/data/overview/app-001.json"
    with pytest.raises(ValueError, match="Malformed JSON"):
        parse_json_source(item, "{")
    with pytest.raises(ValueError, match="Required JSON section missing"):
        parse_json_source(item, '{"hero": {}}')


def test_markdown_parser_is_bounded_and_never_exposes_fenced_raw_markdown():
    item = SourceInventoryItem(
        repository=SourceRepository.BACKEND,
        path="app/modules/app_001/story.md",
        section="capabilities",
        field_name="currentCapabilities",
    )
    claim = parse_markdown_source(item, "## Current Capabilities\nWorks now.\n```\nDATABASE_URL=postgres://x\n```\n")
    assert claim.value == "Works now."
    assert "DATABASE_URL" not in claim.value


def test_parser_rejects_prohibited_sources():
    item = SourceInventoryItem(
        repository=SourceRepository.BACKEND,
        path="app/modules/app_001/story.md",
        section="purpose",
        field_name="purpose",
        visibility=SourceVisibility.PROHIBITED,
    )
    with pytest.raises(ValueError, match="Prohibited sources"):
        parse_source(item, "## Purpose\nHidden")


def test_normalization_is_deterministic_and_does_not_invent_claims():
    assert normalize_slug(" App #001 ") == "app-001"
    assert normalize_route("/App 001") == "/app-001"
    assert canonical_url("/app-001") == "https://ansiversa.com/app-001"
    assert stable_list(("Beta", "alpha", "beta"), lowercase=True) == ("alpha", "beta")
    with pytest.raises(ValueError):
        normalize_route("https://ansiversa.com/app-001")


def test_conflicting_authoritative_values_fail_closed():
    first = parse_json_source(
        SourceInventoryItem(
            repository=SourceRepository.BACKEND,
            path="app/modules/content/data/overview/app-001.json",
            section="hero.description",
            field_name="purpose",
        ),
        '{"hero": {"description": "First approved value"}}',
    )
    second = parse_markdown_source(
        SourceInventoryItem(
            repository=SourceRepository.BACKEND,
            path="app/modules/app_001/story.md",
            section="purpose",
            field_name="purpose",
        ),
        "## Purpose\nSecond approved value",
    )
    result = detect_conflicts((first, second))
    assert result.blocks_release
    assert result.findings[0].severity is Severity.CRITICAL
    assert result.conflicts[0].field_name == "purpose"


def test_fixture_validation_reports_stale_required_truth_where_represented():
    fixture = ValidationFixture(
        fixture_id="stale-purpose",
        source=SourceInventoryItem(
            repository=SourceRepository.BACKEND,
            path="app/modules/app_001/story.md",
            section="purpose",
            field_name="purpose",
        ),
        claims=("Approved but stale truth.",),
        review_state="stale",
    )
    result = validate_fixtures((fixture,))
    assert not result.blocks_release
    assert result.findings[0].code.value == "stale_required_truth"
    assert result.findings[0].severity is Severity.MAJOR


def test_entity_resolution_enforces_exactly_100_apps_and_14_categories():
    release, result = resolve_entities(apps=_apps(), categories=_categories())
    assert result.passed
    assert len(release.apps) == 100
    short_release, short_result = resolve_entities(apps=_apps(count=99), categories=_categories())
    assert short_release.apps
    assert short_result.blocks_release


def test_entity_resolution_rejects_app_101_duplicate_identity_and_unresolved_relationships():
    app_101 = AppEntity(
        app_id="app_101",
        number=101,
        name="App 101",
        slug="app-101",
        category_id="cat_01",
        category_name="Category 01",
        purpose="Not allowed.",
        short_description="Not allowed.",
        route="/app-101",
    )
    _, result = resolve_entities(apps=(*_apps(count=99), app_101), categories=_categories())
    assert result.blocks_release
    assert any(finding.code.value == "app_101_prohibited" for finding in result.findings)

    duplicate = _apps()
    duplicate_app = AppEntity(
        app_id=duplicate[0].app_id,
        number=duplicate[1].number,
        name=duplicate[1].name,
        slug=duplicate[1].slug,
        category_id=duplicate[1].category_id,
        category_name=duplicate[1].category_name,
        purpose=duplicate[1].purpose,
        short_description=duplicate[1].short_description,
        route=duplicate[1].route,
    )
    _, duplicate_result = resolve_entities(apps=(duplicate[0], duplicate_app, *duplicate[2:]), categories=_categories())
    assert duplicate_result.blocks_release

    unresolved = list(_apps())
    unresolved[0] = AppEntity(
        app_id="app_001",
        number=1,
        name="App 001",
        slug="app-001",
        category_id="cat_01",
        category_name="Category 01",
        purpose="App 001 provides approved public purpose.",
        short_description="Approved public summary for App 001.",
        route="/app-001",
        related_app_ids=("missing_app",),
    )
    _, unresolved_result = resolve_entities(apps=tuple(unresolved), categories=_categories())
    assert unresolved_result.blocks_release


def test_graph_compilation_has_stable_ordering_and_resolves_edges():
    release, validation = resolve_entities(apps=_apps(related=True), categories=_categories(), pages=(PublicPageEntity("about", "About", "/about", "About Ansiversa."),))
    graph, graph_validation = compile_graph(release, validation)
    assert graph is not None
    assert graph_validation.passed
    ids = [node["@id"] for node in graph.nodes]
    assert ids == sorted(ids)
    serialized = stable_json(graph.as_dict())
    assert "https://ansiversa.com/app-002#software" in serialized
    assert stable_digest(graph.as_dict()) == stable_digest(json.loads(stable_json(graph.as_dict())))


def test_graph_validation_rejects_unsupported_properties():
    result = validate_graph_nodes(({"@id": "https://ansiversa.com/app-001#software", "@type": "SoftwareApplication", "name": "App", "offers": {}},))
    assert result.blocks_release
    assert result.findings[0].code.value == "unsupported_graph_property"


def test_internal_and_public_manifests_are_separated():
    release, validation = resolve_entities(apps=_apps(), categories=_categories())
    graph, graph_validation = compile_graph(release, validation)
    assert graph is not None and graph_validation.passed
    internal = build_internal_manifest(
        release=release,
        graph=graph,
        validation=validation,
        source_package_revision="source-fixture",
        backend_revision="backend-rev",
        frontend_route_registry_revision="frontend-rev",
        rollback_base_release_id="previous-release",
    )
    public = build_public_render_manifest(release=release, graph=graph, release_id=internal.release_id)
    public_json = stable_json(public.as_dict())
    assert internal.as_dict()["rollbackBaseReleaseId"] == "previous-release"
    assert "rollbackBaseReleaseId" not in public_json
    assert "sourcePackageRevision" not in public_json
    assert "backend-rev" not in public_json
    assert validate_public_manifest_boundary(public).passed


def test_public_manifest_boundary_rejects_governance_leakage():
    public = PublicRenderManifest(
        release_id="release",
        page_bundles=(
            PublicPageBundle(
                route="/app-001",
                canonical_url="https://ansiversa.com/app-001",
                visible_content={"sourceInventory": "app/modules/app_001/story.md"},
                metadata={"title": "App 001"},
                graph_bundle={"@context": "https://schema.org", "@graph": []},
                entity_revision="entity",
                release_id="release",
            ),
        ),
    )
    result = validate_public_manifest_boundary(public)
    assert result.blocks_release


def test_pipeline_repeated_runs_are_equivalent_and_internal_reports_are_deterministic():
    claims = (
        parse_json_source(
            SourceInventoryItem(
                repository=SourceRepository.BACKEND,
                path="app/modules/content/data/overview/app-001.json",
                section="hero.description",
                field_name="purpose",
            ),
            '{"hero": {"description": "Approved public purpose"}}',
        ),
    )
    compiler_input = CompilerInput(source_inventory=_inventory(), parsed_claims=claims, apps=_apps(), categories=_categories())
    first = compile_candidate(compiler_input)
    second = compile_candidate(compiler_input)
    assert first.internal_manifest is not None
    assert first.public_render_manifest is not None
    assert stable_json(first.internal_manifest.as_dict()) == stable_json(second.internal_manifest.as_dict())
    assert stable_json(first.public_render_manifest.as_dict()) == stable_json(second.public_render_manifest.as_dict())
    assert first.validation_report.as_dict()["passed"] is True


def test_pipeline_fails_closed_before_public_output_after_blocker():
    compiler_input = CompilerInput(source_inventory=_inventory(), parsed_claims=(), apps=_apps(count=99), categories=_categories())
    output = compile_candidate(compiler_input)
    assert output.internal_manifest is None
    assert output.public_render_manifest is None
    assert output.graph is None
    assert output.validation_report.as_dict()["passed"] is False
