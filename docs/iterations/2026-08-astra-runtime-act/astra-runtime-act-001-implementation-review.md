# ASTRA-RUNTIME-ACT-001 Implementation Review

Status: Implemented / Changes Required / Pending Astra Re-Review.

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

## Astra Review Corrections

Activation is exact Runtime-owned authority. `AstraRuntimeActivationIssuer`
issues activation contracts, stores exact object identity in a Runtime-owned
registry, and invalidates that registry when Runtime shuts down. A structurally
valid activation object is not sufficient.

Governance requires all three pieces before activation can cover a disabled
Stage-0 request:

```text
exact activation_context object
activation_reference
activation_digest
```

The reference and digest are safe metadata. They are included in the serialized
governance input used for evidence hashing, and the activation reference is
included in the governance evidence provenance reference. The private Runtime
activation issuer and authority object are never serialized.

Activation is bound to the Runtime startup lifecycle. There is no short TTL and
no caller, frontend, API, database, or background renewal path. Runtime shutdown
invalidates the exact activation issuer and makes the previous activation
unusable.

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

Additional correction tests prove:

```text
caller/reconstructed activation -> direct Governance -> FAIL_CLOSED
copied activation -> direct Governance -> FAIL_CLOSED
tampered activation -> direct Governance -> FAIL_CLOSED
modified activation reference/digest -> FAIL_CLOSED
post-shutdown activation -> FAIL_CLOSED
safe activation provenance present in evidence
private Runtime authority absent from evidence
```
