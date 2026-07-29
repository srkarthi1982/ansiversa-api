# ASTRA-APP-VAL-001 Subscription Manager Governed Read Execution Validation

## Objective

Validate the governed Runtime-to-Subscription-Manager read execution path
implemented by ASTRA-READ-EXEC-001.

## Scope

ASTRA-APP-VAL-001 is validation-only. It observes and verifies the implemented
bridge, exact Runtime-issued execution request, read authorization boundary,
explicit adapter selection, app-owned read behavior, response contract,
fail-closed behavior, database-session ownership boundary, and production
boundary.

## Validation Scenarios

```text
runtime_produces_execution_request
read_authorization_enforced
adapter_selection_is_explicit
app_owned_read_executes
response_is_validated_and_redacted
unauthorized_and_malformed_fail_closed
database_session_boundary_proof
production_boundaries_unchanged
```

## Database-Session Boundary Proof

The validation runner uses a SQLAlchemy `Session` subclass that records
`Session.execute()` calls. A registered Subscription Manager adapter wrapper
asserts that no SQL execution has occurred before adapter entry, then delegates
to the certified app-owned adapter. The test verifies the first SQL execution
occurs inside the app adapter and that no session object or session field
appears in the returned Runtime result.

This proves central Astra transports the session opaquely for the current
implementation. A future stronger design may replace this transport with an
app-owned callable/service boundary.

## Not Authorized

```text
Frontend / Chat
Provider / Model
General Tool Executor
Additional app adapters
Write / Mutation execution
Production read execution
Production configuration
Database schema or migration changes
```

## Status

Certified / Approved after Astra source/security review, Partner review,
Product Owner approval, and certification closure.
