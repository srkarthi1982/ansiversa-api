# ASTRA-AI-INTENT-ARCH-001 — Governed Natural-Language Intent Architecture

Status: Architecture Approved / Certified / Closed

Certified architecture:
`cc65502990e69c39bc542933d6d8d28aac5b0291`.

Astra architecture review: `4881828844`.

PR #6: open, draft, unmerged.

Implementation: **NOT AUTHORIZED**.

Authorization: GitHub issue `srkarthi1982/ansiversa-api#5`, gate-release comment
`5215395273`.

Architecture base: backend commit
`615ef1b3ec375aacca9a9a9cb564832688a0d34c`.

Certified chat executable:
`4d7d25fd1f95ef7fd3912a1cdc21ef43729e8646`, Astra review
`4876497721`.

Production authorization: **NOT APPROVED**.

## Purpose

This proposal adds one narrow, untrusted language-interpretation boundary in
front of the certified Astra chat path. It does not implement that boundary.

```text
current user question
    -> deterministic exact-question fast path
       OR bounded provider interpretation
    -> untrusted candidate intent
    -> deterministic exact capability and parameter validation
    -> certified AstraChatRequest
    -> certified AstraChatGateway
    -> certified authority, authorization, execution, and app-owned read
    -> bounded deterministic response
```

The permanent ownership rule is:

```text
Applications own capabilities. Astra owns orchestration.
```

Subscription Manager continues to own capability definitions, parameter
schemas, business semantics, the read adapter, and its data. Astra coordinates
interpretation and validation. Runtime and Governance continue to own
activation, provenance, authorization, grants, and execution boundaries. A
provider owns none of these.

## New Trust Boundary

The proposed `AstraNaturalLanguageIntentInterpreter` accepts only:

- the current user question; and
- a metadata-only projection of eligible, certified, app-owned capabilities and
  their parameter schemas.

It returns only an untrusted candidate. Provider output is treated exactly like
untrusted caller input. It cannot be passed directly to Read Authority, Read
Execution, an application adapter, or a database.

The candidate may express only:

```text
interpretation_status
app_id
capability_id
parameters
clarification_reason
```

Allowed statuses are `resolved`, `clarification_required`, and `unsupported`.
The schema forbids extra fields. Authority-looking fields make the entire
candidate invalid; they are not silently ignored.

The interpreter cannot establish or carry a user ID, owner ID, role,
permission, authorization, grant, tenant, activation, Runtime authority,
Governance decision, database identity, SQL, or provider tool execution.

## Authority Separation

The model never becomes execution authority because four independent gates
remain outside it:

1. the server selects eligible metadata from the app-owned certified catalog;
2. a deterministic validator requires one exact supplied capability and its
   exact parameter contract;
3. the server constructs the declared-intent `AstraChatRequest`; and
4. the unchanged certified chat, Runtime, Governance, Read Authority, Read
   Access Authorization, Read Execution, and app-owned adapter chain makes all
   authority and ownership decisions.

Model confidence is not an execution field. A candidate is data, not proof.

## Capability Provenance

The sole authority-bearing pilot catalog remains:

```text
app/modules/subscription_manager/astra_read_capabilities.py
    capability_catalog()
```

The ten eligible capabilities are:

```text
subscription.count_all
subscription.count_active
subscription.list_active
subscription.highest_cost
subscription.total_recurring_cost
subscription.monthly_cost_estimate
subscription.renewing_this_month
subscription.renewing_within_days
subscription.overdue_renewals
subscription.group_by_category
```

A future metadata projector may derive a purpose description, exact capability
ID, version, allowed parameter names, parameter types/ranges, and status from
that catalog. The projection is not a second registry and cannot add, enable,
rename, or broaden capabilities. A capability absent from the fresh projection
is rejected even if it looks plausible.

## Deterministic Fast Path

Today's exact supported question mapping remains the first path. A future
backend agent boundary should own an equivalent sealed mapping so non-frontend
clients receive the same provider-independent behavior.

```text
exact supported normalized question?
    yes -> deterministic candidate -> validation -> certified chat
    no  -> provider candidate -> validation -> certified chat or no execution
```

Exact questions continue when the provider is disabled, unavailable, or timed
out. The fast path must not widen matching through fuzzy or semantic rules.

## Deterministic Candidate Validation

Validation is fail-closed and ordered:

1. parse a bounded structured response with `extra=forbid`;
2. reject oversized, malformed, multiple-candidate, or authority-bearing output;
3. require an allowed interpretation status;
4. for `resolved`, require exactly `app_id=subscription_manager`;
5. require exactly one capability ID present in the server-supplied metadata;
6. verify it is still enabled in the app-owned certified catalog;
7. reject every parameter not declared by that capability;
8. independently validate parameter type, cardinality, and range;
9. require no parameters for the nine non-parameterized capabilities;
10. require exactly integer `days` in `1..366` for
    `subscription.renewing_within_days`;
11. bind the candidate to the current request, principal-bound conversation
    turn, eligible-metadata digest, and a short one-use lifetime; and
12. construct a new server-owned `AstraChatRequest`; never accept a client-built
    resolved intent at the natural-language endpoint.

Ambiguous wording never supplies a default. “How much are my subscriptions?”
must clarify recurring totals versus normalized monthly estimate. “Soon” must
clarify the day window.

## Recommended API Boundary

Use a new authenticated endpoint:

```text
POST /api/v1/astra/agent/query
```

This is safer than extending `/api/v1/astra/chat` because certified chat accepts
declared intent, whereas the new endpoint accepts natural language and adds
provider availability, candidate validation, and new failure states. Separation:

- leaves the certified route, request schema, and gateway unchanged;
- prevents natural language from being confused with trusted declared intent;
- permits an independent default-off feature gate;
- isolates provider latency and failure from certified chat; and
- makes later certification scope explicit.

The new route would call `AstraChatGateway` in-process after validation. It must
not call `/api/v1/astra/chat` over HTTP and must not depend on
`/api/v1/assistant/query`.

## Provider Input Boundary

The provider envelope is minimal and purpose-bound:

```text
current_question
eligible_capabilities[]:
  app_id
  capability_id
  short purpose
  allowed_parameters[]:
    name
    primitive type
    required state
    minimum/maximum where applicable
allowed_statuses
output_schema_version
```

It contains no subscription records, names, prices, billing data, database URL,
SQL, auth token, cookie, user object, email, user/owner identifier, read grant,
authorization object, Governance evidence, Runtime authority, activation object,
previous private provider payload, or cross-session history.

## No Tools And No Model-Written Answer

Provider tool/function calling is disabled and rejected. No generic Tool
Executor, dynamic plugin, MCP, database tool, HTTP tool, write action, or
provider-controlled follow-up is available.

The model performs only `natural language -> untrusted candidate intent`. It
does not receive DB results and does not generate the final answer. The
certified deterministic DB-backed response stays authoritative. Later natural-
language response rendering requires a separate governed work item.

## Failure Model

| Condition | Outcome | Execution |
|---|---|---|
| Exact deterministic resolution | `resolved` to one validated capability | Certified chat path |
| Model resolves one valid candidate | `resolved` after independent validation | Certified chat path |
| Ambiguous wording or missing value | `clarification_required` with bounded reason | None |
| Unsupported app, write, action, or capability | `unsupported` | None |
| Provider disabled/unavailable/timed out | exact path works; unmatched input returns bounded unavailable guidance | None for unmatched input |
| Malformed, oversized, extra-field, or multi-candidate output | bounded invalid-provider-response failure | None |
| Stale/replayed/foreign candidate | bounded stale-or-invalid interpretation failure | None |

No fallback guesses a capability.

## Conversation And Memory Boundary

The first implementation should interpret the current turn only. It introduces
no persistent memory, cross-session behavioral memory, vector memory, profile
learning, or personalization.

If a later separately approved clarification flow needs context, it may retain
only `conversation_id`, the immediately preceding bounded clarification code,
unresolved capability-choice identifiers or missing parameter names, and the
originating request reference. Storage must be existing in-memory, principal-
bound Conversation Context; lifetime must not exceed the active conversation
and turn. Logout, principal change, reset, IDLE/CLOSING/CLOSED/FAULTED state,
unrelated turn advance, expiry, or Runtime restart invalidates it. Raw prompts
and provider output are not clarification memory.

## Existing Provider Infrastructure Findings

The shared Assistant uses `app/modules/assistant/openai_provider.py` and the
OpenAI Responses HTTP API. It provides:

- an `AssistantAnswerProvider` protocol and `OpenAIResponseProvider` client;
- server-side API key, model, timeout, max-token, and temperature settings;
- `AI_GATEWAY_ENABLED` and `ASSISTANT_OPENAI_ENABLED` gates;
- an `httpx.Client` timeout;
- safe public errors for HTTP, JSON, and empty-output failure;
- deterministic fallback when unavailable; and
- environment-only secret loading through Pydantic settings.

It has no retry policy. The first intent phase should likewise use zero retries
and one bounded attempt. It extracts free text rather than validating structured
output, and its prompt contract is public answer generation. It therefore cannot
serve as the governed intent authority or parser.

Reusable ideas are the small provider protocol, server-owned settings, bounded
HTTP client, generic unavailable exception, timeout, and disabled behavior. A
future intent client needs its own strict schema, minimal envelope, size limit,
redaction-safe observability, and no dependency on Assistant service, route,
prompt, knowledge context, actions, tools, or response modes.

## Configuration Proposal

Future server-owned settings should be:

```text
ASTRA_AI_INTENT_ENABLED=false
ASTRA_AI_INTENT_MODEL=<server-selected model>
ASTRA_AI_INTENT_TIMEOUT_SECONDS=<bounded value, proposed 8>
ASTRA_AI_INTENT_MAX_OUTPUT_TOKENS=<bounded value, proposed 256>
```

The feature is honored only in `local`, `development`, `qa`, and `staging`.
Production remains unavailable even if the flag is accidentally true until
separate Product Owner authorization. Client input cannot enable or select a
provider/model. Credentials remain environment secrets.

## Observability And Privacy

Safe evidence may include request and interpretation references, schema/metadata
digest, status, validated capability ID, server-owned provider/model alias,
latency bucket, output-size bucket, and bounded failure code.

Do not log or persist tokens, cookies, credentials, DB URLs, SQL, Runtime
authority, grants, authorization objects, provider bodies, private records, or
raw user prompt text. Use stable reason codes, never provider exception bodies.
Raw prompts are not Astra evidence by default.

## Later Test Architecture

Future implementation must cover:

- multiple paraphrases for each of the ten capabilities;
- all exact mappings with provider disabled and failing;
- recurring-total/monthly-estimate and missing-day ambiguity;
- unsupported writes, admin impersonation, injection, SQL/DB, prompt, and
  cross-app requests;
- hallucinated, not-supplied, disabled, and cross-app capability IDs;
- missing, extra, duplicate, string, fractional, zero, negative, `9999`, `1`,
  and `366` day parameters;
- malformed JSON, extra/authority fields, multiple candidates, empty and
  oversized output;
- provider disabled, unavailable, timeout, and no-retry behavior;
- replay, expiry, stale turn, logout, principal change, and Runtime restart;
- frontend attempts to submit a resolved capability to the natural-language
  route;
- absence of tool/HTTP/DB/write surface;
- authenticated owner isolation; and
- real browser/API/app/DB provenance: known answer, normal UI mutation, changed
  paraphrased answer, and isolated secondary-user answer.

## Anticipated Later Implementation Surface

Only after separate approval, narrow implementation is expected to add:

```text
app/modules/astra_ai/natural_language_intent.py
app/modules/astra_ai/api/agent.py
intent-specific request/response schemas
intent-specific provider client/abstraction
server settings and safe .env.example placeholders
tests for intent, endpoint, security, provider failure, and provenance
documentation/source-pack status updates
```

It should register a non-production route, project the existing app-owned
catalog, preserve exact mapping, validate one candidate, construct the existing
`AstraChatRequest`, and invoke the existing gateway. Certified components must
not be edited unless a future issue explicitly identifies certification impact.

## Frozen Components Remaining Untouched

This architecture task changes no executable source. Frozen and untouched:

```text
ASTRA-RUNTIME-ACT-001
ASTRA-READ-AUTH-BIND-001
ASTRA-META-ACT-BIND-001
ASTRA-READ-EXEC-001
ASTRA-CHAT-001
ASTRA-FE-CHAT-001
Subscription Manager capability catalog/adapter
authentication boundary
databases, schemas, and migrations
```

## Architecture Review Answers

1. The boundary is current question plus permitted metadata to an intent-only
   interpreter returning an untrusted candidate.
2. Deterministic validation and certified authority remain server-owned.
3. The canonical list comes from Subscription Manager `capability_catalog()`.
4. A candidate absent from the fresh supplied projection is rejected.
5. Exact per-capability validation enforces parameters; `days` is integer 1–366.
6. Provider input is current question plus minimal eligible metadata.
7. Records, identity, auth, authority, grants, governance/runtime objects, SQL,
   DB details, and secrets are prohibited.
8. The model cannot call tools.
9. The model cannot access the DB.
10. It cannot select a user; owner scope remains in certified backend controls.
11. Ambiguity returns clarification with no execution.
12. Exact mappings continue; unmatched input gets bounded unavailable guidance.
13. Yes, exact questions remain provider-independent.
14. Use `/api/v1/astra/agent/query` to isolate the new boundary and preserve
    certified `/astra/chat`.
15. Reuse generic protocol/HTTP/settings/error patterns, not Assistant authority
    or answer behavior.
16. `ASTRA_AI_INTENT_ENABLED=false`, server-owned and non-production-only.
17. Later changes are the narrow interpreter, route, provider client, schemas,
    settings placeholders, tests, and docs listed above.
18. All certified Runtime, metadata, authority, execution, chat, frontend,
    authentication, and Subscription Manager executable components are untouched.

## Certified State

```text
ASTRA-AI-INTENT-ARCH-001 — Architecture Approved / Certified / Closed
Implementation — NOT AUTHORIZED
Production — NOT APPROVED
```

The architecture was certified at the commit above. This documentation-only
closure is not a new architecture target. No implementation begins until a
separate GitHub implementation issue is explicitly authorized by Product
Owner/Astra.
