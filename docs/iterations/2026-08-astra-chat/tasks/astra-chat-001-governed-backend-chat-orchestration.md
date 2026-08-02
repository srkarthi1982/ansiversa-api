# ASTRA-CHAT-001 - Governed Backend Chat Orchestration

Status: Implemented / Pending Astra Review

Product Owner authorization: Approved on 2026-08-02.

## Objective

Implement the first backend-only Astra chat orchestration path on top of the
certified Runtime activation, read authority binding, read authorization, read
execution, and Subscription Manager app-owned read adapter foundations.

## Scope

ASTRA-CHAT-001 introduces:

- a narrow authenticated backend chat route;
- a deterministic declared-intent request contract;
- principal-bound in-memory conversation ownership;
- orchestration through Conversation Context, Intent Resolution, metadata-only
  Capability Discovery, Read Authority Binding, Read Access Authorization, Read
  Execution, and the Subscription Manager registered adapter;
- bounded structured chat responses.

It does not introduce frontend chat, provider/model calls, natural-language
inference, RAG, embeddings, persistent memory, autonomous tool execution,
writes, schema changes, migrations, production configuration, deployment, or
production authorization.

## Route

```text
POST /api/v1/astra/chat
```

The route is registered only in known non-production environments and still
fails closed unless certified Runtime startup and non-production read
activation are valid.

## Request And Response

Request model:

```text
AstraChatRequest
```

Response model:

```text
AstraChatResponse
```

The response may contain safe identifiers, status, resolved intent reference,
capability ID, response kind, deterministic message, bounded structured result,
reason codes, clarification state, safe evidence references, and read/Governance
decision references. It does not expose tokens, owner acceptance objects,
private Runtime authority material, SQL, database handles, provider payloads,
prompts, or secrets.

## Declared Intent Mapping

The initial successful intent is explicit:

```text
declared_action = get_information
declared_subject = subscription
app_id = subscription_manager
capability_id = one certified Subscription Manager read adapter capability
```

Supported adapter capabilities:

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

Unsupported, missing, ambiguous, or invalid declared intent does not trigger
inference. It returns a bounded clarification or unavailable response.

## Security Boundary

The gateway requires `AuthenticatedUserContext` from the existing backend auth
boundary and validates conversations against the authenticated principal. A
caller cannot provide or substitute user IDs, owner IDs, foreign principals,
foreign conversations, read authorizations, app grants, or Runtime authority.

The chat gateway does not directly execute SQL and does not call Subscription
Manager repositories. The only app data path is the certified Read Execution
bridge invoking the registered Subscription Manager adapter.

## Validation

Focused tests cover successful governed Subscription Manager read orchestration,
absence of governance monkeypatching in the positive path, exact principal
conversation binding, foreign conversation rejection, missing declared intent
clarification, unsupported app/capability rejection, no direct SQL/repository
surface in the gateway, no bypass of Read Authority Binding, no bypass of Read
Execution, caller-supplied owner/user ID rejection, parameter/field/row-limit
escalation rejection, bounded read authorization/Governance denial, no
provider/model/NLP path, and unauthenticated API rejection.

Latest validation:

```text
.venv/bin/python -m pytest tests/test_astra_chat_gateway.py -q
12 passed, 1 warning

.venv/bin/python -m pytest tests/test_astra_intent_resolution_engine.py tests/test_astra_capability_discovery_engine.py -q
48 passed

.venv/bin/python -m pytest tests/test_astra_runtime_activation.py tests/test_astra_read_authority_binding.py tests/test_astra_read_execution_bridge.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py tests/test_astra_conversation_context_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_capability_discovery_engine.py tests/test_astra_planning_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_chat_gateway.py -q
261 passed, 1 warning, 11 subtests passed

.venv/bin/python -m compileall app/modules/astra_ai app/modules/auth app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_chat_gateway.py
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
417 passed, 147 warnings, 33 subtests passed in 438.66s
```
