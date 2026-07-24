from __future__ import annotations

from app.modules.astra_ai.audit import (
    assert_no_secret_material,
    build_audit_metadata,
    deterministic_request_id,
    refusal_reason_from_decision,
)
from app.modules.astra_ai.context import resolve_platform_context
from app.modules.astra_ai.contracts import (
    AssistantRequest,
    AssistantResponse,
    ExecutionStatus,
    PolicyDecisionType,
    ResponseClassification,
)
from app.modules.astra_ai.fixtures import PlatformSourceBundle
from app.modules.astra_ai.intents import classify_intent
from app.modules.astra_ai.policy import evaluate_policy
from app.modules.astra_ai.responses import (
    build_action_proposal,
    build_answer,
    build_clarification,
    build_refusal,
)


def orchestrate_platform_request(
    request: AssistantRequest,
    *,
    sources: PlatformSourceBundle | None = None,
    request_id: str | None = None,
) -> AssistantResponse:
    platform_context = resolve_platform_context(request, sources=sources)
    intent = classify_intent(request.message)
    decision = evaluate_policy(request, intent)

    clarification = None
    refusal = None
    action_proposal = None
    execution_status = ExecutionStatus.NOT_APPLICABLE

    if decision.decision is PolicyDecisionType.CLARIFY:
        classification = ResponseClassification.CLARIFICATION
        clarification = build_clarification(decision)
        answer = clarification.question
        execution_status = ExecutionStatus.BLOCKED_BY_POLICY
    elif decision.decision is PolicyDecisionType.REFUSE:
        classification = ResponseClassification.REFUSAL
        refusal = build_refusal(refusal_reason_from_decision(decision))
        answer = refusal.message
        execution_status = ExecutionStatus.BLOCKED_BY_POLICY
    elif decision.decision is PolicyDecisionType.PROPOSE_ACTION_ONLY:
        classification = ResponseClassification.ACTION_PROPOSAL
        action_proposal = build_action_proposal(decision)
        answer = "Astra AI Phase 1 may describe this as a future action proposal, but it cannot execute it."
        execution_status = ExecutionStatus.PROPOSED_NOT_EXECUTED
    else:
        classification = ResponseClassification.PLATFORM_GUIDANCE
        answer = build_answer(intent, platform_context)

    audit = build_audit_metadata(
        request_id=request_id
        or deterministic_request_id(
            request=request,
            context_sources=platform_context.knowledge_sources + platform_context.documentation_sources,
        ),
        intent=intent,
        decision=decision,
        context_sources=platform_context.knowledge_sources + platform_context.documentation_sources,
        classification=classification,
        execution_status=execution_status,
    )
    assert_no_secret_material(audit)
    return AssistantResponse(
        answer=answer,
        classification=classification,
        intent=intent,
        policy_decision=decision.decision,
        platform_context=platform_context,
        clarification=clarification,
        refusal=refusal,
        action_proposal=action_proposal,
        audit=audit,
    )
