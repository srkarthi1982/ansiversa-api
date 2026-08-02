# ASTRA-RUNTIME-ACT-001 Implementation Review

Status: Certified / Approved.

Date: 2026-08-02.

Certification Commit: `a15b3192572cd5a1f3e265652e4778967755b787`.

Certification Review: PR #2 Astra review `4837966223`.

Repository State At Certification: PR #2 open, draft, unmerged, and mergeable.

## Summary

ASTRA-RUNTIME-ACT-001 adds a separate governed non-production activation layer
for the first narrow Astra operational capability. It preserves the Stage-0
global disabled baseline and does not turn Astra on globally.

Final Astra re-review certified the implementation after the exact Runtime
owner binding correction. Activation issuer ownership requires a nominal
`AstraRuntime`, matching startup instance id, and exact Runtime-owned activation
authority; owner-shaped fake objects are rejected.

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
construction requires a nominal `AstraRuntime` owner, matching Runtime startup
instance id, and the exact opaque activation issuer authority owned by that
Runtime. Owner-shaped caller objects with matching attributes or callbacks are
not accepted as Runtime owners. Direct issuer issuance also requires that exact
Runtime authority, and normal activation issuance happens only through
`load_runtime_activation()` after the server-owned `ASTRA_NONPROD_READ_ENABLED`
gate passes. The standalone trusted issuer factory was removed. Runtime startup
registers the exact issuer, issued activation contracts retain exact issuer
identity, validation checks that the exact issuer belongs to the live Runtime
and remains registered, and Runtime shutdown invalidates the issuer registry
entry. A structurally valid activation object is not sufficient.

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
standalone trusted issuer factory is not exposed
caller-created activation issuer with caller-owned authority -> construction rejected
owner-shaped fake Runtime object with matching authority/callback -> construction rejected
direct issuer issuance without Runtime authority -> rejected
server-flag-disabled Runtime issuer activation -> FAIL_CLOSED
caller/reconstructed activation -> direct Governance -> FAIL_CLOSED
copied activation -> direct Governance -> FAIL_CLOSED
tampered activation -> direct Governance -> FAIL_CLOSED
foreign Runtime activation -> direct Governance -> FAIL_CLOSED
modified activation reference/digest -> FAIL_CLOSED
post-shutdown activation -> FAIL_CLOSED
exact live Runtime-issued activation -> real Governance Kernel -> ALLOW
safe activation provenance present in evidence
private Runtime authority absent from evidence
```
