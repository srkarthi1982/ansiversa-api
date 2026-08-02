# ASTRA-RUNTIME-ACT-001 — Governed Non-Production Runtime Activation

Status: Implemented / Pending Astra Review.

Date: 2026-08-02.

## Objective

Introduce a separate Runtime activation contract that allows a narrow
non-production Astra capability to pass the real Governance Kernel without
changing the frozen Stage-0 configuration contract.

## Scope

The first activation covers only:

```text
Subscription Manager
governed authenticated private read authorization
non-production only
```

It does not authorize chat, frontend behavior, provider/model use, memory,
adaptation, writes, general tools, additional applications, production
execution, persistence, schema changes, migrations, production configuration,
or deployment.

## Implementation

The implementation adds:

```text
app/modules/astra_ai/activation.py
```

The activation loader consumes the backend-owned setting:

```text
ASTRA_NONPROD_READ_ENABLED
```

The setting defaults to `false`. Unknown values fail closed. Production
activation is prohibited even when the setting is true.

Runtime loads activation at startup and injects Runtime-owned activation context
into governance evaluation. Callers cannot activate Runtime behavior through API
input, mutable Runtime state, database rows, frontend controls, or caller-owned
tokens.

## Governance Boundary

Stage-0 `AstraConfigurationContract.feature_enabled` remains disabled by
default and continues to reject direct global enablement.

When Stage-0 remains disabled, Governance can allow only if a valid activation
context covers the exact request:

```text
runtime instance
non-production environment
read-only/advisory authority
PRIVATE_READ safety
subscription_manager app
subscription_manager:private_read scope
provider/memory/adaptation/execution handoff not requested
production authorization NOT_APPROVED
```

Activation is necessary but not sufficient. The regular governance fail-closed,
approval, consent, owner-authority, runtime-use, production, and constitutional
checks still apply.

## Current Downstream State

```text
ASTRA-READ-AUTH-BIND-001    Paused pending activation review/certification
ASTRA-CHAT-001              Authorized / Paused
Production                  NOT APPROVED
```
