from __future__ import annotations

from dataclasses import dataclass

from app.modules.astra_ai.contracts import (
    AssistantIntent,
    AssistantIntentType,
    AssistantRequest,
    PolicyDecisionType,
    RefusalReason,
)
from app.modules.astra_ai.matching import has_any_term

PROMPT_CONFLICT_TERMS = ("ignore instructions", "reveal prompt", "system prompt", "developer message")
SECRET_TERMS = ("secret", "token", "password", "database url", "api key")
CROSS_USER_TERMS = ("other user", "another user", "someone else", "cross user", "cross-user")
PRIVATE_DATA_TERMS = ("private data", "my record", "my records", "app database", "database record")
PRIVATE_ACCOUNT_TERMS = ("my", "profile", "settings", "subscription")

@dataclass(frozen=True)
class PolicyDecision:
    decision: PolicyDecisionType
    authorization_result: str
    refusal_reason: RefusalReason | None = None
    clarification_reason: str | None = None
    proposed_action_type: str | None = None


def evaluate_policy(request: AssistantRequest, intent: AssistantIntent) -> PolicyDecision:
    message = request.message
    if has_any_term(message, PROMPT_CONFLICT_TERMS):
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_prompt_conflict",
            refusal_reason=RefusalReason.PROMPT_CONFLICT,
        )
    if has_any_term(message, SECRET_TERMS):
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_secret_or_internal_access",
            refusal_reason=RefusalReason.SECRET_OR_INTERNAL_ACCESS,
        )
    if has_any_term(message, CROSS_USER_TERMS):
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_cross_user_access",
            refusal_reason=RefusalReason.CROSS_USER_ACCESS,
        )
    if has_any_term(message, PRIVATE_DATA_TERMS):
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_private_record_access",
            refusal_reason=RefusalReason.PRIVATE_DATA_ACCESS,
        )
    if intent.intent is AssistantIntentType.CAPABILITY_CLARIFICATION:
        return PolicyDecision(
            decision=PolicyDecisionType.CLARIFY,
            authorization_result="clarification_required",
            refusal_reason=RefusalReason.AMBIGUOUS,
            clarification_reason=intent.clarification_reason or "The request is ambiguous.",
        )
    if intent.intent is AssistantIntentType.FUTURE_APP_ACTION_REQUEST:
        return PolicyDecision(
            decision=PolicyDecisionType.PROPOSE_ACTION_ONLY,
            authorization_result=(
                "authenticated_action_proposal_only"
                if request.user_context.is_authenticated
                else "anonymous_action_proposal_only"
            ),
            proposed_action_type="future_platform_or_app_action",
        )
    if (
        not request.user_context.is_authenticated
        and intent.intent in {AssistantIntentType.ACCOUNT_GUIDANCE}
        and has_any_term(message, PRIVATE_ACCOUNT_TERMS)
    ):
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_anonymous_private_account_guidance",
            refusal_reason=RefusalReason.UNAUTHORIZED,
        )
    if intent.intent is AssistantIntentType.UNSUPPORTED_REQUEST:
        return PolicyDecision(
            decision=PolicyDecisionType.REFUSE,
            authorization_result="blocked_unsupported_scope",
            refusal_reason=RefusalReason.UNSUPPORTED_SCOPE,
        )
    return PolicyDecision(
        decision=PolicyDecisionType.ALLOW_READ_ONLY,
        authorization_result=(
            "authenticated_read_only_platform_guidance"
            if request.user_context.is_authenticated
            else "anonymous_read_only_public_guidance"
        ),
    )
