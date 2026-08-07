# ASTRA-AI-INTENT-001 — Governed Natural-Language Intent Implementation

Status: Changes Corrected / NOT CERTIFIED / Pending Astra Re-Review

Canonical task: `srkarthi1982/ansiversa-api#8`

Exact base: `00102d6669ff9021e7301f689d74090d760a2a03`

Branch: `feature/astra-ai-intent-001`

Certified architecture: `cc65502990e69c39bc542933d6d8d28aac5b0291`

Astra architecture review: `4881828844`

Astra implementation review: `4886169635`

Issue #8 correction gate: `5221470917`

Frontend agent integration: NOT AUTHORIZED

Production: NOT APPROVED

## Implemented Boundary

The authenticated `POST /api/v1/astra/agent/query` endpoint accepts only a
bounded current question and optional existing conversation and client request
references. Extra client fields are rejected before provider or chat execution.

The server first checks the ten narrowly defined canonical Subscription Manager
questions. Other current-turn questions may be sent to the separate
`OpenAIIntentProvider`, which uses one bounded OpenAI Responses API structured
output attempt with zero retries. No provider tool/function definitions exist.

The provider receives only:

- the current question;
- the allowed interpretation statuses; and
- a fresh metadata-only projection of enabled app-owned capabilities, versions,
  purposes, and parameter names/types/required state/bounds.

It receives no authenticated identity, subscription records, authorization,
grants, Runtime/Governance objects, database/session material, SQL, tools,
writes, or final-answer authority. Raw prompts and provider payloads are not
persisted as evidence.

## Deterministic Validation and Handoff

The strict candidate contains only `interpretation_status`, `app_id`,
`capability_id`, `parameters`, and `clarification_reason`; every level forbids
extra fields. A resolved candidate must name `subscription_manager`, match one
enabled capability in the fresh projection, remain current in a second
app-owned `capability_catalog()` check, and satisfy the exact parameter
contract. Nine reads accept no parameters. `subscription.renewing_within_days`
accepts exactly one true integer `days` value from 1 through 366.

Only a validated candidate becomes a server-owned `AstraChatDeclaredIntent`
inside the unchanged certified `AstraChatRequest`. The implementation invokes
the existing certified `AstraChatGateway` in-process. Its deterministic message
and structured DB result are returned without provider rewriting.

## Configuration and Environment

The server owns these default-off settings:

```text
ASTRA_AI_INTENT_ENABLED=false
ASTRA_AI_INTENT_MODEL=gpt-4.1-mini
ASTRA_AI_INTENT_TIMEOUT_SECONDS=8
ASTRA_AI_INTENT_MAX_OUTPUT_TOKENS=256
```

The provider also requires the existing platform AI master gate and an
environment-only OpenAI credential. Agent routes register only for
`local`, `development`, `qa`, and `staging`. `test` and production do not
register the route. Exact supported questions remain provider-independent when
the provider is unavailable, while the endpoint itself remains feature-gated.

## Verification Scope

Focused automated coverage includes:

- all canonical exact questions with no provider call;
- multiple materially different provider paraphrases for all ten reads;
- fresh app-catalog validation and unsupported-input no-guess behavior;
- strict day bounds and type validation;
- malformed, oversized, timeout, unavailable, authority-bearing, SQL/DB/tool,
  explanation, and prompt-injection failures with no chat execution;
- authentication, blocked-user, feature, environment, extra-field, and foreign
  conversation boundaries;
- a real authenticated agent HTTP proof where `count_all` changes from 2 to 3
  after a committed owner-scoped database insert; and
- a secondary authenticated user result of 1, proving owner isolation.

The Astra correction gate additionally proves all four previously missing
acceptance forms:

- a genuinely foreign `app_id` candidate returns invalid-provider-response and
  cannot invoke certified chat;
- an otherwise catalog-valid read capability omitted from the exact metadata
  projection supplied for the request is rejected before `AstraChatRequest`
  construction and chat execution;
- authenticated FastAPI requests carrying client-supplied app, capability,
  parameters, user, authority, grant, Runtime, or Governance fields return 422
  before provider or chat execution; and
- a real JSON array containing two candidate objects fails closed after one
  bounded provider attempt and cannot invoke chat.

Observed correction validation:

```text
focused intent/provider/agent       101 passed, 1 credential-gated skip
full tests/test_astra*.py           551 passed, 33 subtests passed,
                                    1 credential-gated skip
compileall                          passed
git diff --check                    passed
```

The real OpenAI smoke test is credential-gated and non-default. Without
`OPENAI_API_KEY`, its recorded status is `not run — credential gated`.

## Frozen and Excluded

No certified Runtime, metadata binding, read authority, read authorization,
read execution, chat, authentication, or Subscription Manager capability/
adapter semantics changed. No frontend, additional app, schema, migration,
MCP/plugin, RAG, embedding, memory, autonomous loop, write/action, merge,
manual deployment, production configuration, or production authorization is
included.

This implementation is not self-certified. The correction stops at Astra live
GitHub re-review.
