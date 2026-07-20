from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Literal, Protocol

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.assistant.openai_provider import OpenAIResponseProvider
from app.modules.assistant.schemas import (
    AssistantAction,
    AssistantClientContext,
    AssistantQueryResponse,
    AssistantSource,
)
from app.modules.faqs.models import Faq
from app.modules.knowledge.registry import KnowledgeRegistry

SourceType = Literal["app", "platform", "account", "legal", "faq"]
ActionType = Literal["app", "platform", "account", "legal"]

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
OVERVIEW_DATA_DIR = Path(__file__).resolve().parents[1] / "content" / "data" / "overview"
LOGGER = logging.getLogger(__name__)
PHRASE_STOPWORDS = {"a", "an", "and", "for", "in", "of", "on", "or", "the", "to"}
ALIAS_PHRASE_STOPWORDS = PHRASE_STOPWORDS | {"app", "apps", "help", "question", "questions", "support"}
COLLECTION_QUERY_TERMS = {
    "all",
    "apps",
    "app",
    "have",
    "many",
    "show",
    "list",
    "find",
    "which",
    "what",
    "with",
    "for",
    "help",
    "helps",
    "need",
    "you",
    "do",
    "does",
    "ansiversa",
}
CATEGORY_ALIASES: dict[str, tuple[str, ...]] = {
    "Business & UAE": ("business", "uae", "tax", "vat", "corporate"),
    "Career & Professional": ("career", "professional", "job", "resume", "interview", "portfolio", "linkedin"),
    "Content & AI Writing": ("content", "writing", "ai writing", "email", "grammar", "caption", "speech", "proposal", "prompt"),
    "Daily Life": ("daily", "errand", "checklist", "reminder"),
    "Documents & Records": ("document", "documents", "records", "vault", "expiry", "passport"),
    "Health & Medical": ("health", "medical", "medicine", "symptom", "hydration", "vaccination"),
    "Home & Family": ("home", "family", "household", "meal"),
    "Learning & Education": ("learning", "education", "course", "courses", "study", "lesson", "quiz", "textbook", "language"),
    "Mobility & Travel": ("mobility", "travel", "trip", "itinerary", "parking", "car pool", "rent"),
    "Personal Finance": ("personal finance", "money", "finance", "financial", "budget", "budgeting", "expense", "savings", "bill", "salary", "net worth"),
    "Personal Life & Wellness": ("personal life", "wellness", "goal", "birthday", "anniversary"),
    "Utilities & Productivity": ("utility", "utilities", "productivity", "tool", "formatter", "scanner"),
    "Vehicle & Driving": ("vehicle", "driving", "driver", "fuel", "car", "maintenance"),
    "Work & Planning": ("work", "planning", "project", "task", "shift", "meeting", "decision", "schedule"),
}
RESTRICTED_REQUEST_TERMS = {
    "agents md",
    "agent md",
    "story md",
    "certification",
    "promotion",
    "internal notes",
    "system prompt",
    "developer message",
    "hidden",
    "secret",
    "private data",
    "authenticated data",
}
PROMPT_INJECTION_TERMS = {
    "ignore instructions",
    "ignore previous",
    "disregard instructions",
    "reveal prompt",
    "show prompt",
    "print prompt",
}
PROFESSIONAL_BOUNDARY_TERMS: dict[str, tuple[str, ...]] = {
    "medical": ("diagnosis", "diagnose", "treatment", "prescribe", "dosage", "dose advice", "medical advice"),
    "legal": ("legal advice", "lawsuit", "sue", "contract advice"),
}


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    title: str
    source_type: SourceType
    route: str
    summary: str
    catalog_id: str | None = None
    app_key: str | None = None
    category: str | None = None
    aliases: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    action_label: str | None = None
    action_type: ActionType | None = None
    visibility: str = "public"
    rank_weight: int = 0
    related_app_slugs: tuple[str, ...] = ()
    future_summary: str | None = None


@dataclass(frozen=True)
class RankedEntry:
    entry: KnowledgeEntry
    score: int
    reason: str


@dataclass(frozen=True)
class AssistantKnowledgeIndex:
    entries: tuple[KnowledgeEntry, ...]
    allowed_routes: frozenset[str]


@dataclass(frozen=True)
class DeterministicAssistantResult:
    answer: str
    actions: list[AssistantAction]
    sources: list[AssistantSource]
    confidence: Literal["high", "medium", "low"]
    top_entries: tuple[KnowledgeEntry, ...]

    def to_response(
        self,
        *,
        answer: str | None = None,
        response_mode: Literal["deterministic", "openai_grounded", "fallback"] = "deterministic",
    ) -> AssistantQueryResponse:
        return AssistantQueryResponse(
            answer=answer or self.answer,
            actions=self.actions,
            sources=self.sources,
            confidence=self.confidence,
            response_mode=response_mode,
        )


class AssistantAnswerProvider(Protocol):
    def generate_answer(self, question: str, context: str) -> str | None:
        ...


APP_ALIASES: dict[str, tuple[str, ...]] = {
    "bill-splitter": ("bill", "split bills", "shared expenses"),
    "document-expiry-tracker": ("passport", "visa expiry", "id expiry", "licence expiry", "renewal dates"),
    "digital-document-vault": ("documents", "vault", "document storage"),
    "emergency-checklist": ("emergency list", "preparedness checklist"),
    "errand-planner": ("errands", "todo errands", "outside tasks"),
    "local-services-finder": ("services", "provider", "local provider"),
    "meeting-scheduler": ("meeting", "schedule meeting", "participants", "agenda"),
    "net-worth-tracker": ("net worth", "assets", "liabilities", "snapshot"),
    "salary-breakdown-calculator": ("salary", "pay", "net pay", "gross salary", "deductions"),
    "savings-goal-planner": ("savings", "saving goal", "money goal"),
    "shift-planner": ("shift", "schedule shifts", "staff schedule"),
    "work-log-tracker": ("work log", "timesheet", "billable hours"),
}

PLATFORM_ENTRIES: tuple[KnowledgeEntry, ...] = (
    KnowledgeEntry(
        id="platform:dashboard",
        title="Dashboard",
        source_type="platform",
        route="/dashboard",
        summary="Dashboard is your personal starting point for favorites, recent apps, suggested apps, quick actions, and account context.",
        aliases=("home dashboard", "personal dashboard"),
        keywords=("dashboard", "favorites", "recent apps", "quick actions"),
        action_label="Open Dashboard",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="platform:apps",
        title="Apps",
        source_type="platform",
        route="/apps",
        summary="Apps is the complete catalog of 100 carefully curated Ansiversa solution apps.",
        aliases=("catalog", "browse apps", "explore apps"),
        keywords=("apps", "catalog", "search apps", "category"),
        action_label="Browse Apps",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="platform:about",
        title="About",
        source_type="platform",
        route="/about",
        summary="About explains the Ansiversa story, platform principles, people, and fixed 100-app ecosystem.",
        aliases=("what is ansiversa", "ansiversa story"),
        keywords=("about", "ansiversa", "platform", "ecosystem"),
        action_label="Open About",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="platform:pricing",
        title="Pricing",
        source_type="platform",
        route="/pricing",
        summary="Pricing explains Ansiversa plans, platform access, and subscription options.",
        aliases=("price", "plans", "cost", "subscription pricing"),
        keywords=("pricing", "plan", "subscription", "billing"),
        action_label="Open Pricing",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="platform:faq",
        title="FAQ",
        source_type="platform",
        route="/faq",
        summary="FAQ answers common questions about Ansiversa, accounts, apps, access, and support.",
        aliases=("frequently asked", "questions", "help"),
        keywords=("faq", "help", "question", "support"),
        action_label="Open FAQ",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="platform:contact",
        title="Contact",
        source_type="platform",
        route="/contact",
        summary="Contact is where users can reach Ansiversa for platform questions and support.",
        aliases=("support", "contact us"),
        keywords=("contact", "support", "message"),
        action_label="Open Contact",
        action_type="platform",
        rank_weight=3,
    ),
    KnowledgeEntry(
        id="account:profile",
        title="Profile",
        source_type="account",
        route="/profile",
        summary="Profile lets signed-in users review and manage account identity.",
        aliases=("account", "my account"),
        keywords=("profile", "account", "identity"),
        action_label="Open Profile",
        action_type="account",
        rank_weight=2,
    ),
    KnowledgeEntry(
        id="account:settings",
        title="Settings",
        source_type="account",
        route="/settings",
        summary="Settings contains account preferences and platform settings.",
        aliases=("preferences",),
        keywords=("settings", "preferences"),
        action_label="Open Settings",
        action_type="account",
        rank_weight=2,
    ),
    KnowledgeEntry(
        id="account:subscription",
        title="Subscription",
        source_type="account",
        route="/subscription",
        summary="Subscription is where signed-in users review plan and billing-related account information.",
        aliases=("billing", "plan"),
        keywords=("subscription", "billing", "plan"),
        action_label="Open Subscription",
        action_type="account",
        rank_weight=2,
    ),
    KnowledgeEntry(
        id="platform:login",
        title="Login",
        source_type="platform",
        route="/login",
        summary="Login is the sign-in page for existing Ansiversa users.",
        aliases=("sign in", "signin"),
        keywords=("login", "sign in"),
        action_label="Open Login",
        action_type="platform",
        rank_weight=1,
    ),
    KnowledgeEntry(
        id="platform:register",
        title="Register",
        source_type="platform",
        route="/register",
        summary="Register is where new users create an Ansiversa account.",
        aliases=("sign up", "signup", "create account"),
        keywords=("register", "sign up"),
        action_label="Open Register",
        action_type="platform",
        rank_weight=1,
    ),
    KnowledgeEntry(
        id="legal:privacy",
        title="Privacy Policy",
        source_type="legal",
        route="/privacy",
        summary="Privacy Policy explains Ansiversa data-use and privacy rules.",
        aliases=("privacy", "data policy"),
        keywords=("privacy", "data", "policy"),
        action_label="Open Privacy",
        action_type="legal",
        rank_weight=2,
    ),
    KnowledgeEntry(
        id="legal:terms",
        title="Terms of Service",
        source_type="legal",
        route="/terms",
        summary="Terms of Service explains the rules for using Ansiversa.",
        aliases=("terms", "terms and conditions", "legal"),
        keywords=("terms", "legal", "service"),
        action_label="Open Terms",
        action_type="legal",
        rank_weight=2,
    ),
)

FALLBACK_ACTIONS: tuple[AssistantAction, ...] = (
    AssistantAction(type="platform", label="Browse Apps", route="/apps"),
    AssistantAction(type="platform", label="Open FAQ", route="/faq"),
)

FINANCIAL_GUIDANCE_ACTIONS: tuple[AssistantAction, ...] = (
    AssistantAction(type="app", label="Open Salary Breakdown Calculator", route="/salary-breakdown-calculator"),
    AssistantAction(type="app", label="Open Savings Goal Planner", route="/savings-goal-planner"),
    AssistantAction(type="app", label="Open Expense Tracker", route="/expense-tracker"),
)

NAVIGATION_INTENTS = {
    "open",
    "go",
    "show",
    "find",
    "launch",
    "take",
    "browse",
}

BACK_NAVIGATION_TERMS = {
    "go back",
    "take me back",
    "back to it",
    "back to that app",
    "return to it",
    "return to that app",
}

RECENT_REFERENCE_TERMS = {
    "using something",
    "used something",
    "something yesterday",
    "recent app",
    "recent apps",
    "what was i using",
    "what did i use",
}

CURRENT_APP_CREATE_TERMS = {
    "add one",
    "create one",
    "make one",
    "new one",
    "add this",
    "create this",
}

FINANCIAL_ADVICE_TERMS = {
    "financial advice",
    "finance advice",
    "investment advice",
    "money advice",
    "advise me financially",
}

OUT_OF_SCOPE_TERMS = {
    "not in ansiversa",
    "outside ansiversa",
    "not part of ansiversa",
    "something else",
    "unrelated to ansiversa",
}

RELATED_APP_TERMS = {
    "similar",
    "related",
    "alternative",
    "alternatives",
    "like",
}

FUTURE_TERMS = {
    "future",
    "planned",
    "plans",
    "roadmap",
    "coming",
    "next",
}


def normalize_text(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.lower()))


def tokenize(value: str) -> set[str]:
    tokens = set(normalize_text(value).split())
    expanded = set(tokens)
    for token in tokens:
        if len(token) > 3 and token.endswith("ies"):
            expanded.add(f"{token[:-3]}y")
        elif len(token) > 3 and token.endswith("s"):
            expanded.add(token[:-1])
    return expanded


def _extract_overview_route(app_slug: str) -> str | None:
    path = OVERVIEW_DATA_DIR / f"{app_slug}.json"
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    candidates = [
        data.get("hero", {}).get("primaryAction", {}).get("path"),
        data.get("finalCta", {}).get("action", {}).get("path"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith(f"/{app_slug}"):
            return candidate

    return None


def _build_app_entries(db: Session) -> tuple[KnowledgeEntry, ...]:
    statement = (
        select(
            AppCatalogItem.slug,
            AppCatalogItem.id,
            AppCatalogItem.key,
            AppCatalogItem.name,
            AppCatalogItem.description,
            AppCatalogItem.status,
            AppCatalogItem.launch_status,
            Category.name.label("category_name"),
        )
        .join(Category, AppCatalogItem.category_id == Category.id)
        .where(
            and_(
                AppCatalogItem.visibility == "public",
                AppCatalogItem.status == "active",
            )
        )
        .order_by(AppCatalogItem.name.asc())
    )
    entries: list[KnowledgeEntry] = []
    for row in db.execute(statement).mappings().all():
        slug = str(row["slug"])
        overview_route = _extract_overview_route(slug)
        route = overview_route or f"/{slug}"
        entries.append(
            KnowledgeEntry(
                id=f"app:{slug}",
                title=str(row["name"]),
                source_type="app",
                route=route,
                summary=str(row["description"]),
                catalog_id=str(row["id"]),
                app_key=str(row["key"]),
                category=str(row["category_name"]),
                aliases=APP_ALIASES.get(slug, ()),
                keywords=(
                    slug.replace("-", " "),
                    str(row["key"]),
                    str(row["category_name"]),
                    str(row["launch_status"]),
                ),
                action_label=f"Open {row['name']}",
                action_type="app",
                rank_weight=5 if row["launch_status"] == "live" else 1,
            )
        )

    return tuple(entries)


def _build_faq_entries(db: Session) -> tuple[KnowledgeEntry, ...]:
    statement = (
        select(Faq.id, Faq.question, Faq.answer)
        .where(
            and_(
                Faq.is_published.is_(True),
                Faq.audience == "user",
                Faq.app_key.is_(None),
            )
        )
        .order_by(Faq.sort_order.asc(), Faq.created_at.desc())
        .limit(12)
    )
    entries: list[KnowledgeEntry] = []
    for row in db.execute(statement).mappings().all():
        entries.append(
            KnowledgeEntry(
                id=f"faq:{row['id']}",
                title=str(row["question"]),
                source_type="faq",
                route="/faq",
                summary=str(row["answer"]),
                keywords=("faq", "question", "help"),
                action_label="Open FAQ",
                action_type="platform",
                rank_weight=1,
            )
        )

    return tuple(entries)


def build_legacy_knowledge_index(db: Session) -> AssistantKnowledgeIndex:
    entries = (*_build_app_entries(db), *PLATFORM_ENTRIES, *_build_faq_entries(db))
    public_entries = tuple(entry for entry in entries if entry.visibility == "public")
    allowed_routes = frozenset({entry.route for entry in public_entries} | {"/apps", "/faq"})

    return AssistantKnowledgeIndex(entries=public_entries, allowed_routes=allowed_routes)


def _registry_page_summary(page: dict[str, object]) -> str:
    summary = page.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    name = str(page.get("name") or "This page")
    route = str(page.get("route") or "")
    fallback_by_route = {
        "/about": "About explains Ansiversa as one platform with one account, one navigation system, and a fixed 100-app ecosystem.",
        "/apps": "Apps is the complete catalog of 100 carefully curated Ansiversa solution apps.",
        "/privacy": "Privacy explains Ansiversa data-use and privacy rules.",
        "/terms": "Terms explains the rules for using Ansiversa.",
        "/faq": "FAQ answers common questions about Ansiversa, accounts, apps, access, and support.",
        "/contact": "Contact is where users can reach Ansiversa for platform questions and support.",
    }
    return fallback_by_route.get(route, f"{name} is an Ansiversa platform page.")


def _registry_action_type_for_route(route: str) -> ActionType:
    if route in {"/privacy", "/terms"}:
        return "legal"
    if route in {"/profile", "/settings", "/subscription"}:
        return "account"
    return "platform"


def _registry_action_label(name: str, action_type: ActionType) -> str:
    if action_type == "legal":
        return f"Open {name}"
    if name.lower().startswith("one subscription"):
        return "Open Pricing"
    if name.lower().startswith("100 carefully"):
        return "Open Home"
    return f"Open {name}"


def _registry_app_entry(app: dict[str, object]) -> KnowledgeEntry:
    slug = str(app["slug"])
    name = str(app["name"])
    category = str(app["category"])
    capabilities = tuple(str(value) for value in app.get("currentCapabilities") or ())
    problems = tuple(str(value) for value in app.get("problemsSolved") or ())
    use_cases = tuple(str(value) for value in app.get("commonUseCases") or ())
    phrases = tuple(str(value) for value in app.get("searchPhrases") or ())
    aliases = tuple(str(value) for value in app.get("searchAliases") or ())
    future = app.get("futureDirection")
    future_summary = (
        str(future.get("summary"))
        if isinstance(future, dict) and isinstance(future.get("summary"), str)
        else None
    )
    related = tuple(
        str(item["slug"])
        for item in app.get("relatedApps") or ()
        if isinstance(item, dict) and isinstance(item.get("slug"), str)
    )

    return KnowledgeEntry(
        id=f"app:{slug}",
        title=name,
        source_type="app",
        route=str(app.get("exploreRoute") or app.get("overviewRoute") or f"/{slug}"),
        summary=str(app.get("shortDescription") or app.get("purpose") or ""),
        catalog_id=str(app.get("id") or ""),
        app_key=slug,
        category=category,
        aliases=aliases,
        keywords=(
            slug.replace("-", " "),
            category,
            str(app.get("categoryId") or ""),
            str(app.get("currentState") or ""),
            *capabilities,
            *problems,
            *use_cases,
            *phrases,
        ),
        action_label=f"Open {name}",
        action_type="app",
        visibility=str(app.get("visibility") or "public"),
        rank_weight=5 if app.get("launchStatus") == "live" else 1,
        related_app_slugs=related,
        future_summary=future_summary,
    )


def _registry_page_entry(page: dict[str, object]) -> KnowledgeEntry:
    route = str(page.get("route") or "/")
    name = str(page.get("name") or "Ansiversa")
    action_type = _registry_action_type_for_route(route)
    source_type: SourceType = action_type if action_type in {"account", "legal"} else "platform"
    aliases = tuple(str(value) for value in page.get("searchAliases") or ())
    raw_id = str(page.get("id") or f"page:{route}")
    if raw_id.startswith("page_"):
        entry_id = raw_id.replace("page_", "platform:", 1)
    elif raw_id.startswith("account_"):
        entry_id = raw_id.replace("account_", "account:", 1)
    elif raw_id.startswith("legal_"):
        entry_id = raw_id.replace("legal_", "legal:", 1)
    elif raw_id.startswith("platform_"):
        entry_id = raw_id.replace("platform_", "platform:", 1)
    else:
        entry_id = raw_id

    return KnowledgeEntry(
        id=entry_id,
        title=name,
        source_type=source_type,
        route=route,
        summary=_registry_page_summary(page),
        aliases=aliases,
        keywords=(route.strip("/") or "home", name, *aliases),
        action_label=_registry_action_label(name, action_type),
        action_type=action_type,
        visibility=str(page.get("visibility") or "public"),
        rank_weight=3,
    )


def _registry_platform_entry(registry: KnowledgeRegistry) -> KnowledgeEntry:
    platform = registry.data["platform"]
    boundary = platform["catalogBoundary"]
    fixed_count = int(platform["appCount"])
    summary = (
        f"{platform['name']} is {platform['purpose']} It is {platform['positioning']} "
        f"Users use one account across {fixed_count} curated solution apps. "
        f"The catalog is permanently limited to {boundary['fixedAppCount']} apps, "
        f"with horizontal improvement and replacement allowed instead of routine expansion."
    )
    return KnowledgeEntry(
        id="platform:ansiversa",
        title=str(platform["name"]),
        source_type="platform",
        route="/about",
        summary=summary,
        aliases=tuple(str(value) for value in platform.get("searchAliases") or ())
        + ("what is ansiversa", "how many apps", "why only 100 apps", "one account"),
        keywords=(
            str(platform["shortName"]),
            str(platform["tagline"]),
            *[str(value) for value in platform.get("coreCapabilities") or ()],
            *[str(value) for value in platform.get("platformFeatures") or ()],
            "fixed 100 app catalog",
            "one login",
            "one account",
        ),
        action_label="Open About",
        action_type="platform",
        visibility=str(platform.get("visibility") or "public"),
        rank_weight=4,
    )


def build_registry_knowledge_index(
    *,
    allowed_visibility: set[str] | None = None,
) -> AssistantKnowledgeIndex:
    registry = KnowledgeRegistry.load()
    allowed = allowed_visibility or {"public"}
    apps = registry.apps(allowed)
    pages = registry.pages(allowed)
    entries = (
        *[_registry_app_entry(app) for app in apps],
        *[_registry_page_entry(page) for page in pages],
        _registry_platform_entry(registry),
    )
    visible_entries = tuple(entry for entry in entries if entry.visibility in allowed)
    allowed_routes = frozenset(
        {
            entry.route
            for entry in visible_entries
            if entry.route.startswith("/") and not entry.route.startswith("//")
        }
        | {"/apps", "/faq"}
    )
    return AssistantKnowledgeIndex(entries=visible_entries, allowed_routes=allowed_routes)


def build_knowledge_index(db: Session | None = None) -> AssistantKnowledgeIndex:
    return build_registry_knowledge_index()


def _entry_matches_context_app(entry: KnowledgeEntry, context_app: object | None) -> bool:
    if entry.source_type != "app" or context_app is None:
        return False

    context_id = getattr(context_app, "id", None)
    context_key = getattr(context_app, "key", None)
    context_slug = getattr(context_app, "slug", None)
    entry_slug = entry.id.split(":", 1)[1] if ":" in entry.id else ""

    return bool(
        (context_id and entry.catalog_id == context_id) or
        (context_slug and entry_slug == context_slug) or
        (context_key and entry.app_key == context_key)
    )


def score_entry(
    message: str,
    entry: KnowledgeEntry,
    context: AssistantClientContext | None = None,
) -> RankedEntry | None:
    normalized = normalize_text(message)
    if not normalized:
        return None

    title = normalize_text(entry.title)
    slug = entry.id.split(":", 1)[1].replace("-", " ") if ":" in entry.id else ""
    category = normalize_text(entry.category or "")
    aliases = tuple(normalize_text(alias) for alias in entry.aliases)
    keywords = tuple(normalize_text(keyword) for keyword in entry.keywords)
    summary = normalize_text(entry.summary)
    message_tokens = tokenize(message)

    score = entry.rank_weight
    reason = ""

    if normalized == title:
        score += 200
        reason = "exact-name"
    elif any(normalized == alias for alias in aliases):
        score += 90
        reason = "alias"
    elif normalized == slug:
        score += 80
        reason = "slug"
    elif title and title in normalized:
        score += 70
        reason = "title-phrase"
    elif any(
        alias and len(alias) > 2 and alias not in ALIAS_PHRASE_STOPWORDS and alias in normalized
        for alias in aliases
    ):
        score += 65
        reason = "alias-phrase"
    elif slug and slug in normalized:
        score += 60
        reason = "slug-phrase"

    if category and category in normalized:
        score += 45
        reason = reason or "category"

    keyword_bonus_count = 0
    keyword_phrase_matched = False
    for keyword in keywords:
        if keyword and len(keyword) > 2 and keyword not in PHRASE_STOPWORDS and keyword in normalized:
            if keyword_bonus_count < 3:
                score += 35
                keyword_bonus_count += 1
            reason = reason or "keyword"
        elif (
            keyword
            and len(normalized) > 5
            and normalized in keyword
            and not keyword_phrase_matched
        ):
            score += 55
            keyword_phrase_matched = True
            reason = reason or "phrase-in-keyword"

    searchable_tokens = tokenize(
        " ".join((entry.title, entry.summary, entry.category or "", *entry.aliases, *entry.keywords))
    )
    overlap = message_tokens & searchable_tokens
    if overlap:
        score += min(len(overlap), 6) * 8
        reason = reason or "token"

    if context is not None and entry.source_type == "app":
        if context.favorite_app_ids and entry.id.startswith("app:"):
            if entry.catalog_id in context.favorite_app_ids:
                score += 12
                reason = reason or "favorite"

        if context.recent_app_keys:
            recent_keys = set(context.recent_app_keys[:10])
            if entry.app_key in recent_keys:
                score += 10
                reason = reason or "recent"

        if _entry_matches_context_app(entry, context.current_app):
            score += 8
            reason = reason or "current-app"

    if score <= entry.rank_weight:
        return None

    return RankedEntry(entry=entry, score=score, reason=reason or "match")


def rank_entries(
    message: str,
    index: AssistantKnowledgeIndex,
    context: AssistantClientContext | None = None,
) -> list[RankedEntry]:
    ranked = [
        match
        for entry in index.entries
        if (match := score_entry(message, entry, context))
    ]
    ranked.sort(
        key=lambda match: (
            match.score,
            1 if match.entry.source_type == "app" else 0,
            match.entry.rank_weight,
            match.entry.title,
        ),
        reverse=True,
    )
    return ranked


def _safe_actions(entries: list[KnowledgeEntry], allowed_routes: frozenset[str]) -> list[AssistantAction]:
    actions: list[AssistantAction] = []
    seen_routes: set[str] = set()
    for entry in entries:
        if entry.route not in allowed_routes or entry.route in seen_routes:
            continue
        if entry.action_label is None or entry.action_type is None:
            continue
        actions.append(
            AssistantAction(
                type=entry.action_type,
                label=entry.action_label,
                route=entry.route,
            )
        )
        seen_routes.add(entry.route)
        if len(actions) == 3:
            break

    return actions


def _sources(entries: list[KnowledgeEntry]) -> list[AssistantSource]:
    return [
        AssistantSource(id=entry.id, title=entry.title, type=entry.source_type)
        for entry in entries[:3]
    ]


def _answer_for_match(entries: list[KnowledgeEntry], message: str) -> str:
    primary = entries[0]
    if primary.source_type == "app":
        parts = [
            f"{primary.title} is an Ansiversa app in {primary.category or 'the app catalog'}.",
            primary.summary,
        ]
        if len(entries) > 1 and entries[1].source_type == "app":
            also = ", ".join(entry.title for entry in entries[1:3] if entry.source_type == "app")
            if also:
                parts.append(f"Related matches: {also}.")
        return " ".join(parts)

    if primary.source_type == "faq":
        return primary.summary

    return primary.summary


def _filter_allowed_actions(
    actions: tuple[AssistantAction, ...],
    allowed_routes: frozenset[str],
) -> list[AssistantAction]:
    return [action for action in actions if action.route in allowed_routes]


def _is_financial_advice_query(message: str) -> bool:
    normalized = normalize_text(message)
    return "advice" in normalized and any(term in normalized for term in FINANCIAL_ADVICE_TERMS)


def _is_restricted_request(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in RESTRICTED_REQUEST_TERMS | PROMPT_INJECTION_TERMS)


def _restricted_request_result() -> DeterministicAssistantResult:
    return DeterministicAssistantResult(
        answer=(
            "I can only answer from public Ansiversa knowledge. I cannot expose "
            "internal instructions, private records, restricted documents, or hidden implementation notes."
        ),
        actions=list(FALLBACK_ACTIONS),
        sources=[],
        confidence="low",
        top_entries=(),
    )


def _professional_boundary_area(message: str) -> str | None:
    normalized = normalize_text(message)
    if _is_financial_advice_query(message):
        return "financial"
    for area, terms in PROFESSIONAL_BOUNDARY_TERMS.items():
        if any(term in normalized for term in terms):
            return area
    return None


def _professional_boundary_result(area: str, index: AssistantKnowledgeIndex) -> DeterministicAssistantResult:
    if area == "medical":
        entries = [
            entry
            for slug in ("medicine-reminder", "symptom-journal", "health-report-organizer")
            if (entry := _app_entry_by_slug(index, slug)) is not None
        ]
        actions = _safe_actions(entries, index.allowed_routes) or list(FALLBACK_ACTIONS)
        answer = (
            "Ansiversa can help organize health information, reminders, and records, "
            "but it does not provide medical diagnosis, treatment, dosage, or emergency advice. "
            "For medical decisions, consult a qualified healthcare professional."
        )
        return DeterministicAssistantResult(
            answer=answer,
            actions=actions,
            sources=_sources(entries),
            confidence="high",
            top_entries=tuple(entries[:3]),
        )

    if area == "legal":
        return DeterministicAssistantResult(
            answer=(
                "Ansiversa can help organize documents and information, but it does not "
                "provide professional legal advice. For legal decisions, consult a qualified legal professional."
            ),
            actions=list(FALLBACK_ACTIONS),
            sources=[],
            confidence="high",
            top_entries=(),
        )

    return _financial_guidance_result(index)


def _is_explicit_out_of_scope_query(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in OUT_OF_SCOPE_TERMS)


def _is_related_app_query(message: str) -> bool:
    tokens = tokenize(message)
    return bool(tokens & RELATED_APP_TERMS) and ("app" in tokens or "apps" in tokens)


def _is_future_query(message: str) -> bool:
    return bool(tokenize(message) & FUTURE_TERMS)


def _contains_specific_app_reference(message: str, index: AssistantKnowledgeIndex) -> bool:
    normalized = normalize_text(message)
    tokens = tokenize(message)
    for entry in index.entries:
        if entry.source_type != "app":
            continue
        title = normalize_text(entry.title)
        slug = _entry_slug(entry).replace("-", " ")
        if title and title in normalized:
            return True
        if slug and slug in normalized:
            return True
        for alias in entry.aliases:
            alias_tokens = tokenize(alias)
            significant_alias_tokens = {
                token
                for token in alias_tokens
                if len(token) > 2 and token not in ALIAS_PHRASE_STOPWORDS
            }
            if significant_alias_tokens and significant_alias_tokens <= tokens:
                return True
        if len(tokens & tokenize(entry.title)) >= 2:
            return True
    return False


def _generic_future_result(index: AssistantKnowledgeIndex) -> DeterministicAssistantResult:
    apps_entry = next((entry for entry in index.entries if entry.route == "/apps"), None)
    entries = [apps_entry] if apps_entry is not None else []
    return DeterministicAssistantResult(
        answer=(
            "I can explain approved public future direction for a specific Ansiversa app, "
            "but I cannot expose internal roadmap details or implementation plans. "
            "Ask about a specific app if you want its approved public future direction."
        ),
        actions=_safe_actions(entries, index.allowed_routes) or list(FALLBACK_ACTIONS),
        sources=_sources(entries),
        confidence="low",
        top_entries=tuple(entries),
    )


def _category_for_message(message: str) -> str | None:
    normalized = normalize_text(message)
    for category, aliases in CATEGORY_ALIASES.items():
        category_text = normalize_text(category)
        if category_text in normalized or any(normalize_text(alias) in normalized for alias in aliases):
            return category
    return None


def _is_collection_query(message: str) -> bool:
    tokens = tokenize(message)
    normalized = normalize_text(message)
    return (
        "app" in tokens
        or "apps" in tokens
        or "all" in tokens
        or "many" in tokens
        or normalized.startswith(("show me", "list", "which", "what"))
    )


def _collection_answer_result(
    entries: list[KnowledgeEntry],
    index: AssistantKnowledgeIndex,
    *,
    label: str,
) -> DeterministicAssistantResult:
    ordered = sorted(entries, key=lambda entry: entry.title)
    names = ", ".join(entry.title for entry in ordered)
    answer = f"Ansiversa has {len(ordered)} public {label}: {names}."
    return DeterministicAssistantResult(
        answer=answer,
        actions=_safe_actions(ordered, index.allowed_routes) or list(FALLBACK_ACTIONS),
        sources=_sources(ordered),
        confidence="high",
        top_entries=tuple(ordered[:3]),
    )


def _category_collection_result(
    message: str,
    index: AssistantKnowledgeIndex,
) -> DeterministicAssistantResult | None:
    tokens = tokenize(message)
    if not _is_collection_query(message) or not (
        {"apps", "all", "many", "list"} & tokens
        or normalize_text(message).startswith("show")
    ):
        return None
    category = _category_for_message(message)
    if category is None:
        return None
    matches = [
        entry
        for entry in index.entries
        if entry.source_type == "app" and entry.visibility == "public" and entry.category == category
    ]
    if not matches:
        return None
    return _collection_answer_result(matches, index, label=f"apps in {category}")


def _family_collection_result(
    message: str,
    index: AssistantKnowledgeIndex,
) -> DeterministicAssistantResult | None:
    if not _is_collection_query(message):
        return None
    tokens = tokenize(message)
    candidates = [
        token
        for token in tokens
        if len(token) > 3 and token not in COLLECTION_QUERY_TERMS and token not in FUTURE_TERMS
    ]
    if not candidates:
        return None

    app_entries = [
        entry
        for entry in index.entries
        if entry.source_type == "app" and entry.visibility == "public"
    ]
    best_token = ""
    best_matches: list[KnowledgeEntry] = []
    for token in candidates:
        matches = [
            entry
            for entry in app_entries
            if token in tokenize(" ".join((entry.title, _entry_slug(entry), *entry.aliases)))
        ]
        if len(matches) > len(best_matches):
            best_token = token
            best_matches = matches

    if len(best_matches) < 2:
        return None

    return _collection_answer_result(best_matches, index, label=f'apps matching "{best_token}"')


def _financial_guidance_result(index: AssistantKnowledgeIndex) -> DeterministicAssistantResult:
    actions = _filter_allowed_actions(FINANCIAL_GUIDANCE_ACTIONS, index.allowed_routes)
    if not actions:
        actions = list(FALLBACK_ACTIONS)

    return DeterministicAssistantResult(
        answer=(
            "Ansiversa provides tools to help you organize, calculate, and understand "
            "financial information, but it does not provide professional financial advice. "
            "For important financial decisions, consult a qualified financial advisor."
        ),
        actions=actions,
        sources=[],
        confidence="high",
        top_entries=(),
    )


def _out_of_scope_result() -> DeterministicAssistantResult:
    return DeterministicAssistantResult(
        answer=(
            "I could not find that topic within the current Ansiversa knowledge base. "
            "I can help with apps, platform features, pricing, accounts, navigation, "
            "and policies. If you are looking for something else, try rephrasing your question."
        ),
        actions=list(FALLBACK_ACTIONS),
        sources=[],
        confidence="low",
        top_entries=(),
    )


def _entry_slug(entry: KnowledgeEntry) -> str:
    return entry.id.split(":", 1)[1] if entry.id.startswith("app:") else ""


def _app_entry_by_slug(index: AssistantKnowledgeIndex, slug: str) -> KnowledgeEntry | None:
    return next(
        (
            entry
            for entry in index.entries
            if entry.source_type == "app" and _entry_slug(entry) == slug
        ),
        None,
    )


def _related_apps_result(
    message: str,
    index: AssistantKnowledgeIndex,
    context: AssistantClientContext | None,
) -> DeterministicAssistantResult | None:
    if not _is_related_app_query(message):
        return None

    ranked = rank_entries(message, index, context)
    primary = next((match.entry for match in ranked if match.entry.source_type == "app"), None)
    if primary is None or not primary.related_app_slugs:
        return None

    related_entries = [
        entry
        for slug in primary.related_app_slugs
        if (entry := _app_entry_by_slug(index, slug)) is not None
    ]
    if not related_entries:
        return None

    related_names = ", ".join(entry.title for entry in related_entries)
    entries = [primary, *related_entries]
    return DeterministicAssistantResult(
        answer=f"Apps related to {primary.title}: {related_names}.",
        actions=_safe_actions(related_entries, index.allowed_routes) or _safe_actions([primary], index.allowed_routes),
        sources=_sources(entries),
        confidence="high",
        top_entries=tuple(entries[:3]),
    )


def _future_result(
    message: str,
    index: AssistantKnowledgeIndex,
    context: AssistantClientContext | None,
) -> DeterministicAssistantResult | None:
    if not _is_future_query(message):
        return None

    ranked = rank_entries(message, index, context)
    primary = next((match.entry for match in ranked if match.entry.source_type == "app"), None)
    if primary is None:
        return None
    if not primary.future_summary:
        answer = (
            f"{primary.title} does not have approved public future-direction details in the "
            "current Ansiversa knowledge base. Current functionality remains the grounded source."
        )
        return _single_entry_result(primary, answer, index, confidence="high")

    answer = (
        f"Approved future direction for {primary.title}: {primary.future_summary} "
        "This is future direction, not current functionality."
    )
    return DeterministicAssistantResult(
        answer=answer,
        actions=_safe_actions([primary], index.allowed_routes),
        sources=_sources([primary]),
        confidence="high",
        top_entries=(primary,),
    )


def _find_entry_by_route(
    route: str | None,
    index: AssistantKnowledgeIndex,
) -> KnowledgeEntry | None:
    if not route:
        return None

    return next((entry for entry in index.entries if entry.route == route), None)


def _find_app_entry_by_context_app(
    context_app: object | None,
    index: AssistantKnowledgeIndex,
) -> KnowledgeEntry | None:
    if context_app is None:
        return None

    return next(
        (
            entry
            for entry in index.entries
            if entry.source_type == "app" and _entry_matches_context_app(entry, context_app)
        ),
        None,
    )


def _single_entry_result(
    entry: KnowledgeEntry,
    answer: str,
    index: AssistantKnowledgeIndex,
    *,
    confidence: Literal["high", "medium", "low"] = "high",
    action_label: str | None = None,
    action_route: str | None = None,
) -> DeterministicAssistantResult:
    action = AssistantAction(
        type=entry.action_type or "platform",
        label=action_label or entry.action_label or f"Open {entry.title}",
        route=action_route or entry.route,
    )
    actions = [action] if action.route in index.allowed_routes else []

    return DeterministicAssistantResult(
        answer=answer,
        actions=actions,
        sources=_sources([entry]),
        confidence=confidence,
        top_entries=(entry,),
    )


def _is_back_navigation_query(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in BACK_NAVIGATION_TERMS)


def _is_recent_reference_query(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in RECENT_REFERENCE_TERMS)


def _is_current_page_follow_up(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {
        "what do i get",
        "what is this",
        "tell me more",
        "how does this work",
        "can i change my picture",
        "can i update my profile picture",
    }


def _is_current_app_create_query(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in CURRENT_APP_CREATE_TERMS)


def _is_simple_navigation_message(message: str) -> bool:
    tokens = normalize_text(message).split()
    return bool(tokens and tokens[0] in NAVIGATION_INTENTS)


def _context_result(
    message: str,
    index: AssistantKnowledgeIndex,
    context: AssistantClientContext | None,
) -> DeterministicAssistantResult | None:
    if context is None:
        return None

    if _is_back_navigation_query(message):
        last_entry = _find_app_entry_by_context_app(context.last_opened_app, index)
        if last_entry is not None:
            return _single_entry_result(
                last_entry,
                f"Your last opened app was {last_entry.title}. I can take you back there.",
                index,
                action_label=f"Open {last_entry.title}",
            )

    if _is_recent_reference_query(message) and context.recent_app_keys:
        recent_entries: list[KnowledgeEntry] = []
        for app_key in context.recent_app_keys[:3]:
            entry = next(
                (
                    candidate
                    for candidate in index.entries
                    if candidate.source_type == "app" and candidate.app_key == app_key
                ),
                None,
            )
            if entry is not None:
                recent_entries.append(entry)

        if recent_entries:
            actions = _safe_actions(recent_entries, index.allowed_routes)
            return DeterministicAssistantResult(
                answer=(
                    f"Your most recent app is {recent_entries[0].title}. "
                    "I can open it or show other recently used apps."
                ),
                actions=actions or list(FALLBACK_ACTIONS),
                sources=_sources(recent_entries),
                confidence="high",
                top_entries=tuple(recent_entries),
            )

    current_route_entry = _find_entry_by_route(context.current_route, index)
    if current_route_entry is not None and _is_current_page_follow_up(message):
        return _single_entry_result(
            current_route_entry,
            current_route_entry.summary,
            index,
        )

    current_app_entry = _find_app_entry_by_context_app(context.current_app, index)
    if current_app_entry is not None and _is_current_app_create_query(message):
        page = context.current_page or "this page"
        answer = (
            f"You are currently in {current_app_entry.title} on {page}. "
            "Use the Create or Add action on this page to add a new record in the current workflow."
        )
        return _single_entry_result(
            current_app_entry,
            answer,
            index,
            action_label=f"Stay on {page}",
            action_route=context.current_route or current_app_entry.route,
        )

    return None


def retrieve_deterministic(
    message: str,
    index: AssistantKnowledgeIndex,
    context: AssistantClientContext | None = None,
) -> DeterministicAssistantResult:
    if _is_restricted_request(message):
        return _restricted_request_result()

    if professional_area := _professional_boundary_area(message):
        return _professional_boundary_result(professional_area, index)

    if _is_explicit_out_of_scope_query(message):
        return _out_of_scope_result()

    if context_result := _context_result(message, index, context):
        return context_result

    if _is_future_query(message) and not _contains_specific_app_reference(message, index):
        return _generic_future_result(index)

    if future_result := _future_result(message, index, context):
        return future_result

    if related_result := _related_apps_result(message, index, context):
        return related_result

    if category_result := _category_collection_result(message, index):
        return category_result

    if family_result := _family_collection_result(message, index):
        return family_result

    public_index = AssistantKnowledgeIndex(
        entries=tuple(entry for entry in index.entries if entry.visibility == "public"),
        allowed_routes=index.allowed_routes,
    )
    ranked = rank_entries(message, public_index, context)
    if not ranked:
        return DeterministicAssistantResult(
            answer=(
                "I could not find a confident match in the public Ansiversa knowledge base. "
                "Try an app name, category, platform page, or common topic such as pricing, FAQ, or documents."
            ),
            actions=list(FALLBACK_ACTIONS),
            sources=[],
            confidence="low",
            top_entries=(),
        )

    top_entries: list[KnowledgeEntry] = []
    seen_ids: set[str] = set()
    for match in ranked:
        if match.entry.id in seen_ids:
            continue
        top_entries.append(match.entry)
        seen_ids.add(match.entry.id)
        if len(top_entries) == 3:
            break

    best_score = ranked[0].score
    confidence = "high" if best_score >= 70 else "medium"
    action_entries = top_entries
    if (
        context is not None
        and top_entries
        and _entry_matches_context_app(top_entries[0], context.current_app)
        and not _is_simple_navigation_message(message)
    ):
        action_entries = [
            entry
            for entry in top_entries
            if not _entry_matches_context_app(entry, context.current_app)
        ]
    actions = _safe_actions(action_entries, index.allowed_routes) or list(FALLBACK_ACTIONS)

    return DeterministicAssistantResult(
        answer=_answer_for_match(top_entries, message),
        actions=actions,
        sources=_sources(top_entries),
        confidence=confidence,
        top_entries=tuple(top_entries),
    )


def _is_simple_navigation_query(message: str, result: DeterministicAssistantResult) -> bool:
    if not result.top_entries:
        return False

    if result.top_entries[0].source_type != "app":
        return True

    return _is_simple_navigation_message(message)


def _select_response_mode(
    message: str,
    result: DeterministicAssistantResult,
    *,
    provider_available: bool,
) -> Literal["deterministic", "openai_grounded", "fallback"]:
    if result.confidence == "low":
        return "fallback"

    if _is_future_query(message):
        return "deterministic"

    if _is_current_app_create_query(message):
        return "deterministic"

    if not result.top_entries:
        return "deterministic"

    if not provider_available or _is_simple_navigation_query(message, result):
        return "deterministic"

    if result.top_entries[0].source_type == "app":
        return "openai_grounded"

    return "deterministic"


def _provider_context(
    entries: tuple[KnowledgeEntry, ...],
    actions: list[AssistantAction],
    *,
    max_chars: int,
    max_chunks: int,
    context: AssistantClientContext | None = None,
) -> str:
    permitted_action_labels = ", ".join(action.label for action in actions)
    chunks: list[str] = []
    if context is not None:
        context_lines = [
            f"Current route: {context.current_route or 'Unknown'}",
            f"Current page: {context.current_page or 'Unknown'}",
        ]
        if context.current_app is not None and context.current_app.name:
            context_lines.append(f"Current app: {context.current_app.name}")
        if context.current_category:
            context_lines.append(f"Current category: {context.current_category}")
        chunks.append("\n".join(context_lines))

    for entry in entries[:max_chunks]:
        if entry.visibility != "public":
            continue
        chunks.append(
            "\n".join(
                (
                    f"Title: {entry.title}",
                    f"Type: {entry.source_type}",
                    f"Category: {entry.category or 'Platform'}",
                    f"Summary: {entry.summary}",
                )
            )
        )

    if permitted_action_labels:
        chunks.append(f"Permitted action labels: {permitted_action_labels}")

    context = "\n\n---\n\n".join(chunks)
    if len(context) <= max_chars:
        return context

    return context[:max_chars].rsplit(" ", 1)[0].strip()


def query_index(
    message: str,
    index: AssistantKnowledgeIndex,
    *,
    context: AssistantClientContext | None = None,
    answer_provider: AssistantAnswerProvider | None = None,
    max_context_chars: int = 3500,
) -> AssistantQueryResponse:
    deterministic = retrieve_deterministic(message, index, context)
    provider_available = answer_provider is not None
    response_mode = _select_response_mode(
        message,
        deterministic,
        provider_available=provider_available,
    )
    if response_mode != "openai_grounded" or answer_provider is None:
        return deterministic.to_response(response_mode=response_mode)

    try:
        context = _provider_context(
            deterministic.top_entries,
            deterministic.actions,
            max_chars=max_context_chars,
            max_chunks=settings.AI_MAX_CONTEXT_CHUNKS,
            context=context,
        )
        ai_answer = answer_provider.generate_answer(message, context)
    except Exception:
        return deterministic.to_response(response_mode="deterministic")

    if not ai_answer:
        return deterministic.to_response(response_mode="deterministic")

    return deterministic.to_response(answer=ai_answer, response_mode="openai_grounded")


def query_assistant(
    db: Session,
    message: str,
    context: AssistantClientContext | None = None,
) -> AssistantQueryResponse:
    start = perf_counter()
    try:
        index = build_knowledge_index()
        LOGGER.debug(
            "Assistant registry retrieval index loaded in %.2fms with %s entries.",
            (perf_counter() - start) * 1000,
            len(index.entries),
        )
    except Exception:
        LOGGER.exception(
            "Assistant registry retrieval failed; using legacy deterministic fallback."
        )
        index = build_legacy_knowledge_index(db)
    if not settings.AI_GATEWAY_ENABLED:
        return retrieve_deterministic(message, index, context).to_response(response_mode="deterministic")

    provider = OpenAIResponseProvider() if settings.ASSISTANT_OPENAI_ENABLED else None
    if provider is not None and not provider.is_configured:
        provider = None
    return query_index(
        message,
        index,
        context=context,
        answer_provider=provider,
        max_context_chars=settings.ASSISTANT_MAX_CONTEXT_CHARS,
    )
