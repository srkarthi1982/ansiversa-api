# ASTRA-META-ACT-BIND-001 - Governed Metadata Activation & Capability Context Binding

Status: Changes Required / Pending Astra Re-Review

Product Owner authorization: Approved on 2026-08-02.

## Objective

Provide the missing certified prerequisite between Runtime activation and
metadata governance so ASTRA-CHAT-001 can later consume exact app/capability
metadata lineage without modifying frozen parents silently.

## Implemented Scope

ASTRA-META-ACT-BIND-001 introduces a Runtime-owned governed metadata context
for Subscription Manager only. It binds:

```text
Runtime
conversation
current turn
request reference
application
capability scope
exact certified capability
certified activation provenance
bounded lifetime
```

The context grants no execution authority and no read authorization. It is only
metadata governance context.

## Capability Provenance Source

The source of capability truth is the certified read-authority capability
summary exposed by the existing sealed Subscription Manager read registry:

```text
runtime.read_authority.capabilities()
```

Unsupported capabilities, wrong app, wrong scope, wrong version, and fabricated
contexts fail closed.

## Metadata Behavior

Capability Discovery remains metadata-only and app-agnostic by default. A valid
Runtime-owned governed metadata context is required before metadata governance
can evaluate as `subscription_manager:private_read`.

Intent Resolution remains declared-intent only. It resolves a certified
Subscription Manager capability only when the declared target matches the exact
trusted governed metadata context, and the Capability Discovery requester
context carries that same exact Runtime-issued context object.

## Security Coverage

Focused tests prove fail-closed behavior for:

```text
caller-created context
copied context
tampered context
foreign Runtime context
foreign conversation context
foreign turn context
expired/stale context
stale turn reuse through Capability Discovery
stale request-reference reuse through Capability Discovery
wrong app
wrong capability scope
unsupported capability
capability version mismatch
declared capability changed after context issuance
declared capability not equal to trusted context capability
different valid context split between Intent Resolution and Capability Discovery
governed discovery context without matching governed intent context
Subscription Manager context reused for another app
generic internal metadata request gaining activation without trusted context
disabled activation context issuance
caller-created issuer
```

Positive tests prove:

```text
certified non-production activation
    -> exact Runtime
    -> certified Subscription Manager capability
    -> Runtime-owned metadata context
    -> Capability Discovery metadata governance
    -> Intent Resolution
    -> exact resolved capability lineage
```

No SQL, app read execution, provider/model call, or chat route is involved.

## Validation Evidence

```text
.venv/bin/python -m compileall app/modules/astra_ai/metadata_activation_binding.py app/modules/astra_ai/capability_discovery.py app/modules/astra_ai/intent_resolution.py app/modules/astra_ai/runtime.py tests/test_astra_metadata_activation_binding.py
passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py -q
11 passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py tests/test_astra_runtime_activation.py tests/test_astra_capability_discovery_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_conversation_context_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py -q
166 passed, 11 subtests passed

.venv/bin/python -m pytest tests/test_astra_read_authority_binding.py tests/test_astra_read_execution_bridge.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py -q
64 passed

.venv/bin/python -m pytest tests/test_astra_metadata_activation_binding.py tests/test_astra_runtime_activation.py tests/test_astra_capability_discovery_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_conversation_context_engine.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_planning_engine.py tests/test_astra_read_authority_binding.py tests/test_astra_read_execution_bridge.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py -q
260 passed, 11 subtests passed

.venv/bin/python -m compileall app/modules/astra_ai app/modules/auth app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_metadata_activation_binding.py
passed

git diff --check
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
416 passed, 147 warnings, 33 subtests passed
```
