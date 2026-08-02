# ASTRA-READ-AUTH-BIND-001 Implementation Review

Status: Implemented / Pending Astra Review

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
    -> app-owned Subscription Manager read grant
    -> ASTRA-IMP-010 authorization
    -> Runtime registration with ASTRA-READ-EXEC-001
```

The implementation relies on ASTRA-IMP-010 for the authorization decision and
ASTRA-READ-EXEC-001 for future execution. It does not execute the read.

## Security Notes

The binding component fails closed for unsupported capabilities, unresolved
intents, mismatched app grants, missing authenticated users, foreign Runtime
issuers, duplicate issuer classes, and shutdown Runtime handles.

The binding module does not import SQLAlchemy, own a database session, execute
SQL, or call Subscription Manager repositories.

## Remaining Limitations

ASTRA-CHAT-001 remains paused until this prerequisite is reviewed, approved,
and certified.

No provider/model integration exists.

No frontend chat exists.

Only Subscription Manager read-only capability binding exists.

Production authorization remains not approved.
