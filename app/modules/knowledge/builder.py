"""Build and validate the deterministic Ansiversa knowledge registry."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 2
GENERATOR_VERSION = "1.1.0"
GENERATED_AT = "2026-07-21T00:00:00Z"
VISIBILITIES = {"public", "authenticated", "internal", "restricted"}
MAX_TEXT = 2_000
MAX_LIST = 12

BACKEND_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = BACKEND_ROOT.parent
FRONTEND_ROOT = WORKSPACE_ROOT / "ansiversa"
DATA_DIR = Path(__file__).resolve().parent / "data"
REGISTRY_PATH = DATA_DIR / "ansiversa-knowledge.json"
GAP_REPORT_PATH = DATA_DIR / "documentation-gaps.json"
FRONTEND_REGISTRY = FRONTEND_ROOT / "src/app/router/appOverviewRegistry.ts"
FRONTEND_SEARCH_INDEX = FRONTEND_ROOT / "src/shared/components/command-palette/searchIndex.ts"
OVERVIEW_DIR = BACKEND_ROOT / "app/modules/content/data/overview"

CATEGORY_ALIASES = {
    "learning": "Learning & Education",
    "career": "Career & Professional",
    "career & professional": "Career & Professional",
    "business": "Career & Professional",
    "writing": "Content & AI Writing",
    "content & ai writing": "Content & AI Writing",
    "utility": "Utilities & Productivity",
    "utilities": "Utilities & Productivity",
    "utilities & productivity": "Utilities & Productivity",
    "lifestyle": "Personal Life & Wellness",
    "personal life & wellness": "Personal Life & Wellness",
    "finance": "Personal Life & Wellness",
    "travel": "Personal Life & Wellness",
    "mobility & travel": "Mobility & Travel",
    "business & uae": "Business & UAE",
    "school records": "Business & UAE",
    "documents & records": "Documents & Records",
    "home & family": "Home & Family",
    "health & medical": "Health & Medical",
    "vehicle & driving": "Vehicle & Driving",
    "work & planning": "Work & Planning",
    "personal finance": "Personal Finance",
    "daily life": "Daily Life",
}

CATEGORY_IDS = {
    "Learning & Education": "cat_learning",
    "Career & Professional": "cat_career",
    "Content & AI Writing": "cat_writing",
    "Utilities & Productivity": "cat_utility",
    "Personal Life & Wellness": "cat_lifestyle",
}

EXPLICIT_ALIASES = {
    "salary-breakdown-calculator": ["salary", "pay", "income", "gross salary", "net salary", "allowance", "deduction"],
    "emi-loan-calculator": ["emi", "loan", "monthly payment"],
    "qr-code-creator": ["qr", "qr code"],
    "ai-notes-summarizer": ["summarize notes", "note summary"],
    "json-formatter": ["json validator", "format json"],
}

SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    "authorization": re.compile(r"authorization\s*:\s*bearer\s+\S+", re.I),
    "database-url": re.compile(r"(?:postgres(?:ql)?|mysql|libsql)://[^\s\"]+", re.I),
    "environment-secret": re.compile(r"(?:API_KEY|TOKEN|PASSWORD|DATABASE_URL)\s*=\s*[^\s\"]+", re.I),
}

HEADING_ALIASES = {
    "purpose": {"purpose", "product purpose", "final product vision"},
    "audience": {"audience", "who it is for", "target users", "intended audiences"},
    "problems": {"problem", "problems", "core user problems", "user problems"},
    "capabilities": {"current capabilities", "features", "current implementation"},
    "limitations": {"limitations", "non goals", "boundaries", "boundary"},
    "safety": {"safety", "safety notes"},
    "future": {"future direction", "future version ideas"},
    "use_cases": {"use cases", "common use cases", "journey"},
}


@dataclass(frozen=True)
class SourceRef:
    repository: str
    path: str
    section: str
    visibility: str = "public"

    def as_dict(self) -> dict[str, str]:
        return {"repository": self.repository, "path": self.path, "section": self.section, "visibility": self.visibility}


def _safe_path(path: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"Source escapes allowlisted root: {path}")
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root.parent):
        raise ValueError(f"Symlink sources are not allowed: {path}")
    return resolved


def _read_text(path: Path, root: Path, *, max_bytes: int = 300_000) -> str:
    safe = _safe_path(path, root)
    if safe.stat().st_size > max_bytes:
        raise ValueError(f"Source exceeds size limit: {path}")
    return safe.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def normalize_text(value: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", value, flags=re.S)
    value = re.sub(r"```.*?```", " ", value, flags=re.S)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", value)
    value = re.sub(r"^[\s>*#-]+", "", value, flags=re.M)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:MAX_TEXT]


def parse_markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^#{1,4}\s+(.+?)\s*$", line)
        if heading:
            normalized = normalize_text(heading.group(1)).lower()
            current = next((key for key, aliases in HEADING_ALIASES.items() if normalized in aliases), None)
            if current:
                sections.setdefault(current, [])
            continue
        if current and not line.lstrip().startswith("<!--"):
            sections[current].append(line)
    return {key: normalize_text("\n".join(lines)) for key, lines in sections.items() if normalize_text("\n".join(lines))}


def _slugify(value: str) -> str:
    value = value.lower().replace("&", " and ").replace("+", " plus ")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value)).strip("-")


def _category(raw_kicker: str) -> str:
    raw = re.split(r"Ansiversa\s+mini\s+app", raw_kicker, maxsplit=1, flags=re.I)[0]
    raw = re.sub(r"[^A-Za-z&]+$", "", raw).strip().lower()
    category = CATEGORY_ALIASES.get(raw)
    if not category:
        raise ValueError(f"Unknown overview category label: {raw_kicker}")
    return category


def _category_id(name: str) -> str:
    return CATEGORY_IDS.get(name, f"cat_{_slugify(name)}")


def _source_ref(path: Path, section: str, repository: str = "ansiversa-api") -> dict[str, str]:
    root = BACKEND_ROOT if repository == "ansiversa-api" else FRONTEND_ROOT
    return SourceRef(repository, path.resolve().relative_to(root.resolve()).as_posix(), section).as_dict()


def _frontend_apps() -> list[dict[str, str]]:
    text = _read_text(FRONTEND_REGISTRY, FRONTEND_ROOT)
    matches = re.findall(r'"slug":\s*"([^"]+)"\s*,\s*"name":\s*"([^"]+)"', text)
    return [{"slug": slug, "name": name} for slug, name in matches]


def _flatten_items(section: Any) -> list[str]:
    if not isinstance(section, dict):
        return []
    values: list[str] = []
    for item in section.get("items") or []:
        if isinstance(item, str):
            values.append(normalize_text(item))
        elif isinstance(item, dict):
            values.append(normalize_text(" — ".join(str(item.get(key, "")) for key in ("title", "description") if item.get(key))))
    return [value for value in values if value][:MAX_LIST]


def _aliases(name: str, slug: str, category: str) -> list[str]:
    candidates = [name, slug.replace("-", " "), category, *slug.split("-"), *EXPLICIT_ALIASES.get(slug, [])]
    result: list[str] = []
    for candidate in candidates:
        normalized = normalize_text(candidate).lower()
        if normalized and normalized not in result:
            result.append(normalized)
    return result[:16]


def _app_record(number: int, identity: dict[str, str]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    slug, name = identity["slug"], identity["name"]
    overview_path = OVERVIEW_DIR / f"{slug}.json"
    overview = json.loads(_read_text(overview_path, BACKEND_ROOT))
    hero = overview.get("hero") or {}
    category = _category(str(hero.get("kicker", "")))
    module_dir = BACKEND_ROOT / "app/modules" / slug.replace("-", "_")
    story_path, destination_path = module_dir / "story.md", module_dir / "destination.md"
    story_sections = parse_markdown_sections(_read_text(story_path, BACKEND_ROOT)) if story_path.exists() else {}
    destination_sections = parse_markdown_sections(_read_text(destination_path, BACKEND_ROOT)) if destination_path.exists() else {}
    purpose = normalize_text(str(hero.get("description") or story_sections.get("purpose") or "")) or None
    capabilities = [normalize_text(str(value)) for value in hero.get("points") or []]
    capabilities += _flatten_items(overview.get("resourceSection"))
    capabilities += _flatten_items(overview.get("technicalSection"))
    capabilities = list(dict.fromkeys(value for value in capabilities if value))[:MAX_LIST]
    problems = _flatten_items(overview.get("differences"))
    audiences = [normalize_text(str(item.get("title", ""))) for item in (overview.get("audiences") or {}).get("items") or [] if isinstance(item, dict)]
    use_cases = [normalize_text(str(step)) for step in (overview.get("flow") or {}).get("steps") or []]
    explore_route = ((hero.get("primaryAction") or {}).get("path") or f"/{slug}")
    future = destination_sections.get("future")
    limitations = [story_sections[key] for key in ("limitations",) if story_sections.get(key)]
    safety = [story_sections[key] for key in ("safety",) if story_sections.get(key)]
    refs = [_source_ref(FRONTEND_REGISTRY, "APP_OVERVIEW_APPS", "ansiversa"), _source_ref(overview_path, "hero")]
    if story_path.exists(): refs.append(_source_ref(story_path, "Current Implementation"))
    if future and destination_path.exists(): refs.append(_source_ref(destination_path, "Future Version Ideas"))
    gaps: list[dict[str, str]] = []
    for field, value, expected in (
        ("purpose", purpose, f"app/modules/content/data/overview/{slug}.json#hero.description"),
        ("intendedAudiences", audiences, f"app/modules/content/data/overview/{slug}.json#audiences"),
        ("currentCapabilities", capabilities, f"app/modules/content/data/overview/{slug}.json#hero.points"),
    ):
        if not value: gaps.append({"slug": slug, "field": field, "expectedSource": expected})
    record = {
        "number": number, "id": f"app_{slug}", "slug": slug, "name": name,
        "category": category, "categoryId": _category_id(category), "status": "active",
        "launchStatus": "live", "version": "1.0.0", "overviewRoute": f"/{slug}",
        "exploreRoute": explore_route, "purpose": purpose,
        "shortDescription": purpose, "currentCapabilities": capabilities,
        "problemsSolved": problems, "intendedAudiences": audiences,
        "commonUseCases": use_cases, "searchAliases": _aliases(name, slug, category),
        "searchPhrases": list(dict.fromkeys([*use_cases, *problems]))[:10],
        "relatedApps": [], "limitations": limitations, "safetyNotes": safety,
        "currentState": "live", "futureDirection": ({"state": "future", "summary": future} if future else None),
        "sourceReferences": refs, "visibility": "public",
    }
    return record, gaps


def _related_apps(apps: list[dict[str, Any]]) -> None:
    by_category: dict[str, list[dict[str, Any]]] = {}
    for app in apps: by_category.setdefault(app["categoryId"], []).append(app)
    for app in apps:
        peers = sorted((peer for peer in by_category[app["categoryId"]] if peer["slug"] != app["slug"]), key=lambda peer: (abs(peer["number"] - app["number"]), peer["number"]))
        app["relatedApps"] = [{"slug": peer["slug"], "reason": f"shared {app['category'].lower()} category"} for peer in peers[:3]]


def _platform_pages() -> list[dict[str, Any]]:
    specs = [("home", "/", "home.json"), ("about", "/about", "about.json"), ("apps", "/apps", "overview/apps.json"), ("pricing", "/pricing", "pricing.json"), ("privacy", "/privacy", "privacy.json"), ("terms", "/terms", "terms.json")]
    pages = []
    for key, route, relative in specs:
        path = BACKEND_ROOT / "app/modules/content/data" / relative
        data = json.loads(_read_text(path, BACKEND_ROOT))
        hero = data.get("hero") or {}
        summary = normalize_text(str(hero.get("description") or data.get("introduction") or "")) or None
        pages.append({"id": f"page_{key}", "name": str(hero.get("title") or key.title()), "route": route, "summary": summary, "searchAliases": [key], "sourceReferences": [_source_ref(path, "public metadata")], "visibility": "public"})
    search_text = _read_text(FRONTEND_SEARCH_INDEX, FRONTEND_ROOT)
    frontend_pages = (
        ("page-activity", "activity", "/activity", "Activity", ["activity", "timeline", "history"]),
        ("platform-ai-assistant", "ai-assistant", "/dashboard", "Ansiversa AI", ["ai assistant", "help"]),
        ("page-dashboard", "dashboard", "/dashboard", "Dashboard", ["dashboard", "home"]),
        ("page-faq", "faq", "/faq", "FAQ", ["faq", "help"]),
        ("page-contact", "contact", "/contact", "Contact", ["contact", "support", "help"]),
        ("account-profile", "profile", "/profile", "Profile", ["profile", "account"]),
        ("account-settings", "settings", "/settings", "Settings", ["settings", "preferences"]),
        ("account-subscription", "subscription", "/subscription", "Subscription", ["subscription", "billing", "plan"]),
        ("account-login", "login", "/login", "Login", ["login", "sign in"]),
        ("account-register", "register", "/register", "Register", ["register", "sign up", "create account"]),
    )
    existing_routes = {page["route"] for page in pages}
    existing_ids = {page["id"] for page in pages}
    for source_id, key, route, name, aliases in frontend_pages:
        if source_id in existing_ids:
            continue
        match = re.search(rf"id:\s*'{re.escape(source_id)}'.*?description:\s*'([^']+)'.*?searchText:\s*'([^']+)'", search_text, re.S)
        search_aliases = aliases
        if match:
            search_aliases = list(dict.fromkeys([*aliases, *normalize_text(match.group(2)).lower().split()]))
        if route in existing_routes and source_id.startswith("page-"):
            continue
        pages.append({"id": source_id.replace("-", "_"), "name": name, "route": route, "summary": normalize_text(match.group(1)) if match else None, "searchAliases": search_aliases[:12], "sourceReferences": [_source_ref(FRONTEND_SEARCH_INDEX, source_id, "ansiversa")], "visibility": "public"})
    return pages


def _platform_identity_knowledge() -> list[dict[str, Any]]:
    about_path = BACKEND_ROOT / "app/modules/content/data/about.json"
    ref = _source_ref(about_path, "approved public identity content")

    def record(
        identity_id: str,
        intents: list[str],
        aliases: list[str],
        answer: str,
        facts: list[str],
        actions: list[tuple[str, str]],
    ) -> dict[str, Any]:
        return {
            "id": identity_id,
            "visibility": "public",
            "questionIntents": intents,
            "aliases": aliases,
            "answer": answer,
            "facts": facts,
            "actions": [{"label": label, "route": route} for label, route in actions],
            "sourceReferences": [ref],
        }

    return [
        record("platform-meaning", ["what does ansiversa mean", "what is the full form of ansiversa"], ["ansiversa meaning", "full form"], "Ansiversa stands for Advanced Next-Gen Software Innovation and Versatility.", ["Advanced Next-Gen Software Innovation and Versatility"], [("Open About", "/about")]),
        record("platform-purpose", ["what is ansiversa", "what is ansiversa used for", "who is ansiversa for", "is ansiversa an app store", "what makes ansiversa different", "why was ansiversa created", "what problem does ansiversa solve", "what is the ansiversa ecosystem"], ["ansiversa identity", "platform purpose", "ansiversa ecosystem"], "Ansiversa is one consistent platform for exactly 100 curated solution apps across everyday life and work. It gives people one account, familiar navigation, and focused tools instead of a noisy, endlessly expanding app store.", ["exactly 100 curated solution apps", "one account", "consistent platform experience"], [("Open About", "/about"), ("Browse Apps", "/apps")]),
        record("platform-founder", ["who founded ansiversa", "who is the founder of ansiversa", "who is ansiversa founder", "who created ansiversa", "who designed ansiversa", "who is behind ansiversa", "is ansiversa built by a company or an individual"], ["founder", "creator", "architect"], "Ansiversa was founded and architected by Karthikeyan Ramalingam, Founder and Chief Architect. He leads the platform vision, architecture, quality, and product direction.", ["Karthikeyan Ramalingam", "Founder and Chief Architect"], [("Open About", "/about")]),
        record("platform-history", ["when was ansiversa started", "where was ansiversa created"], ["ansiversa history", "platform timeline"], "The idea for Ansiversa formed in late 2024, and its name, domain, and long-term mission were established in December 2024. Ansiversa's public information does not specify a creation location.", ["late 2024", "December 2024", "creation location is not publicly specified"], [("Open About", "/about")]),
        record("platform-owner", ["who owns ansiversa"], ["owner", "legal license holder"], "Ansila Adamkutty is the official owner and legal license holder of Ansiversa, with responsibility for governance, registrations, and formal representation.", ["Ansila Adamkutty", "official owner and legal license holder"], [("Open About", "/about")]),
        record("platform-operator", ["who operates ansiversa"], ["operator", "operating entity"], "Ansiversa's public information identifies its founder and architect and its official owner and legal license holder, but it does not publish a separate operating entity.", ["no separate operating entity is published"], [("Open About", "/about"), ("Open Contact", "/contact")]),
        record("astra-identity", ["who is astra", "what is astra", "are you astra", "is astra an ai", "what can astra do", "what can you help me with", "does astra know all ansiversa apps", "can astra open apps for me"], ["astra", "ai assistant", "assistant identity"], "Astra is Ansiversa's built-in AI assistant. I help users understand the platform, discover and compare relevant apps, and open validated destinations across its fixed ecosystem of 100 apps. My answers are grounded in Ansiversa's canonical public knowledge.", ["built-in AI assistant", "canonical public knowledge", "validated destinations"], [("Browse Apps", "/apps"), ("Open About", "/about")]),
        record("astra-provider", ["are you chatgpt", "which ai powers astra"], ["astra model", "ai provider", "chatgpt"], "I am Astra, Ansiversa's built-in AI assistant. Ansiversa does not publish Astra's underlying model or provider configuration; my role is to provide grounded platform guidance from approved public knowledge.", ["underlying model and provider configuration are not public"], [("Open About", "/about")]),
        record("fixed-catalog", ["why exactly 100 apps", "why only 100 apps", "will ansiversa add more apps", "will there be app 101", "will there be app #101", "what happens after 100 apps", "what does horizontal improvement mean", "why not keep adding apps", "is the catalog permanent", "how does ansiversa grow", "can apps be replaced"], ["exactly 100", "app 101", "horizontal improvement", "fixed catalog"], "Ansiversa is permanently curated at exactly 100 apps, so there is no routine App #101. Growth is horizontal: shared quality, accessibility, performance, search, security, AI integration, and user experience improve across the ecosystem. An app may be replaced if it is unpopular, unused, or no longer provides enough value, while the total remains 100.", ["exactly 100 apps", "no routine App #101", "horizontal improvement", "replacement may occur while total remains 100"], [("Open About", "/about"), ("Browse Apps", "/apps")]),
        record("platform-account", ["can i use one account for all apps"], ["one account", "shared account"], "Yes. Ansiversa is designed around one account for its fixed ecosystem of 100 apps.", ["one account for 100 apps"], [("Open About", "/about"), ("Open Login", "/login")]),
        record("platform-categories", ["are all 100 apps live", "do the apps share the same design"], ["live apps", "shared design"], "Ansiversa has 100 live apps organized across 14 public app categories. The apps use a consistent platform design language and shared experience standards.", ["100 live apps", "14 public app categories", "consistent design language"], [("Browse Apps", "/apps"), ("Open About", "/about")]),
        record("platform-data", ["does each app have a separate database", "is my data private", "does ansiversa store everything centrally"], ["data architecture", "privacy", "separate database"], "Ansiversa uses clear ownership boundaries for platform and app data rather than treating everything as one central record store. Public privacy details are available in the Privacy Policy; sensitive infrastructure details are not disclosed.", ["clear data ownership boundaries", "high-level public security wording"], [("Open Privacy", "/privacy"), ("Open Terms", "/terms")]),
        record("creator-program", ["what is the creator program", "can creators build apps for ansiversa"], ["creators", "developers", "creator program"], "Ansiversa is designed to give creators and developers a consistent foundation for improving useful products within clear architecture and experience standards. Public information currently describes carefully supported creator contributions, not an open marketplace or unrestricted app expansion.", ["supported creator contributions", "fixed 100-app boundary remains"], [("Open About", "/about"), ("Open Contact", "/contact")]),
        record("open-source", ["is ansiversa open source"], ["open source", "source code"], "Ansiversa's public platform information does not state that the platform is open source.", ["open-source status is not publicly stated"], [("Open About", "/about")]),
    ]


def _digest(paths: Iterable[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.resolve().relative_to(root.resolve()).as_posix().encode())
        digest.update(_read_text(path, root).encode())
    return digest.hexdigest()


def source_files() -> tuple[list[Path], list[Path]]:
    backend = sorted(OVERVIEW_DIR.glob("*.json")) + sorted((BACKEND_ROOT / "app/modules").glob("*/story.md")) + sorted((BACKEND_ROOT / "app/modules").glob("*/destination.md"))
    backend += [BACKEND_ROOT / "story.md"]
    backend += [BACKEND_ROOT / "app/modules/content/data" / name for name in ("home.json", "about.json", "pricing.json", "privacy.json", "terms.json")]
    return list(dict.fromkeys(path for path in backend if path.exists())), [FRONTEND_REGISTRY, FRONTEND_SEARCH_INDEX]


def build_registry() -> tuple[dict[str, Any], list[dict[str, str]]]:
    identities = _frontend_apps()
    apps, gaps = [], []
    for number, identity in enumerate(identities, 1):
        app, app_gaps = _app_record(number, identity); apps.append(app); gaps.extend(app_gaps)
    _related_apps(apps)
    locked_catalog_source = WORKSPACE_ROOT.parent / "approved-apps.md"
    if not locked_catalog_source.exists():
        gaps.append({"slug": "platform", "field": "lockedCatalogSource", "expectedSource": "approved-apps.md"})
    categories = [{"id": category_id, "name": name, "visibility": "public"} for name, category_id in sorted({app["category"]: app["categoryId"] for app in apps}.items())]
    backend_sources, frontend_sources = source_files()
    registry = {
        "schemaVersion": SCHEMA_VERSION, "generatedAt": GENERATED_AT, "generatorVersion": GENERATOR_VERSION,
        "sourceRevision": {"backend": f"sha256:{_digest(backend_sources, BACKEND_ROOT)}", "frontend": f"sha256:{_digest(frontend_sources, FRONTEND_ROOT)}"},
        "platform": {"name": "Ansiversa", "shortName": "Ansiversa", "canonicalUrl": "https://ansiversa.com", "purpose": "One consistent platform for focused everyday solution apps.", "positioning": "A permanently curated ecosystem of exactly 100 solution apps.", "tagline": "One account. 100 curated apps.", "catalogBoundary": {"fixedAppCount": 100, "growthModel": "horizontal", "replacementAllowed": True, "routineExpansion": False}, "appCount": 100, "categoryCount": len(categories), "audiences": ["individuals", "professionals", "families"], "coreCapabilities": ["app discovery", "shared account", "personal dashboard", "global search", "AI-assisted guidance"], "platformFeatures": ["Favorites", "Recent Apps", "Notifications", "Activity Timeline", "Ansiversa AI"], "navigationDestinations": [page["route"] for page in _platform_pages()], "publicPolicies": ["/privacy", "/terms"], "searchAliases": ["ansiversa", "100 apps", "solution apps"], "sourceReferences": [_source_ref(BACKEND_ROOT / "story.md", "Platform story")], "visibility": "public"},
        "pages": _platform_pages(), "platformIdentityKnowledge": _platform_identity_knowledge(), "categories": categories, "apps": apps,
        "validation": {"appCount": len(apps), "categoryCount": len(categories), "warningCount": len(gaps), "errorCount": 0},
    }
    validate_registry(registry)
    return registry, gaps


def validate_registry(registry: dict[str, Any]) -> None:
    apps = registry.get("apps") or []
    identities = registry.get("platformIdentityKnowledge") or []
    if not identities: raise ValueError("Platform identity knowledge is required")
    if len({item["id"] for item in identities}) != len(identities): raise ValueError("Duplicate platform identity id")
    for item in identities:
        if item.get("visibility") != "public": raise ValueError("Platform identity knowledge must be public")
        if not item.get("questionIntents") or not item.get("answer") or not item.get("sourceReferences"): raise ValueError("Incomplete platform identity record")
    if len(apps) != 100: raise ValueError(f"Expected exactly 100 apps, found {len(apps)}")
    for field in ("number", "id", "slug", "overviewRoute"):
        values = [app[field] for app in apps]
        if len(values) != len(set(values)): raise ValueError(f"Duplicate app {field}")
    if sorted(app["number"] for app in apps) != list(range(1, 101)): raise ValueError("App numbers must be 1 through 100")
    slugs = {app["slug"] for app in apps}; expected_slugs = {app["slug"] for app in _frontend_apps()}
    if slugs != expected_slugs: raise ValueError("Registry contains an unknown or missing app")
    category_ids = {category["id"] for category in registry["categories"]}
    for app in apps:
        if app["number"] == 101 or app["slug"] == "app-101": raise ValueError("App #101 is prohibited")
        if app["status"] == "active" and app["launchStatus"] == "live" and not re.fullmatch(r"\d+\.\d+\.\d+", app["version"]): raise ValueError(f"Invalid live version: {app['slug']}")
        if app["categoryId"] not in category_ids: raise ValueError(f"Invalid category: {app['slug']}")
        if app["overviewRoute"] != f"/{app['slug']}" or not app["exploreRoute"].startswith(f"/{app['slug']}"): raise ValueError(f"Invalid canonical route: {app['slug']}")
        if app["visibility"] not in VISIBILITIES: raise ValueError(f"Invalid visibility: {app['slug']}")
        for related in app["relatedApps"]:
            if related["slug"] == app["slug"] or related["slug"] not in slugs: raise ValueError(f"Invalid relationship: {app['slug']}")
        if app["futureDirection"] and app["futureDirection"].get("state") != "future": raise ValueError(f"Future state is ambiguous: {app['slug']}")
        for source in app["sourceReferences"]:
            if source.get("repository") not in {"ansiversa", "ansiversa-api"} or source.get("visibility") not in VISIBILITIES:
                raise ValueError(f"Invalid source reference: {app['slug']}")
            if ".." in Path(source.get("path", "")).parts or Path(source.get("path", "")).is_absolute():
                raise ValueError(f"Source is not allowlisted: {app['slug']}")
        for value in [app.get("purpose") or "", *app["currentCapabilities"], *app["problemsSolved"], *app["commonUseCases"]]:
            if len(value) > MAX_TEXT: raise ValueError(f"Generated text exceeds length bound: {app['slug']}")
    serialized = json.dumps(registry, ensure_ascii=False)
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(serialized): raise ValueError(f"Restricted pattern detected: {label}")


def serialized_registry(registry: dict[str, Any]) -> str:
    return json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
