# ASTRA-CHAT-001 Implementation Review

Status: Certified / Approved

Certified executable:
`4d7d25fd1f95ef7fd3912a1cdc21ef43729e8646`.

Astra certification review: `4876497721`.

PR #3: Open, draft, unmerged; based on certified
ASTRA-META-ACT-BIND-001.

Production authorization: Not approved.

Product Owner/Astra resume authorization: Approved on 2026-08-06 for controlled
non-production development and QA only.

Reconciliation commit:
`4d7d25fd1f95ef7fd3912a1cdc21ef43729e8646`.

Certified prerequisite branch head:
`06de785da513e04c19f1c59c1ec4a72ac0d42d28`.

Certified metadata implementation:
`0715483147d5a1a0ba6180d5a63e489f3b6fd982`.

Certified metadata review: `4839188883`.

Astra blocker review `4838708303` required reconciliation onto the certified
metadata prerequisite. The existing chat history was preserved and merged
non-destructively with the certified prerequisite history.

## Summary

ASTRA-CHAT-001 adds the first backend-only governed chat orchestration path.
It accepts an authenticated request with an explicit declared intent and routes
supported Subscription Manager reads through the certified Astra stack.

The implementation does not infer natural language, call a provider/model,
modify or wire the existing frontend Astra UI, persist memory, execute arbitrary tools, perform
writes, add schemas/migrations, or authorize production.

## Backend Surface

Route:

```text
POST /api/v1/astra/chat
```

Runtime module:

```text
app/modules/astra_ai/chat_gateway.py
```

API module:

```text
app/modules/astra_ai/api/chat.py
```

The route requires the existing backend authenticated request boundary through
`get_authenticated_user_context`. It never accepts caller-supplied user IDs as
authority.

## Request Contract

The initial request is bounded and explicit:

```text
conversation_id optional
declared_intent optional
declared_intent.app_id
declared_intent.declared_action
declared_intent.declared_subject
declared_intent.capability_id
declared_intent.parameters
requested_field_references optional
requested_row_limit optional
client_request_reference optional
```

Missing declared intent returns clarification. Unsupported apps or
capabilities return bounded unavailable responses.

## Supported Intent Mapping

Natural-language inference is absent. The only successful initial shape is a
declared `get_information` request for Subscription Manager subscription data,
with `capability_id` matching one of the certified Subscription Manager read
adapter capabilities:

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

Intent Resolution remains the certified declared-intent resolver. Capability
Discovery remains metadata-only. The chat gateway validates the declared
capability against the app-owned capability catalog, then calls
`runtime.issue_subscription_manager_governed_metadata_context(...)`. The same
exact Runtime-issued context object is supplied to the intent request and the
conversation-bound Capability Discovery requester context. The declared target
must resolve to exactly the certified context capability before read authority
is requested. For this initial simple read path:

```text
plan_reference = None
plan = None
```

## Governed Execution Chain

The positive path is:

```text
get_authenticated_user_context
    -> AstraChatGateway
    -> AstraConversationContextEngine
    -> runtime.issue_subscription_manager_governed_metadata_context(...)
    -> AstraIntentResolutionEngine
    -> AstraCapabilityDiscoveryEngine discover_for_conversation(...)
    -> runtime.read_authority.authorize_subscription_manager_read(...)
    -> ASTRA-IMP-010 Read Access Authorization
    -> Subscription Manager app-owned grant
    -> runtime.read_execution.issue_request(...)
    -> runtime.read_execution.execute(...)
    -> Subscription Manager registered adapter
    -> deterministic bounded chat response
```

The chat gateway does not import SQLAlchemy, own a database session, call
Subscription Manager repositories, or execute SQL. The API route passes the
existing Subscription Manager database dependency only into the certified Read
Execution bridge so the app-owned adapter remains the first SQL boundary.

## Parent Preservation

ASTRA-RUNTIME-ACT-001 remains certified/frozen.

ASTRA-READ-AUTH-BIND-001 remains certified/approved/closed.

ASTRA-READ-EXEC-001 remains certified/approved.

Capability Discovery remains metadata-only. Intent Resolution remains
declared-intent only. Planning remains metadata-only and non-executable.

The reconciliation resolves parent-component conflicts in favor of certified
ASTRA-META-ACT-BIND-001. The old chat-owned `governance_app_id`,
`governance_capability_scope`, `governance_capability_id`, request-carried
`declared_capability_ids`, `_validate_resolved_capability_lineage(...)`, and
modified Read Authority fixture do not survive. There is no chat-owned delta in
the certified Capability Discovery, Intent Resolution, Read Authority Binding,
or their certified fixtures relative to the prerequisite branch.

Chat verifies exact capability lineage at its orchestration boundary:

```text
declared capability
    -> declared-intent binding target
    -> Runtime-issued governed metadata context
    -> AstraIntentRequest declared target and same exact context
    -> resolved_capability_ids
    -> Read Authority adapter_capability_id
    -> Read Execution adapter_capability_id
```

Mismatched, changed, or reused capability lineage fails closed.

## Response Projection

Chat response protection is structural. The gateway projects Subscription
Manager results through allowlisted summary and record fields and rejects
unsupported private metadata keys. It does not keyword-scan app-owned business
values, so legitimate values such as `1Password` and `SQL Server` remain
returnable when the governed capability authorizes those fields. Projection
failures are converted to bounded non-success chat responses.

## Failure Behavior

The chat gateway fails closed with bounded non-success responses for missing
intent, unsupported app, unsupported capability, foreign/stale conversation,
invalid authentication context, read authority rejection, governance/read
authorization denial, read execution rejection, field escalation, parameter
escalation, row-limit escalation, and malformed request contracts.

No fallback ungoverned execution exists.

## Database Provenance Proof

The authenticated HTTP integration test seeds two owner-scoped Subscription
Manager rows, calls `POST /api/v1/astra/chat` with
`subscription.count_all`, and receives `Subscriptions: 2.`. It then commits a
third row through the test database session, repeats the same governed HTTP
request, and receives `Subscriptions: 3.`. The answer path traverses HTTP auth,
chat orchestration, governed metadata context, Intent Resolution, Read Authority,
Read Access Authorization, Read Execution, the registered app-owned adapter,
and the Subscription Manager database.

The gateway imports no SQLAlchemy API and does not call a Subscription Manager
repository or execute SQL directly.

## Test Clock Correction

The activation lifecycle test mixed a wall-clock-loaded Runtime configuration
with fixed August 2/3 evaluation timestamps. It now freezes Runtime
configuration loading to the scenario's existing `NOW` value. Production
activation semantics, lifetime, freshness validation, and fail-closed behavior
are unchanged. Existing metadata activation tests continue to prove expired and
stale contexts fail closed.

## Validation Evidence

```text
.venv/bin/python -m pytest tests/test_astra_chat_gateway.py -q
27 passed, 1 warning

.venv/bin/python -m pytest tests/test_astra_chat_gateway.py tests/test_astra_metadata_activation_binding.py tests/test_astra_runtime_activation.py tests/test_astra_capability_discovery_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_conversation_context_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_read_authority_binding.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_read_execution_bridge.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py -q
264 passed, 1 warning, 11 subtests passed in 53.90s

.venv/bin/python -m compileall app/modules/astra_ai app/modules/auth app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_chat_gateway.py
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
450 passed, 147 warnings, 33 subtests passed in 427.11s

git diff --check
passed
```

## Explicit Non-Goals

No frontend integration. The existing frontend Astra panel remains unchanged.

No provider/model/OpenAI integration.

No LLM calls.

No natural-language inference.

No RAG, embeddings, vector store, memory, adaptation, autonomous agents,
generic Tool Executor, writes, migrations, schemas, production configuration,
deployment, production authorization, or PR merge.
