from app.modules.astra_ai.contracts import AssistantIntent, AssistantIntentType
from app.modules.astra_ai.matching import has_any_term, matched_terms, tokenize

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
COMPARE_TERMS = ("compare", "versus", "vs", "difference", "better")
CATEGORY_TERMS = ("category", "categories")
ACCOUNT_TERMS = ("login", "account", "profile", "settings", "password")
NAVIGATION_TERMS = ("route", "navigate", "navigation", "open", "where", "go")
PRICING_TERMS = ("pricing", "price", "subscription", "billing", "plan")
LEGAL_POLICY_TERMS = ("terms", "privacy", "legal", "policy")
HELP_TERMS = ("help", "faq", "support", "question")
APP_DISCOVERY_TERMS = ("app", "apps", "find", "discover", "recommend", "catalog")
PLATFORM_TERMS = ("ansiversa", "platform", "astra")


def classify_intent(message: str) -> AssistantIntent:
    tokens = tokenize(message)
    if not tokens or len(tokens) < 2:
        return AssistantIntent(
            intent=AssistantIntentType.CAPABILITY_CLARIFICATION,
            confidence="low",
            matched_terms=tokens,
            clarification_reason="The request is too short to resolve safely.",
        )
    if has_any_term(message, PROMPT_CONFLICT_TERMS):
        return AssistantIntent(
            intent=AssistantIntentType.UNSUPPORTED_REQUEST,
            confidence="high",
            matched_terms=("prompt_conflict",),
        )
    if has_any_term(message, PRIVATE_DATA_TERMS):
        return AssistantIntent(
            intent=AssistantIntentType.UNSUPPORTED_REQUEST,
            confidence="high",
            matched_terms=("private_data",),
        )
    action_matches = matched_terms(message, ACTION_TERMS)
    if action_matches:
        return AssistantIntent(
            intent=AssistantIntentType.FUTURE_APP_ACTION_REQUEST,
            confidence="high",
            matched_terms=action_matches,
        )
    compare_matches = matched_terms(message, COMPARE_TERMS)
    if compare_matches:
        return AssistantIntent(
            intent=AssistantIntentType.APP_COMPARISON,
            confidence="medium",
            matched_terms=compare_matches,
        )
    category_matches = matched_terms(message, CATEGORY_TERMS)
    if category_matches:
        return AssistantIntent(
            intent=AssistantIntentType.CATEGORY_DISCOVERY,
            confidence="high",
            matched_terms=category_matches,
        )
    account_matches = matched_terms(message, ACCOUNT_TERMS)
    if account_matches:
        return AssistantIntent(
            intent=AssistantIntentType.ACCOUNT_GUIDANCE,
            confidence="high",
            matched_terms=account_matches,
        )
    navigation_matches = matched_terms(message, NAVIGATION_TERMS)
    if navigation_matches:
        return AssistantIntent(
            intent=AssistantIntentType.NAVIGATION_GUIDANCE,
            confidence="high",
            matched_terms=navigation_matches,
        )
    pricing_matches = matched_terms(message, PRICING_TERMS)
    if pricing_matches:
        return AssistantIntent(
            intent=AssistantIntentType.PRICING_SUBSCRIPTION_GUIDANCE,
            confidence="high",
            matched_terms=pricing_matches,
        )
    legal_matches = matched_terms(message, LEGAL_POLICY_TERMS)
    if legal_matches:
        return AssistantIntent(
            intent=AssistantIntentType.LEGAL_POLICY_GUIDANCE,
            confidence="high",
            matched_terms=legal_matches,
        )
    help_matches = matched_terms(message, HELP_TERMS)
    if help_matches:
        return AssistantIntent(
            intent=AssistantIntentType.HELP_FAQ,
            confidence="medium",
            matched_terms=help_matches,
        )
    app_matches = matched_terms(message, APP_DISCOVERY_TERMS)
    if app_matches:
        return AssistantIntent(
            intent=AssistantIntentType.APP_DISCOVERY,
            confidence="high",
            matched_terms=app_matches,
        )
    platform_matches = matched_terms(message, PLATFORM_TERMS)
    if platform_matches:
        return AssistantIntent(
            intent=AssistantIntentType.PLATFORM_INFORMATION,
            confidence="high",
            matched_terms=platform_matches,
        )
    return AssistantIntent(
        intent=AssistantIntentType.CAPABILITY_CLARIFICATION,
        confidence="low",
        matched_terms=tokens[:5],
        clarification_reason="The request does not match a bounded platform intent.",
    )
