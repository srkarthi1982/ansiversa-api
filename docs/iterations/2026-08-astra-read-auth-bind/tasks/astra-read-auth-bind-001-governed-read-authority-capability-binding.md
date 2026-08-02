# ASTRA-READ-AUTH-BIND-001 - Governed Read Authority & Capability Binding

Status: Changes Required / Pending Astra Re-Review

Product Owner authorization: Approved on 2026-08-02.

## Objective

ASTRA-READ-AUTH-BIND-001 fills the prerequisite gap discovered during
ASTRA-CHAT-001 preflight. The certified Runtime already owned Conversation
Context, Intent Resolution, Read Access Authorization, and Governed Read
Execution, but normal Runtime-owned application code did not yet have a
certified way to bind app-owned Subscription Manager read capabilities and
Runtime-owned proof issuers into ASTRA-IMP-010.

This task introduces that binding without implementing chat, provider/model
integration, natural-language inference, SQL execution, persistence, frontend
work, production activation, or additional app adapters.

## Architecture

The implementation preserves the parent responsibilities:

- Capability Discovery remains metadata-oriented.
- Planning remains metadata-only and non-executable.
- Read Access Authorization remains the read decision authority.
- ASTRA-READ-EXEC-001 remains the governed read execution bridge.
- Subscription Manager remains the only executable app-owned read adapter.

The new `app/modules/astra_ai/read_authority_binding.py` module provides a
Runtime-owned read authority boundary. Runtime startup now creates a sealed
Subscription Manager read capability registry from the app-owned certified
declarations, creates exact Runtime-owned proof issuers, binds those issuers to
ASTRA-IMP-010, and exposes a narrow `runtime.read_authority` interface.

## Runtime Binding Flow

```text
Runtime startup
    -> app-owned Subscription Manager read declarations
    -> sealed AstraNamedReadCapabilityRegistry
    -> Runtime-owned proof issuers
    -> ASTRA-IMP-010 issuer binding
    -> runtime.read_authority interface
```

For a non-planning read authorization request:

```text
Conversation Context
    -> Intent Resolution
    -> Read Authority Binding
    -> existing backend auth-owned user context
    -> app-owned Subscription Manager owner acceptance
    -> Runtime-owned authority proofs
    -> ASTRA-IMP-010 authorization
    -> app-owned Subscription Manager read grant with actual read and
       Governance decision identity
    -> Runtime registration with ASTRA-READ-EXEC-001
```

Planning remains optional and absent for this read-only information path:

```text
plan_reference = None
plan = None
```

## Subscription Manager Scope

The only registered app-owned read capabilities are the certified Subscription
Manager capabilities:

- `subscription.count_all`
- `subscription.count_active`
- `subscription.list_active`
- `subscription.highest_cost`
- `subscription.total_recurring_cost`
- `subscription.monthly_cost_estimate`
- `subscription.renewing_this_month`
- `subscription.renewing_within_days`
- `subscription.overdue_renewals`
- `subscription.group_by_category`

The declarations remain in Subscription Manager through
`read_authorization_capabilities()`. Astra consumes those declarations but does
not duplicate Subscription Manager business logic.

## Authority Model

The binding component issues proof material only through Runtime-owned issuers
already bound to ASTRA-IMP-010:

- `principal`
- `user`
- `tenant`
- `app`
- `record`
- `field`
- `purpose`
- `owner_acceptance`

Owner acceptance is derived from an exact app-owned Subscription Manager owner
acceptance issued by Subscription Manager's private authority. The acceptance
is app-owned, principal-bound, capability-bound, field-bound, purpose-bound,
request-bound, and time-bounded.

The app-owned execution grant is issued only after ASTRA-IMP-010 returns the
actual `AUTHORIZED_METADATA_ONLY` decision. The grant binds that actual read
authorization decision identifier and the actual Governance decision reference;
the binding component does not predict or manufacture Governance decision IDs.

The Governance authorization input is bound to the certified
ASTRA-RUNTIME-ACT-001 Subscription Manager private-read activation scope:

```text
requested_app_id = subscription_manager
requested_capability_scope = subscription_manager:private_read
owner_authority_status = verified
```

Principal/user authority comes from a sealed backend-auth-owned
`AuthenticatedUserContext` issued only by the existing authenticated backend
request boundary. The context issuer requires bearer token or auth cookie
resolution, access-token decoding, token expiration binding, existing DB user
lookup by token subject/email, login-status validation, auth-owned SQLAlchemy
persistence validation, timing user binding, and a module-private
authenticated-request-boundary authority. A persistent user obtained directly
from `db.get(...)`, a transient caller-created `User(...)`, or a
caller-constructed context cannot establish read authority.

Subscription Manager has no tenant or organization authority model in this
repository. Read capability tenant scope is therefore represented explicitly as
`tenant:not_applicable`, not as a fabricated platform tenant.

## Boundaries

ASTRA-READ-AUTH-BIND-001 does not add:

- chat routes or chat service code;
- frontend code;
- provider/model calls;
- natural-language inference;
- SQL or database sessions in the binding component;
- schema or Alembic migrations;
- production configuration;
- write or mutation capability;
- additional app adapters;
- generic plugin registration.

Production authorization remains not approved.

## Validation

Focused tests prove Runtime startup registry binding, exact proof issuer
ownership, duplicate/foreign issuer rejection, normal Runtime-owned
authorization without validation-only private mutation, no Planning execution
shortcut, no Capability Discovery executable shortcut, no SQL surface in the
binding module, exact authenticated request-boundary context issuance,
persistent-DB-user-without-request rejection, direct context construction
rejection, copied/tampered/foreign/expired auth context rejection,
disabled/later-suspended user rejection, app-owned owner acceptance object
identity, copied/expired/foreign/tampered owner acceptance rejection, different
request reference/capability/version/parameters/result limit rejection,
field/purpose/parameter escalation rejection, exact issued read decision
validation, actual Governance decision identity binding, shutdown invalidation,
and bounded rejection behavior.

Existing certified parent tests for Runtime, Conversation Context, Capability
Discovery, Planning, Intent Resolution, Read Access Authorization, Read
Execution, and ASTRA-APP-VAL-001 remain part of the regression evidence.

Latest local validation:

```text
.venv/bin/python -m pytest tests/test_astra_read_authority_binding.py -q
23 passed

.venv/bin/python -m pytest tests/test_subscription_manager_astra_read_capabilities.py -q
20 passed

.venv/bin/python -m pytest tests/test_astra_runtime_activation.py tests/test_astra_read_authority_binding.py tests/test_astra_read_access_authorization_engine.py tests/test_astra_read_execution_bridge.py tests/test_astra_app_val_001_read_execution_validation.py tests/test_subscription_manager_astra_read_capabilities.py tests/test_astra_governance_kernel.py tests/test_astra_runtime_core.py tests/test_astra_configuration_foundation.py tests/test_astra_evidence_sink.py tests/test_astra_conversation_context_engine.py tests/test_astra_intent_resolution_engine.py tests/test_astra_planning_engine.py -q
259 passed, 25 subtests passed

.venv/bin/python -m compileall app/modules/auth app/modules/astra_ai app/modules/subscription_manager validation/astra_app_001 validation/astra_app_val_001 tests/test_astra_read_authority_binding.py tests/test_astra_runtime_activation.py tests/test_astra_read_execution_bridge.py tests/test_subscription_manager_astra_read_capabilities.py
passed

.venv/bin/python -m pytest tests/test_astra*.py -q
405 passed, 147 warnings, 33 subtests passed
```
