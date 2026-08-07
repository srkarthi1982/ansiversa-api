# ASTRA-AI-INTENT-ARCH-001 — Proposed Contract

Status: Proposed / Non-Executable / Pending Astra Review

## Endpoint

```text
POST /api/v1/astra/agent/query
```

The endpoint is authenticated, server-gated, and absent or fail-closed outside
recognized non-production environments. It is independent of
`/api/v1/assistant/query` and preserves `/api/v1/astra/chat` unchanged.

## Client Request

```json
{
  "question": "What's renewing in the next 30 days?",
  "conversationId": "optional server-issued active conversation reference",
  "clientRequestReference": "optional bounded correlation reference"
}
```

The question is trimmed, non-empty, and bounded. Extra fields are forbidden.
Client-supplied app, capability, parameters, identity, provider/model choice,
authority, grant, or resolved intent are forbidden. Client input cannot enable
the feature.

## Internal Provider Envelope

```json
{
  "schemaVersion": "1.0",
  "question": "What's renewing in the next 30 days?",
  "allowedStatuses": ["resolved", "clarification_required", "unsupported"],
  "eligibleCapabilities": [
    {
      "appId": "subscription_manager",
      "capabilityId": "subscription.renewing_within_days",
      "purpose": "List active subscriptions renewing within an allowed day window.",
      "parameters": [
        {"name": "days", "type": "integer", "required": true, "minimum": 1, "maximum": 366}
      ]
    }
  ]
}
```

The server derives this metadata-only envelope from the certified app-owned
catalog. It contains no record data or identity/authority material.

## Untrusted Candidate

```json
{
  "interpretationStatus": "resolved",
  "appId": "subscription_manager",
  "capabilityId": "subscription.renewing_within_days",
  "parameters": [{"name": "days", "value": 30}],
  "clarificationReason": null
}
```

Rules:

- exactly one bounded object and `extra=forbid` at every level;
- `resolved` requires exact app, supplied capability, and valid parameters;
- clarification requires a bounded server-allowlisted reason and cannot carry
  an executable capability or parameters;
- unsupported cannot carry an executable capability or parameters;
- duplicate parameters are invalid; and
- confidence, explanation, identity, authority, DB, SQL, tool, prompt, or
  provider-action fields invalidate output.

Suggested clarification codes are `ambiguous_cost_basis`,
`missing_days_window`, `multiple_supported_meanings`, and
`insufficient_supported_intent`.

## Deterministic Validation Result

The validator returns one of:

```text
validated_resolved_intent
clarification_required
unsupported
provider_unavailable
invalid_provider_response
stale_or_replayed_interpretation
```

Only `validated_resolved_intent` can be converted by the server to an
`AstraChatDeclaredIntent` with exact app, action, subject, capability, and
parameters. The server constructs `AstraChatRequest` and calls the certified
gateway in-process with existing authenticated context and app DB dependency.

## Agent Response

```json
{
  "conversationId": "conv_...",
  "status": "ok",
  "interpretationStatus": "resolved",
  "interpretationReference": "intent_...",
  "capabilityId": "subscription.renewing_within_days",
  "message": "certified deterministic chat message",
  "structuredResult": {},
  "clarification": null,
  "reasonCodes": [],
  "productionAuthorizationState": "not_approved"
}
```

For success, message, structured result, capability lineage, and evidence are
projected from certified chat, not written by the model. Non-success responses
expose bounded server guidance and codes, never raw provider errors or output.

## Parameter Contract

Nine capabilities accept no parameters. Any parameter is an error.
`subscription.renewing_within_days` requires exactly `days`: a true integer,
not boolean, float, or numeric string, with minimum 1 and maximum 366. Ambiguous
language yields clarification; no default is inferred.

## Provider Contract

- structured output only;
- tool/function calling disabled;
- one bounded attempt and zero retries in the first phase;
- server-selected provider/model only;
- bounded timeout, output tokens, and body size;
- deterministic validation before any execution;
- distinct bounded internal failures for unavailable, timeout, malformed,
  empty, and oversized responses; and
- provider exception text is never returned or persisted.

## Configuration Contract

```text
ASTRA_AI_INTENT_ENABLED=false
ASTRA_AI_INTENT_MODEL=<server owned>
ASTRA_AI_INTENT_TIMEOUT_SECONDS=8        # proposed
ASTRA_AI_INTENT_MAX_OUTPUT_TOKENS=256    # proposed
```

The architecture does not add settings now. Later implementation must preserve
a separate hard production prohibition.

## Privacy And Conversation Contract

Provider input is limited to the current question and eligible metadata. Raw
question/provider persistence is off by default. Safe metrics use references,
status, validated capability, latency/output buckets, and bounded failure codes.

Interpretation is current-turn by default. A candidate binds to the current
request, active principal-bound turn, metadata digest, and one-use short
lifetime. Logout, principal change, stale/non-active conversation, mismatch,
expiry, consumption, or Runtime restart invalidates it. No persistent or cross-
session memory is introduced.

## Certification Impact

The separate endpoint permits later certification of the new agent surface
without modifying certified `/astra/chat`. The existing gateway remains the only
bridge from validated declared intent into certified authority and execution.
