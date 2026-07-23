"""SEO-004 graph compilation for validated entity fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.ai_seo_compiler.entities import AppEntity, EntityRelease
from app.modules.ai_seo_compiler.normalization import stable_id_fragment
from app.modules.ai_seo_compiler.validation import Severity, ValidationCode, ValidationFinding, ValidationResult

SCHEMA_CONTEXT = "https://schema.org"
ORGANIZATION_ID = "https://ansiversa.com/#organization"
WEBSITE_ID = "https://ansiversa.com/#website"
APPS_COLLECTION_ID = "https://ansiversa.com/apps#collection"
APP_RELATIONSHIP_PROPERTY = "isRelatedTo"
ALLOWED_NODE_TYPES = {"Organization", "WebSite", "CollectionPage", "WebPage", "SoftwareApplication", "FAQPage", "Question", "Answer"}
ALLOWED_SOFTWARE_PROPERTIES = {
    "@id",
    "@type",
    "name",
    "url",
    "description",
    "applicationCategory",
    "applicationSuite",
    "publisher",
    "isPartOf",
    "alternateName",
    "featureList",
    APP_RELATIONSHIP_PROPERTY,
}
ALLOWED_NODE_PROPERTIES = {
    "Organization": {"@id", "@type", "name", "url"},
    "WebSite": {"@id", "@type", "name", "url", "publisher"},
    "CollectionPage": {"@id", "@type", "name", "url", "isPartOf", "hasPart"},
    "WebPage": {"@id", "@type", "name", "url", "description", "isPartOf", "mainEntity"},
    "SoftwareApplication": ALLOWED_SOFTWARE_PROPERTIES,
    "FAQPage": {"@id", "@type", "name", "url", "isPartOf", "mainEntity"},
    "Question": {"@id", "@type", "name", "acceptedAnswer"},
    "Answer": {"@id", "@type", "text"},
}


@dataclass(frozen=True)
class GraphBundle:
    nodes: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, object]:
        return {"@context": SCHEMA_CONTEXT, "@graph": list(self.nodes)}


def app_software_id(app: AppEntity) -> str:
    return f"{app.canonical_url}#software"


def app_webpage_id(app: AppEntity) -> str:
    return f"{app.canonical_url}#webpage"


def category_collection_id(slug: str) -> str:
    return f"https://ansiversa.com/apps/{stable_id_fragment(slug)}#collection"


def _reference(node_id: str) -> dict[str, str]:
    return {"@id": node_id}


def _software_node(app: AppEntity, app_urls_by_id: dict[str, str]) -> dict[str, Any]:
    node: dict[str, Any] = {
        "@id": app_software_id(app),
        "@type": "SoftwareApplication",
        "name": app.name,
        "url": app.canonical_url,
        "description": app.short_description,
        "applicationCategory": app.category_name,
        "applicationSuite": "Ansiversa",
        "publisher": _reference(ORGANIZATION_ID),
        "isPartOf": _reference(APPS_COLLECTION_ID),
    }
    if app.aliases:
        node["alternateName"] = list(app.aliases)
    if app.capabilities:
        node["featureList"] = list(app.capabilities)
    if app.related_app_ids:
        node[APP_RELATIONSHIP_PROPERTY] = [_reference(f"{app_urls_by_id[related]}#software") for related in app.related_app_ids if related in app_urls_by_id]
    return node


def _webpage_node(app: AppEntity) -> dict[str, Any]:
    return {
        "@id": app_webpage_id(app),
        "@type": "WebPage",
        "name": app.name,
        "url": app.canonical_url,
        "description": app.short_description,
        "isPartOf": _reference(WEBSITE_ID),
        "mainEntity": _reference(app_software_id(app)),
    }


def validate_graph_nodes(nodes: tuple[dict[str, Any], ...]) -> ValidationResult:
    findings: list[ValidationFinding] = []
    ids = [node.get("@id") for node in nodes]
    for node in nodes:
        node_id = str(node.get("@id") or "missing")
        node_type = node.get("@type")
        if node_type not in ALLOWED_NODE_TYPES:
            findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.UNSUPPORTED_GRAPH_PROPERTY, "Unsupported graph node type", node_id))
            continue
        allowed_properties = ALLOWED_NODE_PROPERTIES[str(node_type)]
        extra = set(node) - allowed_properties
        if extra:
            findings.append(
                ValidationFinding(
                    Severity.BLOCKER,
                    ValidationCode.UNSUPPORTED_GRAPH_PROPERTY,
                    f"Unsupported {node_type} properties: {', '.join(sorted(extra))}",
                    node_id,
                )
            )
    for node_id in sorted({node_id for node_id in ids if ids.count(node_id) > 1}):
        findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.DUPLICATE_IDENTITY, "Duplicate graph @id", str(node_id)))
    return ValidationResult(tuple(findings))


def compile_graph(
    release: EntityRelease,
    validation: ValidationResult | None = None,
    extra_nodes: tuple[dict[str, Any], ...] = (),
) -> tuple[GraphBundle | None, ValidationResult]:
    if validation and validation.blocks_release:
        return None, ValidationResult(
            (
                ValidationFinding(
                    Severity.BLOCKER,
                    ValidationCode.RELEASE_BLOCKED,
                    "Graph compilation fails closed after blocking validation failure",
                    "graph",
                ),
            )
        )
    app_ids = {app.app_id: app_software_id(app) for app in release.apps}
    app_urls_by_id = {app.app_id: app.canonical_url for app in release.apps}
    findings: list[ValidationFinding] = []
    for app in release.apps:
        for related in app.related_app_ids:
            if related not in app_ids:
                findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.UNRESOLVED_RELATIONSHIP, "Graph edge target is unresolved", app.app_id))
    nodes: list[dict[str, Any]] = [
        {"@id": ORGANIZATION_ID, "@type": "Organization", "name": release.platform.name, "url": release.platform.canonical_url},
        {"@id": WEBSITE_ID, "@type": "WebSite", "name": release.platform.name, "url": release.platform.canonical_url, "publisher": _reference(ORGANIZATION_ID)},
        {
            "@id": APPS_COLLECTION_ID,
            "@type": "CollectionPage",
            "name": "Ansiversa Apps",
            "url": "https://ansiversa.com/apps",
            "isPartOf": _reference(WEBSITE_ID),
            "hasPart": [_reference(app_software_id(app)) for app in release.apps],
        },
    ]
    for category in release.categories:
        apps = [app for app in release.apps if app.category_id == category.category_id]
        nodes.append(
            {
                "@id": category_collection_id(category.slug),
                "@type": "CollectionPage",
                "name": category.name,
                "url": f"https://ansiversa.com/apps/{category.slug}",
                "isPartOf": _reference(WEBSITE_ID),
                "hasPart": [_reference(app_software_id(app)) for app in apps],
            }
        )
    for page in release.pages:
        nodes.append(
            {
                "@id": f"{page.canonical_url}#webpage",
                "@type": "WebPage",
                "name": page.name,
                "url": page.canonical_url,
                "description": page.summary,
                "isPartOf": _reference(WEBSITE_ID),
            }
        )
    for app in release.apps:
        nodes.append(_webpage_node(app))
        nodes.append(_software_node(app, app_urls_by_id))
    nodes.extend(extra_nodes)
    ordered_nodes = tuple(sorted(nodes, key=lambda node: str(node["@id"])))
    graph_result = validate_graph_nodes(ordered_nodes)
    return GraphBundle(ordered_nodes), ValidationResult(tuple([*findings, *graph_result.findings]))
