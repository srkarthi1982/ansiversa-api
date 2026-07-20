"""Generate public AI knowledge artifacts from the canonical registry."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from app.modules.knowledge.builder import BACKEND_ROOT, VISIBILITIES, normalize_text
from app.modules.knowledge.registry import KnowledgeRegistry

PUBLIC_SCHEMA_VERSION = 1
PUBLIC_GENERATOR_VERSION = "1.0.0"
PUBLIC_GENERATED_AT = "2026-07-20T00:00:00Z"
PUBLIC_DIR = BACKEND_ROOT / "public"
SITE_URL = "https://ansiversa.com"
PUBLIC_AI_KNOWLEDGE_PATH = PUBLIC_DIR / "public-ai-knowledge.json"
PUBLIC_AI_JSONLD_PATH = PUBLIC_DIR / "public-ai-jsonld.json"
PUBLIC_AI_METADATA_PATH = PUBLIC_DIR / "public-ai-metadata.json"
PUBLIC_AI_SITEMAP_PATH = PUBLIC_DIR / "ai-sitemap.xml"
LLMS_PATH = PUBLIC_DIR / "llms.txt"
LLMS_FULL_PATH = PUBLIC_DIR / "llms-full.txt"
ROBOTS_PATH = PUBLIC_DIR / "robots.txt"

FORBIDDEN_PUBLIC_PATTERNS = {
    "agents": re.compile(r"AGENTS\.md|# AGENTS\.md|Codex Responsibility", re.I),
    "story-path": re.compile(r"story\.md", re.I),
    "certification": re.compile(r"certification|approval report|promotion", re.I),
    "future": re.compile(r"futureDirection|Future Version Ideas|V1\.\d|V2:|\bin V\d\b", re.I),
    "internal": re.compile(r"\binternal\b|\brestricted\b|\bauthenticated\b", re.I),
    "secret": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|authorization\s*:\s*bearer\s+\S+|(?:API_KEY|TOKEN|PASSWORD|DATABASE_URL)\s*=",
        re.I,
    ),
}

NON_PUBLIC_CAPABILITY_PATTERNS = (
    re.compile(r"\bfrontend\b|\bbackend\b|\bdatabase\b|\bmigration\b|\balembic\b", re.I),
    re.compile(r"\bauthenticated\b|\bowner-scoped\b|\blazy-loaded\b|\blocalStorage\b|\bZustand\b", re.I),
    re.compile(r"\bAPI-driven overview metadata\b|\bgenerated API\b|\bOpenAPI\b", re.I),
    re.compile(r"^No\b|\bin V\d\b|\bAPI-driven\b|\bprotected routes\b", re.I),
    re.compile(r"\bcertification\b|\bpromotion\b|\bapproval\b", re.I),
)


@dataclass(frozen=True)
class PublicArtifacts:
    knowledge: dict[str, Any]
    jsonld: dict[str, Any]
    metadata: dict[str, Any]
    sitemap: str
    llms: str
    llms_full: str
    robots: str


def canonical_url(route: str) -> str:
    if not route.startswith("/") or route.startswith("//"):
        raise ValueError(f"Invalid public route: {route}")
    if route == "/":
        return SITE_URL
    return f"{SITE_URL}{route}"


def _public_apps(registry: KnowledgeRegistry) -> list[dict[str, Any]]:
    return registry.apps({"public"})


def _public_categories(registry: KnowledgeRegistry) -> list[dict[str, Any]]:
    return [
        {"id": category["id"], "name": category["name"], "visibility": "public"}
        for category in registry.data["categories"]
        if category["visibility"] == "public"
    ]


def _public_pages(registry: KnowledgeRegistry) -> list[dict[str, Any]]:
    allowed_routes = {"/", "/about", "/pricing", "/faq", "/contact", "/apps", "/privacy", "/terms"}
    pages = []
    for page in registry.pages({"public"}):
        route = str(page["route"])
        if route not in allowed_routes:
            continue
        summary = page.get("summary") or f"{page['name']} is an Ansiversa public page."
        pages.append(
            {
                "id": page["id"],
                "name": page["name"],
                "route": route,
                "canonicalUrl": canonical_url(route),
                "summary": summary,
                "aliases": list(page.get("searchAliases") or []),
                "visibility": "public",
            }
        )
    return pages


def _app_summary(app: dict[str, Any]) -> dict[str, Any]:
    capabilities = [
        value
        for value in app["currentCapabilities"]
        if not any(pattern.search(value) for pattern in NON_PUBLIC_CAPABILITY_PATTERNS)
    ][:8]
    description = _public_text(str(app["shortDescription"] or app["purpose"] or ""))
    purpose = _public_text(str(app["purpose"] or description))
    return {
        "number": app["number"],
        "id": app["id"],
        "slug": app["slug"],
        "name": app["name"],
        "category": app["category"],
        "categoryId": app["categoryId"],
        "route": app["overviewRoute"],
        "exploreRoute": app["exploreRoute"],
        "canonicalUrl": canonical_url(app["overviewRoute"]),
        "exploreUrl": canonical_url(app["exploreRoute"]),
        "description": description,
        "purpose": purpose,
        "capabilities": capabilities,
        "audiences": list(app["intendedAudiences"]),
        "aliases": list(app["searchAliases"]),
        "relatedApps": list(app["relatedApps"]),
        "visibility": "public",
    }


def _public_text(value: str) -> str:
    value = re.sub(r"\s+in V\d\b", "", value)
    value = re.sub(r"\bV\d\b", "", value)
    return normalize_text(value)


def build_public_knowledge(registry: KnowledgeRegistry | None = None) -> dict[str, Any]:
    registry = registry or KnowledgeRegistry.load()
    platform = registry.data["platform"]
    apps = [_app_summary(app) for app in _public_apps(registry)]
    categories = _public_categories(registry)
    pages = _public_pages(registry)

    return {
        "schemaVersion": PUBLIC_SCHEMA_VERSION,
        "generatedAt": PUBLIC_GENERATED_AT,
        "generatorVersion": PUBLIC_GENERATOR_VERSION,
        "canonicalSource": {
            "name": "Canonical AI Knowledge Registry",
            "schemaVersion": registry.data["schemaVersion"],
            "generatorVersion": registry.data["generatorVersion"],
        },
        "platform": {
            "name": platform["name"],
            "shortName": platform["shortName"],
            "canonicalUrl": platform["canonicalUrl"],
            "description": platform["purpose"],
            "positioning": platform["positioning"],
            "tagline": platform["tagline"],
            "appCount": platform["appCount"],
            "categoryCount": platform["categoryCount"],
            "audiences": list(platform["audiences"]),
            "coreCapabilities": list(platform["coreCapabilities"]),
            "platformFeatures": list(platform["platformFeatures"]),
            "catalogBoundary": {
                "fixedAppCount": platform["catalogBoundary"]["fixedAppCount"],
                "growthModel": platform["catalogBoundary"]["growthModel"],
                "replacementAllowed": platform["catalogBoundary"]["replacementAllowed"],
                "routineExpansion": platform["catalogBoundary"]["routineExpansion"],
            },
            "visibility": "public",
        },
        "pages": pages,
        "categories": categories,
        "apps": apps,
        "relationships": [
            {
                "source": app["slug"],
                "target": related["slug"],
                "reason": related["reason"],
                "visibility": "public",
            }
            for app in apps
            for related in app["relatedApps"]
        ],
    }


def _jsonld_graph(knowledge: dict[str, Any]) -> dict[str, Any]:
    website_id = f"{SITE_URL}/#website"
    organization_id = f"{SITE_URL}/#organization"
    app_collection_id = f"{SITE_URL}/apps#collection"
    graph: list[dict[str, Any]] = [
        {
            "@type": "Organization",
            "@id": organization_id,
            "name": knowledge["platform"]["name"],
            "url": SITE_URL,
            "description": knowledge["platform"]["description"],
        },
        {
            "@type": "WebSite",
            "@id": website_id,
            "name": knowledge["platform"]["name"],
            "url": SITE_URL,
            "description": knowledge["platform"]["positioning"],
            "publisher": {"@id": organization_id},
        },
        {
            "@type": "CollectionPage",
            "@id": app_collection_id,
            "name": "Ansiversa Apps",
            "url": f"{SITE_URL}/apps",
            "description": "A public catalog of 100 curated Ansiversa solution apps.",
            "isPartOf": {"@id": website_id},
            "hasPart": [
                {"@id": f"{app['canonicalUrl']}#software"}
                for app in knowledge["apps"]
            ],
        },
        {
            "@type": "FAQPage",
            "@id": f"{SITE_URL}/faq#faq",
            "name": "Ansiversa FAQ",
            "url": f"{SITE_URL}/faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "What is Ansiversa?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": knowledge["platform"]["description"],
                    },
                },
                {
                    "@type": "Question",
                    "name": "How many apps does Ansiversa include?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Ansiversa is permanently curated at exactly 100 solution apps.",
                    },
                },
            ],
        },
    ]
    for app in knowledge["apps"]:
        graph.append(
            {
                "@type": "SoftwareApplication",
                "@id": f"{app['canonicalUrl']}#software",
                "name": app["name"],
                "applicationCategory": app["category"],
                "url": app["canonicalUrl"],
                "description": app["description"],
                "operatingSystem": "Web",
                "isPartOf": {"@id": app_collection_id},
                "keywords": app["aliases"],
                "audience": [
                    {"@type": "Audience", "audienceType": audience}
                    for audience in app["audiences"]
                ],
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def build_public_jsonld(knowledge: dict[str, Any]) -> dict[str, Any]:
    return _jsonld_graph(knowledge)


def build_public_metadata(knowledge: dict[str, Any]) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    base_keywords = ["Ansiversa", "100 apps", "solution apps", "productivity"]
    for page in knowledge["pages"]:
        pages.append(
            {
                "route": page["route"],
                "title": f"{page['name']} | Ansiversa",
                "description": page["summary"],
                "keywords": list(dict.fromkeys([*base_keywords, *page["aliases"]])),
                "canonical": page["canonicalUrl"],
                "openGraph": {
                    "title": f"{page['name']} | Ansiversa",
                    "description": page["summary"],
                    "url": page["canonicalUrl"],
                    "type": "website",
                },
                "twitter": {
                    "card": "summary",
                    "title": f"{page['name']} | Ansiversa",
                    "description": page["summary"],
                },
                "aiDescription": page["summary"],
                "visibility": "public",
            }
        )
    for app in knowledge["apps"]:
        keywords = list(dict.fromkeys([app["name"], app["category"], *app["aliases"], *app["capabilities"][:4]]))
        pages.append(
            {
                "route": app["route"],
                "title": f"{app['name']} | Ansiversa",
                "description": app["description"],
                "keywords": keywords,
                "canonical": app["canonicalUrl"],
                "openGraph": {
                    "title": f"{app['name']} | Ansiversa",
                    "description": app["description"],
                    "url": app["canonicalUrl"],
                    "type": "website",
                },
                "twitter": {
                    "card": "summary",
                    "title": f"{app['name']} | Ansiversa",
                    "description": app["description"],
                },
                "aiDescription": app["purpose"],
                "visibility": "public",
            }
        )
    return {
        "schemaVersion": PUBLIC_SCHEMA_VERSION,
        "generatedAt": PUBLIC_GENERATED_AT,
        "canonicalSource": "Canonical AI Knowledge Registry",
        "pages": pages,
    }


def build_llms_txt(knowledge: dict[str, Any]) -> str:
    lines = [
        "# Ansiversa",
        "",
        f"> {knowledge['platform']['description']}",
        "",
        knowledge["platform"]["positioning"],
        "",
        "## Core Resources",
        "",
        f"- [Home]({SITE_URL}): Ansiversa platform home.",
        f"- [Apps]({SITE_URL}/apps): Catalog of 100 curated solution apps.",
        f"- [Public AI Knowledge]({SITE_URL}/public-ai-knowledge.json): Machine-readable public knowledge export.",
        f"- [Full LLM Context]({SITE_URL}/llms-full.txt): Expanded public app and category context.",
        "",
        "## Categories",
        "",
    ]
    for category in knowledge["categories"]:
        lines.append(f"- {category['name']}")
    lines.extend(["", "## Public Pages", ""])
    for page in knowledge["pages"]:
        lines.append(f"- [{page['name']}]({page['canonicalUrl']}): {page['summary']}")
    lines.extend(["", "## Public Apps", ""])
    for app in knowledge["apps"]:
        lines.append(f"- [{app['name']}]({app['canonicalUrl']}): {app['description']}")
    lines.append("")
    return "\n".join(lines)


def build_llms_full_txt(knowledge: dict[str, Any]) -> str:
    lines = [
        "# Ansiversa Full Public AI Context",
        "",
        f"> {knowledge['platform']['description']}",
        "",
        f"Official description: {knowledge['platform']['positioning']}",
        f"Catalog size: {knowledge['platform']['appCount']} public solution apps.",
        "",
        "## Categories",
        "",
    ]
    for category in knowledge["categories"]:
        lines.append(f"- {category['name']} ({category['id']})")
    lines.extend(["", "## Public Pages", ""])
    for page in knowledge["pages"]:
        lines.extend([f"### {page['name']}", f"- URL: {page['canonicalUrl']}", f"- Summary: {page['summary']}", ""])
    lines.append("## Public Apps")
    lines.append("")
    by_slug = {app["slug"]: app for app in knowledge["apps"]}
    for app in knowledge["apps"]:
        related = [
            by_slug[item["slug"]]["name"]
            for item in app["relatedApps"]
            if item["slug"] in by_slug
        ]
        lines.extend(
            [
                f"### {app['name']}",
                f"- URL: {app['canonicalUrl']}",
                f"- Category: {app['category']}",
                f"- Purpose: {app['purpose']}",
                f"- Audience: {', '.join(app['audiences']) or 'General users'}",
                f"- Aliases: {', '.join(app['aliases'])}",
                f"- Capabilities: {'; '.join(app['capabilities'])}",
                f"- Related apps: {', '.join(related)}",
                "",
            ]
        )
    return "\n".join(lines)


def build_sitemap_xml(knowledge: dict[str, Any]) -> str:
    urls = [SITE_URL, f"{SITE_URL}/about", f"{SITE_URL}/pricing", f"{SITE_URL}/faq", f"{SITE_URL}/contact", f"{SITE_URL}/apps"]
    urls.extend(app["canonicalUrl"] for app in knowledge["apps"])
    urlset = ElementTree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        url_el = ElementTree.SubElement(urlset, "url")
        loc_el = ElementTree.SubElement(url_el, "loc")
        loc_el.text = url
        lastmod_el = ElementTree.SubElement(url_el, "lastmod")
        lastmod_el.text = PUBLIC_GENERATED_AT[:10]
    return ElementTree.tostring(urlset, encoding="unicode", xml_declaration=True)


def build_robots_txt() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {SITE_URL}/ai-sitemap.xml",
            f"LLMs: {SITE_URL}/llms.txt",
            "",
        ]
    )


def build_public_artifacts(registry: KnowledgeRegistry | None = None) -> PublicArtifacts:
    knowledge = build_public_knowledge(registry)
    return PublicArtifacts(
        knowledge=knowledge,
        jsonld=build_public_jsonld(knowledge),
        metadata=build_public_metadata(knowledge),
        sitemap=build_sitemap_xml(knowledge),
        llms=build_llms_txt(knowledge),
        llms_full=build_llms_full_txt(knowledge),
        robots=build_robots_txt(),
    )


def _serialized_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def write_public_artifacts(artifacts: PublicArtifacts | None = None) -> dict[str, Any]:
    artifacts = artifacts or build_public_artifacts()
    changed = {
        "public-ai-knowledge.json": _write_if_changed(PUBLIC_AI_KNOWLEDGE_PATH, _serialized_json(artifacts.knowledge)),
        "public-ai-jsonld.json": _write_if_changed(PUBLIC_AI_JSONLD_PATH, _serialized_json(artifacts.jsonld)),
        "public-ai-metadata.json": _write_if_changed(PUBLIC_AI_METADATA_PATH, _serialized_json(artifacts.metadata)),
        "ai-sitemap.xml": _write_if_changed(PUBLIC_AI_SITEMAP_PATH, artifacts.sitemap),
        "llms.txt": _write_if_changed(LLMS_PATH, artifacts.llms),
        "llms-full.txt": _write_if_changed(LLMS_FULL_PATH, artifacts.llms_full),
        "robots.txt": _write_if_changed(ROBOTS_PATH, artifacts.robots),
    }
    return {
        "changed": changed,
        "appCount": len(artifacts.knowledge["apps"]),
        "categoryCount": len(artifacts.knowledge["categories"]),
        "generatedAt": datetime.now(UTC).isoformat(),
    }


def validate_public_artifacts(artifacts: PublicArtifacts | None = None) -> None:
    artifacts = artifacts or build_public_artifacts()
    knowledge = artifacts.knowledge
    if len(knowledge["apps"]) != 100:
        raise ValueError(f"Expected 100 public apps, found {len(knowledge['apps'])}")
    if len(knowledge["categories"]) != 14:
        raise ValueError(f"Expected 14 public categories, found {len(knowledge['categories'])}")

    routes = [page["route"] for page in knowledge["pages"]] + [app["route"] for app in knowledge["apps"]]
    if len(routes) != len(set(routes)):
        raise ValueError("Duplicate public route detected")
    if any(not route.startswith("/") or route.startswith("//") for route in routes):
        raise ValueError("Invalid canonical route detected")
    if any(item["visibility"] != "public" for item in [*knowledge["apps"], *knowledge["pages"], *knowledge["categories"]]):
        raise ValueError("Hidden visibility record found in public export")
    if any(item.get("visibility") not in VISIBILITIES for item in [*knowledge["apps"], *knowledge["pages"], *knowledge["categories"]]):
        raise ValueError("Unknown visibility found in public export")

    json.loads(_serialized_json(knowledge))
    json.loads(_serialized_json(artifacts.jsonld))
    json.loads(_serialized_json(artifacts.metadata))
    ElementTree.fromstring(artifacts.sitemap)

    serialized = "\n".join(
        (
            _serialized_json(knowledge),
            _serialized_json(artifacts.jsonld),
            _serialized_json(artifacts.metadata),
            artifacts.sitemap,
            artifacts.llms,
            artifacts.llms_full,
            artifacts.robots,
        )
    )
    for label, pattern in FORBIDDEN_PUBLIC_PATTERNS.items():
        if pattern.search(serialized):
            raise ValueError(f"Forbidden public content detected: {label}")

    if "<loc>https://ansiversa.com/" not in artifacts.sitemap:
        raise ValueError("AI sitemap does not contain canonical Ansiversa URLs")
    if not artifacts.llms.startswith("# Ansiversa\n"):
        raise ValueError("llms.txt must start with the Ansiversa H1")
    if artifacts.jsonld.get("@context") != "https://schema.org":
        raise ValueError("JSON-LD schema context is invalid")
