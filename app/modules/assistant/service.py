from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.assistant.openai_provider import OpenAIResponseProvider
from app.modules.assistant.schemas import (
    AssistantAction,
    AssistantQueryResponse,
    AssistantSource,
)
from app.modules.faqs.models import Faq

SourceType = Literal["app", "platform", "account", "legal", "faq"]
ActionType = Literal["app", "platform", "account", "legal"]

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
OVERVIEW_DATA_DIR = Path(__file__).resolve().parents[1] / "content" / "data" / "overview"


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    title: str
    source_type: SourceType
    route: str
    summary: str
    category: str | None = None
    aliases: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    action_label: str | None = None
    action_type: ActionType | None = None
    visibility: str = "public"
    rank_weight: int = 0


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

NAVIGATION_INTENTS = {
    "open",
    "go",
    "show",
    "find",
    "launch",
    "take",
    "browse",
}


def normalize_text(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.lower()))


def tokenize(value: str) -> set[str]:
    return set(normalize_text(value).split())


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
                category=str(row["category_name"]),
                aliases=APP_ALIASES.get(slug, ()),
                keywords=(slug.replace("-", " "), str(row["category_name"]), str(row["launch_status"])),
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


def build_knowledge_index(db: Session) -> AssistantKnowledgeIndex:
    entries = (*_build_app_entries(db), *PLATFORM_ENTRIES, *_build_faq_entries(db))
    public_entries = tuple(entry for entry in entries if entry.visibility == "public")
    allowed_routes = frozenset({entry.route for entry in public_entries} | {"/apps", "/faq"})

    return AssistantKnowledgeIndex(entries=public_entries, allowed_routes=allowed_routes)


def score_entry(message: str, entry: KnowledgeEntry) -> RankedEntry | None:
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
        score += 100
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
    elif any(alias and alias in normalized for alias in aliases):
        score += 65
        reason = "alias-phrase"
    elif slug and slug in normalized:
        score += 60
        reason = "slug-phrase"

    if category and category in normalized:
        score += 45
        reason = reason or "category"

    for keyword in keywords:
        if keyword and keyword in normalized:
            score += 35
            reason = reason or "keyword"

    searchable_tokens = tokenize(
        " ".join((entry.title, entry.summary, entry.category or "", *entry.aliases, *entry.keywords))
    )
    overlap = message_tokens & searchable_tokens
    if overlap:
        score += min(len(overlap), 6) * 8
        reason = reason or "token"

    if score <= entry.rank_weight:
        return None

    return RankedEntry(entry=entry, score=score, reason=reason or "match")


def rank_entries(message: str, index: AssistantKnowledgeIndex) -> list[RankedEntry]:
    ranked = [match for entry in index.entries if (match := score_entry(message, entry))]
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


def retrieve_deterministic(message: str, index: AssistantKnowledgeIndex) -> DeterministicAssistantResult:
    public_index = AssistantKnowledgeIndex(
        entries=tuple(entry for entry in index.entries if entry.visibility == "public"),
        allowed_routes=index.allowed_routes,
    )
    ranked = rank_entries(message, public_index)
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
    actions = _safe_actions(top_entries, index.allowed_routes) or list(FALLBACK_ACTIONS)

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

    tokens = normalize_text(message).split()
    return bool(tokens and tokens[0] in NAVIGATION_INTENTS)


def _select_response_mode(
    message: str,
    result: DeterministicAssistantResult,
    *,
    provider_available: bool,
) -> Literal["deterministic", "openai_grounded", "fallback"]:
    if result.confidence == "low" or not result.sources:
        return "fallback"

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
) -> str:
    permitted_action_labels = ", ".join(action.label for action in actions)
    chunks: list[str] = []
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
    answer_provider: AssistantAnswerProvider | None = None,
    max_context_chars: int = 3500,
) -> AssistantQueryResponse:
    deterministic = retrieve_deterministic(message, index)
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
        )
        ai_answer = answer_provider.generate_answer(message, context)
    except Exception:
        return deterministic.to_response(response_mode="deterministic")

    if not ai_answer:
        return deterministic.to_response(response_mode="deterministic")

    return deterministic.to_response(answer=ai_answer, response_mode="openai_grounded")


def query_assistant(db: Session, message: str) -> AssistantQueryResponse:
    index = build_knowledge_index(db)
    if not settings.AI_GATEWAY_ENABLED:
        return retrieve_deterministic(message, index).to_response(response_mode="deterministic")

    provider = OpenAIResponseProvider() if settings.ASSISTANT_OPENAI_ENABLED else None
    if provider is not None and not provider.is_configured:
        provider = None
    return query_index(
        message,
        index,
        answer_provider=provider,
        max_context_chars=settings.ASSISTANT_MAX_CONTEXT_CHARS,
    )
