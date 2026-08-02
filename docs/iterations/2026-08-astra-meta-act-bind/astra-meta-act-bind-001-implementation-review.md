# ASTRA-META-ACT-BIND-001 Implementation Review

Status: Implemented / Pending Astra Review

Product Owner authorization: Approved on 2026-08-02.

## Summary

ASTRA-META-ACT-BIND-001 adds a narrow Runtime-owned governed metadata context
that binds a metadata request to the exact Runtime, conversation, current turn,
Subscription Manager app scope, certified capability, and certified
non-production activation.

This prerequisite exists so ASTRA-CHAT-001 does not hide parent metadata
activation changes inside chat.

## Backend Surface

New module:

```text
app/modules/astra_ai/metadata_activation_binding.py
```

Runtime methods:

```text
runtime.issue_subscription_manager_governed_metadata_context(...)
runtime.validates_governed_metadata_context(...)
```

No public API route, frontend, provider/model integration, SQL access,
execution bridge, schema, migration, production configuration, deployment, or
production authorization is added.

## Context Contract

The context binds:

```text
runtime_instance_id
conversation_id
current_turn_reference
request_reference
app_id
capability_scope
capability_id
capability_version
activation_reference
activation_digest
issued_at
expires_at
production_authorization_state = not_approved
version
```

The context is immutable, Runtime-issued, exact-object validated, bounded to one
Runtime/conversation/current turn/app/scope/capability, time-limited, and
non-production.

## Capability Provenance

Capability truth comes from the certified Subscription Manager read-authority
capability summaries:

```text
runtime.read_authority.capabilities()
```

The context issuer only supports Subscription Manager and rejects unsupported
capabilities. Intent Resolution does not trust a caller-supplied capability
tuple as capability truth.

## Metadata Engine Behavior

Capability Discovery remains metadata-only and app-agnostic by default. Generic
Runtime internal metadata requests without a governed metadata context keep the
existing certified Stage-0 behavior and do not gain Subscription Manager
private-read activation.

When a valid context is supplied, Capability Discovery may evaluate metadata
governance with the context's exact app and capability scope. It still returns
only generic metadata registry entries and does not register executable app
capabilities.

Intent Resolution remains declared-intent only. It may resolve the exact
certified app capability only when:

```text
declared target == governed metadata context capability
conversation/turn/request == context
Runtime/app/scope/version == context
context is exact Runtime-issued object
context is not expired
```

## Parent Preservation

ASTRA-RUNTIME-ACT-001 remains certified/frozen.

ASTRA-READ-AUTH-BIND-001 remains certified/approved/closed. This branch does
not modify `read_authority_binding.py` or its certified tests.

ASTRA-READ-EXEC-001 remains certified/approved.

ASTRA-CHAT-001 remains Changes Required / paused.

## Validation Evidence

```text
.venv/bin/python -m compileall app/modules/astra_ai/metadata_activation_binding.py app/modules/astra_ai/capability_discovery.py app/modules/astra_ai/intent_resolution.py app/modules/astra_ai/runtime.py tests/test_astra_metadata_activation_binding.py
passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py -q
9 passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py tests/test_astra_runtime_activation.py tests/test_astra_capability_discovery_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_conversation_context_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py -q
164 passed, 11 subtests passed

.venv/bin/python -m pytest tests/test_astra_read_authority_binding.py tests/test_astra_read_execution_bridge.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py -q
64 passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py tests/test_astra_runtime_activation.py tests/test_astra_capability_discovery_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_conversation_context_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_planning_engine.py tests/test_astra_read_authority_binding.py tests/test_astra_read_execution_bridge.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py -q
258 passed, 11 subtests passed

.venv/bin/python -m compileall app/modules/astra_ai app/modules/auth app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_metadata_activation_binding.py
passed

git diff --check
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
414 passed, 147 warnings, 33 subtests passed
```

## Explicit Non-Goals

No chat continuation, frontend, provider/model/OpenAI integration, LLM calls,
NLP, prompt interpretation, RAG, embeddings, persistent memory, adaptation,
autonomous agents, generic Tool Executor, writes, additional apps, schema,
migration, production configuration, deployment, production authorization, or
merge.
