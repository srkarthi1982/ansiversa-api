from __future__ import annotations

import re

from app.modules.astra_ai.contracts import AssistantIntent, AssistantIntentType

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

PROMPT_CONFLICT_TERMS = (
    "ignore instructions",
    "ignore previous",
    "reveal prompt",
    "show system prompt",
    "developer message",
)
PRIVATE_DATA_TERMS = (
    "my record",
    "my records",
    "private data",
    "database",
    "user id",
    "other user",
    "another user",
    "someone else",
    "cross user",
    "cross-user",
)
ACTION_TERMS = ("create", "update", "delete", "edit", "send", "schedule", "save", "pay")


def classify_intent(message: str) -> AssistantIntent:
    normalized = _normalize(message)
    tokens = tuple(TOKEN_PATTERN.findall(normalized))
    if not tokens or len(tokens) < 2:
        return AssistantIntent(
            intent=AssistantIntentType.CAPABILITY_CLARIFICATION,
            confidence="low",
            matched_terms=tokens,
            clarification_reason="The request is too short to resolve safely.",
        )
    if _contains(normalized, PROMPT_CONFLICT_TERMS):
        return AssistantIntent(
            intent=AssistantIntentType.UNSUPPORTED_REQUEST,
            confidence="high",
            matched_terms=("prompt_conflict",),
        )
    if _contains(normalized, PRIVATE_DATA_TERMS):
        return AssistantIntent(
            intent=AssistantIntentType.UNSUPPORTED_REQUEST,
            confidence="high",
            matched_terms=("private_data",),
        )
    if any(term in tokens for term in ACTION_TERMS):
        return AssistantIntent(
            intent=AssistantIntentType.FUTURE_APP_ACTION_REQUEST,
            confidence="high",
            matched_terms=tuple(term for term in ACTION_TERMS if term in tokens),
        )
    if {"compare", "versus", "vs", "difference", "better"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.APP_COMPARISON,
            confidence="medium",
            matched_terms=tuple(sorted({"compare", "versus", "vs", "difference", "better"} & set(tokens))),
        )
    if {"category", "categories"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.CATEGORY_DISCOVERY,
            confidence="high",
            matched_terms=tuple(sorted({"category", "categories"} & set(tokens))),
        )
    if {"login", "account", "profile", "settings", "password"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.ACCOUNT_GUIDANCE,
            confidence="high",
            matched_terms=tuple(sorted({"login", "account", "profile", "settings", "password"} & set(tokens))),
        )
    if {"route", "navigate", "navigation", "open", "where", "go"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.NAVIGATION_GUIDANCE,
            confidence="high",
            matched_terms=tuple(sorted({"route", "navigate", "navigation", "open", "where", "go"} & set(tokens))),
        )
    if {"pricing", "price", "subscription", "billing", "plan"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.PRICING_SUBSCRIPTION_GUIDANCE,
            confidence="high",
            matched_terms=tuple(sorted({"pricing", "price", "subscription", "billing", "plan"} & set(tokens))),
        )
    if {"terms", "privacy", "legal", "policy"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.LEGAL_POLICY_GUIDANCE,
            confidence="high",
            matched_terms=tuple(sorted({"terms", "privacy", "legal", "policy"} & set(tokens))),
        )
    if {"help", "faq", "support", "question"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.HELP_FAQ,
            confidence="medium",
            matched_terms=tuple(sorted({"help", "faq", "support", "question"} & set(tokens))),
        )
    if {"app", "apps", "find", "discover", "recommend", "catalog"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.APP_DISCOVERY,
            confidence="high",
            matched_terms=tuple(sorted({"app", "apps", "find", "discover", "recommend", "catalog"} & set(tokens))),
        )
    if {"ansiversa", "platform", "astra"} & set(tokens):
        return AssistantIntent(
            intent=AssistantIntentType.PLATFORM_INFORMATION,
            confidence="high",
            matched_terms=tuple(sorted({"ansiversa", "platform", "astra"} & set(tokens))),
        )
    return AssistantIntent(
        intent=AssistantIntentType.CAPABILITY_CLARIFICATION,
        confidence="low",
        matched_terms=tokens[:5],
        clarification_reason="The request does not match a bounded platform intent.",
    )


def _normalize(message: str) -> str:
    return " ".join(message.lower().strip().split())


def _contains(message: str, terms: tuple[str, ...]) -> bool:
    return any(term in message for term in terms)
