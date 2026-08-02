# ASTRA-READ-AUTH-BIND-001 - Governed Read Authority & Capability Binding

Status: Implemented / Pending Astra Review

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
    -> app-owned Subscription Manager read grant
    -> ASTRA-IMP-010 authorization
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

Owner acceptance is derived from an exact app-owned Subscription Manager read
grant issued by Subscription Manager's private grant issuer. The grant remains
app-owned, one-time, principal-bound, request-bound, capability-bound, and
time-bounded.

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
binding module, shutdown invalidation, and bounded rejection behavior.

Existing certified parent tests for Runtime, Conversation Context, Capability
Discovery, Planning, Intent Resolution, Read Access Authorization, Read
Execution, and ASTRA-APP-VAL-001 remain part of the regression evidence.
