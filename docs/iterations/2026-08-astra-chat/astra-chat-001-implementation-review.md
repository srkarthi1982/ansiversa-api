# ASTRA-CHAT-001 Implementation Review

Status: Implemented / Pending Astra Review

Product Owner authorization: Approved on 2026-08-02.

## Summary

ASTRA-CHAT-001 adds the first backend-only governed chat orchestration path.
It accepts an authenticated request with an explicit declared intent and routes
supported Subscription Manager reads through the certified Astra stack.

The implementation does not infer natural language, call a provider/model,
create a frontend chat UI, persist memory, execute arbitrary tools, perform
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
Discovery remains metadata-only. For this initial simple read path:

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
    -> AstraIntentResolutionEngine
    -> AstraCapabilityDiscoveryEngine metadata-only governance
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

The only parent-adjacent adjustment is narrow metadata governance binding:
Runtime-internal Capability Discovery and declared Subscription Manager
`get_information` intent governance now carry the certified
`subscription_manager:private_read` activation context, without adding
execution authority to either component.

## Failure Behavior

The chat gateway fails closed with bounded non-success responses for missing
intent, unsupported app, unsupported capability, foreign/stale conversation,
invalid authentication context, read authority rejection, governance/read
authorization denial, read execution rejection, field escalation, parameter
escalation, row-limit escalation, and malformed request contracts.

No fallback ungoverned execution exists.

## Validation Evidence

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

## Explicit Non-Goals

No frontend chat UI.

No provider/model/OpenAI integration.

No LLM calls.

No natural-language inference.

No RAG, embeddings, vector store, memory, adaptation, autonomous agents,
generic Tool Executor, writes, migrations, schemas, production configuration,
deployment, production authorization, or PR merge.
