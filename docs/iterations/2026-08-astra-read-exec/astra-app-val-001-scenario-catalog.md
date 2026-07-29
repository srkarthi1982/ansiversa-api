# ASTRA-APP-VAL-001 Scenario Catalog

## Scenario Groups

### Runtime Request

`runtime_produces_execution_request`

Verifies the execution request is issued through `runtime.read_execution`, is
owned by the Runtime bridge, and carries Runtime request authority.

### Authorization

`read_authorization_enforced`

Verifies non-authorized read decisions cannot be registered for execution.

### Adapter Selection

`adapter_selection_is_explicit`

Verifies adapter lookup uses the explicit Subscription Manager
app/capability/version/operation tuple and that the adapter receives the request.

### App Read

`app_owned_read_executes`

Verifies the registered Subscription Manager adapter performs the read and
returns the expected authenticated-user result.

### Response Contract

`response_is_validated_and_redacted`

Verifies the Runtime result is structured, bounded, production-not-approved,
and free of forbidden authority/session/SQL/provider/prompt/private-path
material.

### Fail Closed

`unauthorized_and_malformed_fail_closed`

Verifies copied requests, reused requests/grants, bad execution contexts,
non-read operations, and subject mismatches fail closed.

### Session Boundary

`database_session_boundary_proof`

Verifies no SQL execution occurs before the registered app-owned adapter
receives the session.

### Production Boundary

`production_boundaries_unchanged`

Verifies production authorization remains `not_approved`, data mutation remains
`prohibited`, and schema mutation remains `prohibited`.
