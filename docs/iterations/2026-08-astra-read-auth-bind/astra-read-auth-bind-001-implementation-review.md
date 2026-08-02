# ASTRA-READ-AUTH-BIND-001 Implementation Review

Status: Changes Required / Pending Astra Re-Review

## Summary

ASTRA-READ-AUTH-BIND-001 introduces the Runtime-owned read authority binding
needed before ASTRA-CHAT-001 can continue. The implementation makes the
Subscription Manager read authorization path usable from normal Runtime-owned
application code while preserving certified parent responsibilities.

## Changed Runtime Surface

The Runtime now exposes:

```text
runtime.read_authority.capabilities()
runtime.read_authority.authorize_subscription_manager_read(...)
```

This surface does not expose proof issuer tokens, registration authority,
mutable registries, SQLAlchemy sessions, database handles, SQL, app grants, or
private Runtime authority material.

## Certified Parent Preservation

Capability Discovery executable semantics changed: NO.

Planning executable semantics changed: NO.

Read authorization requirements weakened: NO.

Read execution requirements weakened: NO.

## Authorization Path

```text
app-owned read capability
    -> Runtime sealed registry bootstrap
    -> Runtime-owned proof issuers
    -> existing backend auth-owned user context
    -> app-owned Subscription Manager owner acceptance
    -> ASTRA-IMP-010 authorization
    -> app-owned Subscription Manager read grant with actual read and
       Governance decision identity
    -> Runtime registration with ASTRA-READ-EXEC-001
```

The implementation relies on ASTRA-IMP-010 for the authorization decision and
ASTRA-READ-EXEC-001 for future execution. It does not execute the read.

The corrected path preserves the two-phase authority flow:

```text
application preauthorization / owner acceptance
    -> real Governance decision through Runtime
    -> post-authorization execution grant containing the actual Governance
       decision identity
```

The binding does not predict Governance decision IDs. It fails closed unless
ASTRA-IMP-010 returns `AUTHORIZED_METADATA_ONLY`, then uses that actual decision
identifier and the actual Governance decision reference in the Subscription
Manager grant.

Read authorization now binds the certified ASTRA-RUNTIME-ACT-001 activation
scope into Governance input through `requested_app_id=subscription_manager` and
`requested_capability_scope=subscription_manager:private_read`.

Principal/user authority comes from a sealed `AuthenticatedUserContext` issued
by the existing backend auth service for a persistent DB-loaded user. A
transient caller-created `User(...)` does not establish read authority.

Subscription Manager read capabilities express the absence of a tenant model as
`tenant:not_applicable`. This is not a tenant, organization, workspace, or role
authority.

## Security Notes

The binding component fails closed for unsupported capabilities, unresolved
intents, mismatched app authority, missing backend auth-owned context,
transient caller-created users, inactive users, copied/expired/foreign/tampered
owner acceptance, different request reference, different capability/version,
different parameters, different result limit, copied/tampered read decisions,
foreign Runtime issuers, duplicate issuer classes, field/purpose/parameter
escalation, and shutdown Runtime handles.

The binding module does not import SQLAlchemy, own a database session, execute
SQL, or call Subscription Manager repositories.

## Validation Evidence

```text
.venv/bin/python -m pytest tests/test_astra_read_authority_binding.py -q
20 passed

.venv/bin/python -m pytest tests/test_subscription_manager_astra_read_capabilities.py -q
20 passed

.venv/bin/python -m pytest tests/test_astra_runtime_activation.py tests/test_astra_read_authority_binding.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_read_execution_bridge.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_configuration_foundation.py tests/test_astra_evidence_sink.py tests/test_astra_conversation_context_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_planning_engine.py -q
256 passed, 25 subtests passed

.venv/bin/python -m compileall app/modules/auth app/modules/astra_ai app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_read_authority_binding.py tests/test_astra_runtime_activation.py tests/test_astra_read_execution_bridge.py tests/test_subscription_manager_astra_read_capabilities.py
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
402 passed, 147 warnings, 33 subtests passed
```

## Remaining Limitations

ASTRA-CHAT-001 remains paused until this prerequisite is reviewed, approved,
and certified.

No provider/model integration exists.

No frontend chat exists.

Only Subscription Manager read-only capability binding exists.

Production authorization remains not approved.
