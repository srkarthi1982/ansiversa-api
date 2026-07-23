"""Internal and public manifest boundaries for isolated compiler candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.ai_seo_compiler.entities import EntityRelease
from app.modules.ai_seo_compiler.graph import GraphBundle, app_webpage_id
from app.modules.ai_seo_compiler.serialization import stable_digest
from app.modules.ai_seo_compiler.validation import Severity, ValidationCode, ValidationFinding, ValidationResult

INTERNAL_MANIFEST_SCHEMA_VERSION = 1
PUBLIC_RENDER_MANIFEST_SCHEMA_VERSION = 1
CONTRACT_VERSION = 1
GRAPH_PROFILE_VERSION = 1
COMPILER_VERSION = "0.2.0"
FORBIDDEN_PUBLIC_MANIFEST_KEYS = {
    "sourceInventory",
    "diagnostics",
    "approver",
    "approverIdentities",
    "rollbackBaseReleaseId",
    "validationReport",
    "internalManifest",
    "sourcePackageRevision",
    "backendRevision",
    "frontendRouteRegistryRevision",
}


@dataclass(frozen=True)
class InternalReleaseManifest:
    release_id: str
    rollback_base_release_id: str | None
    backend_revision: str
    frontend_route_registry_revision: str
    creation_mode: str
    release_status: str
    source_package_revision: str
    graph_digest: str
    entity_digests: dict[str, str]
    page_bundle_digests: dict[str, str]
    artifact_digests: dict[str, str]
    validation_summary: dict[str, int]
    release_blocked: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": INTERNAL_MANIFEST_SCHEMA_VERSION,
            "releaseId": self.release_id,
            "rollbackBaseReleaseId": self.rollback_base_release_id,
            "backendRevision": self.backend_revision,
            "frontendRouteRegistryRevision": self.frontend_route_registry_revision,
            "creationMode": self.creation_mode,
            "releaseStatus": self.release_status,
            "contractVersion": CONTRACT_VERSION,
            "graphProfileVersion": GRAPH_PROFILE_VERSION,
            "compilerVersion": COMPILER_VERSION,
            "sourcePackageRevision": self.source_package_revision,
            "graphDigest": self.graph_digest,
            "entityDigests": dict(sorted(self.entity_digests.items())),
            "pageBundleDigests": dict(sorted(self.page_bundle_digests.items())),
            "artifactDigests": dict(sorted(self.artifact_digests.items())),
            "compatibility": {"publicRenderManifest": PUBLIC_RENDER_MANIFEST_SCHEMA_VERSION},
            "validationSummary": self.validation_summary,
            "releaseBlocked": self.release_blocked,
        }


@dataclass(frozen=True)
class PublicPageBundle:
    route: str
    canonical_url: str
    visible_content: dict[str, object]
    metadata: dict[str, object]
    graph_bundle: dict[str, object]
    entity_revision: str
    release_id: str

    def as_dict(self) -> dict[str, object]:
        return {
            "route": self.route,
            "canonicalUrl": self.canonical_url,
            "visibleContent": self.visible_content,
            "metadata": self.metadata,
            "pageLocalGraphBundle": self.graph_bundle,
            "publicEntityRevision": self.entity_revision,
            "publicReleaseId": self.release_id,
            "compatibleSchemaVersions": {
                "publicRenderManifest": PUBLIC_RENDER_MANIFEST_SCHEMA_VERSION,
                "contract": CONTRACT_VERSION,
                "graphProfile": GRAPH_PROFILE_VERSION,
            },
        }


@dataclass(frozen=True)
class PublicRenderManifest:
    release_id: str
    page_bundles: tuple[PublicPageBundle, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": PUBLIC_RENDER_MANIFEST_SCHEMA_VERSION,
            "releaseId": self.release_id,
            "pageBundles": [bundle.as_dict() for bundle in self.page_bundles],
        }


def release_id_for(*, source_package_revision: str, graph_digest: str, entity_digest: str) -> str:
    return f"ai-seo-{stable_digest({'source': source_package_revision, 'graph': graph_digest, 'entities': entity_digest})[:16]}"


def build_internal_manifest(
    *,
    release: EntityRelease,
    graph: GraphBundle,
    validation: ValidationResult,
    source_package_revision: str,
    backend_revision: str,
    frontend_route_registry_revision: str,
    rollback_base_release_id: str | None = None,
    creation_mode: str = "full",
    release_status: str = "candidate",
) -> InternalReleaseManifest:
    entity_digests = {app.app_id: stable_digest(app.as_dict()) for app in release.apps}
    page_bundle_digests = {app.route: stable_digest({"route": app.route, "entity": app.as_dict()}) for app in release.apps}
    graph_digest = stable_digest(graph.as_dict())
    release_id = release_id_for(
        source_package_revision=source_package_revision,
        graph_digest=graph_digest,
        entity_digest=stable_digest(entity_digests),
    )
    return InternalReleaseManifest(
        release_id=release_id,
        rollback_base_release_id=rollback_base_release_id,
        backend_revision=backend_revision,
        frontend_route_registry_revision=frontend_route_registry_revision,
        creation_mode=creation_mode,
        release_status=release_status,
        source_package_revision=source_package_revision,
        graph_digest=graph_digest,
        entity_digests=entity_digests,
        page_bundle_digests=page_bundle_digests,
        artifact_digests={},
        validation_summary=validation.severity_summary(),
        release_blocked=validation.blocks_release,
    )


def build_public_render_manifest(*, release: EntityRelease, graph: GraphBundle, release_id: str) -> PublicRenderManifest:
    by_id = {str(node["@id"]): node for node in graph.nodes}
    bundles: list[PublicPageBundle] = []
    for app in release.apps:
        page_graph = {
            "@context": "https://schema.org",
            "@graph": [by_id[app_webpage_id(app)], by_id[f"{app.canonical_url}#software"]],
        }
        entity_revision = stable_digest(app.as_dict())
        bundles.append(
            PublicPageBundle(
                route=app.route,
                canonical_url=app.canonical_url,
                visible_content={
                    "name": app.name,
                    "summary": app.short_description,
                    "capabilities": list(app.capabilities),
                },
                metadata={
                    "title": app.name,
                    "description": app.short_description,
                    "canonical": app.canonical_url,
                },
                graph_bundle=page_graph,
                entity_revision=entity_revision,
                release_id=release_id,
            )
        )
    return PublicRenderManifest(release_id, tuple(sorted(bundles, key=lambda bundle: bundle.route)))


def validate_public_manifest_boundary(manifest: PublicRenderManifest) -> ValidationResult:
    serialized = manifest.as_dict()
    findings: list[ValidationFinding] = []

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in FORBIDDEN_PUBLIC_MANIFEST_KEYS:
                    findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.MANIFEST_LEAKAGE, "Public manifest contains governance-only key", path or key))
                walk(child, f"{path}.{key}" if path else key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")
        elif isinstance(value, str):
            if "app/modules/" in value or "AGENTS.md" in value or "DATABASE_URL" in value or "rollbackBaseReleaseId" in value:
                findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.MANIFEST_LEAKAGE, "Public manifest contains internal or sensitive value", path))

    walk(serialized)
    return ValidationResult(tuple(findings))
