from __future__ import annotations

import re

from app.modules.astra_ai.contracts import (
    AuditMetadata,
    EvidenceItem,
    ExecutionStatus,
    RefusalReason,
    ResponseClassification,
)
from app.modules.astra_ai.policy import PolicyDecision
from app.modules.astra_ai.settings import ASTRA_AI_PLATFORM_ENABLED

SECRET_PATTERNS = (
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"(api[_-]?key|token|password|database_url)\s*=", re.IGNORECASE),
    re.compile(r"(postgres(?:ql)?|mysql|libsql)://", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
)


def build_audit_metadata(
    *,
    request_id: str,
    intent,
    decision: PolicyDecision,
    context_sources: tuple[str, ...],
    classification: ResponseClassification,
    execution_status: ExecutionStatus,
) -> AuditMetadata:
    evidence = tuple(
        _safe_evidence_item(key, value)
        for key, value in (
            ("runtime", "disabled_by_default"),
            ("context", ",".join(context_sources)),
            ("policy", decision.authorization_result),
        )
    )
    return AuditMetadata(
        request_id=request_id,
        resolved_intent=intent.intent,
        policy_decision=decision.decision,
        authorization_result=decision.authorization_result,
        context_sources_used=context_sources,
        refusal_reason=decision.refusal_reason,
        clarification_reason=decision.clarification_reason,
        proposed_action_type=decision.proposed_action_type,
        execution_status=execution_status,
        response_classification=classification,
        runtime_enabled=ASTRA_AI_PLATFORM_ENABLED,
        evidence=evidence,
    )


def assert_no_secret_material(metadata: AuditMetadata) -> None:
    payload = metadata.model_dump_json()
    for pattern in SECRET_PATTERNS:
        if pattern.search(payload):
            raise ValueError("Unsafe audit evidence detected.")


def refusal_reason_from_decision(decision: PolicyDecision) -> RefusalReason:
    return decision.refusal_reason or RefusalReason.UNSUPPORTED_SCOPE


def _safe_evidence_item(key: str, value: str) -> EvidenceItem:
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            return EvidenceItem(key=key, value="redacted")
    return EvidenceItem(key=key, value=value[:240])
