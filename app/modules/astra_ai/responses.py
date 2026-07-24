from __future__ import annotations

from app.modules.astra_ai.contracts import (
    ActionProposal,
    AssistantIntent,
    AssistantIntentType,
    ClarificationRequest,
    ExecutionStatus,
    PlatformContext,
    RefusalReason,
    RefusalResponse,
)
from app.modules.astra_ai.policy import PolicyDecision


def build_answer(intent: AssistantIntent, context: PlatformContext) -> str:
    match intent.intent:
        case AssistantIntentType.PLATFORM_INFORMATION:
            return (
                "Ansiversa is one governed platform with one login, one shell, "
                "and a fixed catalog of 100 solution apps."
            )
        case AssistantIntentType.APP_DISCOVERY:
            apps = ", ".join(app.name for app in context.apps[:4])
            return f"Astra AI Phase 1 can discover governed platform catalog apps. Examples: {apps}."
        case AssistantIntentType.APP_COMPARISON:
            return "Astra AI Phase 1 can compare apps using public catalog metadata only, not private app records."
        case AssistantIntentType.CATEGORY_DISCOVERY:
            return "Available platform categories include: " + ", ".join(context.categories) + "."
        case AssistantIntentType.NAVIGATION_GUIDANCE:
            public_routes = ", ".join(route.route for route in context.routes if route.public)
            return f"Phase 1 can guide users to approved platform routes such as {public_routes}."
        case AssistantIntentType.ACCOUNT_GUIDANCE:
            return "Account guidance is limited to platform-level routes and cannot inspect private profile records."
        case AssistantIntentType.PRICING_SUBSCRIPTION_GUIDANCE:
            return "Pricing and subscription guidance is limited to approved platform pricing and subscription routes."
        case AssistantIntentType.LEGAL_POLICY_GUIDANCE:
            return "Legal and policy guidance is limited to navigation toward approved Terms and Privacy information."
        case AssistantIntentType.HELP_FAQ:
            return "Help and FAQ guidance can point users toward approved platform FAQ and support routes."
        case _:
            return "Astra AI Phase 1 only supports bounded platform-level guidance."


def build_clarification(decision: PolicyDecision) -> ClarificationRequest:
    return ClarificationRequest(
        reason=decision.clarification_reason or "The request needs clarification.",
        question="Which platform topic do you want help with: apps, categories, navigation, account, pricing, or policy?",
    )


def build_refusal(reason: RefusalReason) -> RefusalResponse:
    messages = {
        RefusalReason.PRIVATE_DATA_ACCESS: "Astra AI Phase 1 cannot access private app records or app databases.",
        RefusalReason.CROSS_USER_ACCESS: "Astra AI cannot access another user's data or cross user boundaries.",
        RefusalReason.UNSUPPORTED_SCOPE: "That request is outside the authorized platform Phase 1 scope.",
        RefusalReason.PROMPT_CONFLICT: "Astra AI must follow Ansiversa governance and cannot follow conflicting instructions.",
        RefusalReason.UNAUTHORIZED: "Authentication is required for that private account context.",
        RefusalReason.AMBIGUOUS: "Astra AI needs clarification before it can answer safely.",
        RefusalReason.SECRET_OR_INTERNAL_ACCESS: "Astra AI cannot reveal secrets, credentials, or private internal data.",
    }
    return RefusalResponse(reason=reason, message=messages[reason])


def build_action_proposal(decision: PolicyDecision) -> ActionProposal:
    return ActionProposal(
        action_type=decision.proposed_action_type or "future_platform_or_app_action",
        label="Proposed future action",
        route=None,
        requires_future_authorization=True,
        execution_status=ExecutionStatus.PROPOSED_NOT_EXECUTED,
    )
