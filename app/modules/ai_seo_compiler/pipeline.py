"""Isolated Phase 2 compiler pipeline harness.

The harness compiles supplied in-memory fixtures only. It does not read
repository source files, write artifacts, register routes, or publish output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.ai_seo_compiler.entities import AppEntity, CategoryEntity, PublicPageEntity, resolve_entities
from app.modules.ai_seo_compiler.graph import GraphBundle, compile_graph
from app.modules.ai_seo_compiler.inventory import SourceInventory
from app.modules.ai_seo_compiler.manifests import (
    InternalReleaseManifest,
    PublicRenderManifest,
    build_internal_manifest,
    build_public_render_manifest,
    validate_public_manifest_boundary,
)
from app.modules.ai_seo_compiler.parser import ParsedClaim
from app.modules.ai_seo_compiler.reports import ValidationReport
from app.modules.ai_seo_compiler.serialization import stable_digest
from app.modules.ai_seo_compiler.validation import ValidationResult, detect_conflicts, merge_results


@dataclass(frozen=True)
class CompilerInput:
    source_inventory: SourceInventory
    parsed_claims: tuple[ParsedClaim, ...]
    apps: tuple[AppEntity, ...]
    categories: tuple[CategoryEntity, ...]
    pages: tuple[PublicPageEntity, ...] = ()
    backend_revision: str = "backend-fixture"
    frontend_route_registry_revision: str = "frontend-fixture"
    rollback_base_release_id: str | None = None
    require_full_catalog: bool = True
    fixture_extra_graph_nodes: tuple[dict[str, Any], ...] = ()
    fixture_public_visible_content_overrides: dict[str, dict[str, object]] | None = None


@dataclass(frozen=True)
class CompilerOutput:
    internal_manifest: InternalReleaseManifest | None
    public_render_manifest: PublicRenderManifest | None
    validation_report: ValidationReport
    graph: GraphBundle | None


def compile_candidate(data: CompilerInput) -> CompilerOutput:
    source_revision = stable_digest(data.source_inventory.as_dict())
    source_validation = detect_conflicts(data.parsed_claims)
    release, entity_validation = resolve_entities(
        apps=data.apps,
        categories=data.categories,
        pages=data.pages,
        require_full_catalog=data.require_full_catalog,
    )
    validation = merge_results(source_validation, entity_validation)
    graph, graph_validation = compile_graph(release, validation, extra_nodes=data.fixture_extra_graph_nodes)
    validation = merge_results(validation, graph_validation)
    if graph is None or graph_validation.blocks_release:
        report = ValidationReport(
            release_id="blocked",
            validation=validation,
            source_count=len(data.source_inventory.items),
            entity_count=len(data.apps) + len(data.categories) + len(data.pages) + 1,
            graph_passed=False,
            manifest_passed=False,
        )
        return CompilerOutput(None, None, report, None)
    internal_manifest = build_internal_manifest(
        release=release,
        graph=graph,
        validation=validation,
        source_package_revision=source_revision,
        backend_revision=data.backend_revision,
        frontend_route_registry_revision=data.frontend_route_registry_revision,
        rollback_base_release_id=data.rollback_base_release_id,
    )
    public_manifest = build_public_render_manifest(
        release=release,
        graph=graph,
        release_id=internal_manifest.release_id,
        visible_content_overrides=data.fixture_public_visible_content_overrides,
    )
    manifest_validation = validate_public_manifest_boundary(public_manifest)
    validation = merge_results(validation, manifest_validation)
    internal_manifest = build_internal_manifest(
        release=release,
        graph=graph,
        validation=validation,
        source_package_revision=source_revision,
        backend_revision=data.backend_revision,
        frontend_route_registry_revision=data.frontend_route_registry_revision,
        rollback_base_release_id=data.rollback_base_release_id,
    )
    report = ValidationReport(
        release_id=internal_manifest.release_id,
        validation=validation,
        source_count=len(data.source_inventory.items),
        entity_count=len(data.apps) + len(data.categories) + len(data.pages) + 1,
        graph_passed=not graph_validation.blocks_release,
        manifest_passed=not manifest_validation.blocks_release,
    )
    if manifest_validation.blocks_release:
        return CompilerOutput(internal_manifest, None, report, graph)
    return CompilerOutput(internal_manifest, public_manifest, report, graph)
