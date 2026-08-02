# ASTRA-RUNTIME-ACT-001 Implementation Review

Status: Implemented / Pending Astra Review.

Date: 2026-08-02.

## Summary

ASTRA-RUNTIME-ACT-001 adds a separate governed non-production activation layer
for the first narrow Astra operational capability. It preserves the Stage-0
global disabled baseline and does not turn Astra on globally.

## Changed Runtime Surface

Runtime now owns a read-only activation snapshot:

```text
runtime.activation
runtime.health(...).activation
```

The snapshot is metadata-only and exposes no authority tokens, secrets, user
data, provider payloads, prompts, SQL, database handles, or mutation controls.

## Governance Change

`GovernanceEvaluationInput` now includes optional Runtime-owned activation
metadata:

```text
runtime_instance_id
requested_app_id
requested_capability_scope
activation_context
```

The fields are optional and backward compatible. Existing callers without
activation retain the previous fail-closed behavior under the disabled Stage-0
configuration.

Runtime injects its own activation context into governance evaluation and
overrides caller-supplied activation material.

## Explicit Non-Goals

This implementation does not add:

```text
chat
frontend
provider/model integration
natural-language inference
memory
adaptation
writes
general tool execution
additional applications
database persistence
schema or migration changes
production configuration
deployment
production authorization
```

## Validation Target

Focused tests prove:

```text
valid non-production activation + exact Subscription Manager private-read scope
    -> real Governance Kernel
    -> ALLOW

same request without activation
    -> FAIL_CLOSED

production with activation requested
    -> fail closed before activation is usable
```

No governance monkeypatch is used.
