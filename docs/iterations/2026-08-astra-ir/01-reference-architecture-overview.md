# ASTRA-IR-001 Reference Architecture Overview

**Status:** Proposed
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

This overview identifies the future Astra implementation components and their
responsibility boundaries without defining implementation details.

---

# Reference Components

```text
Configuration Layer
        |
        v
Governance Engine
        |
        +--> Audit Engine
        +--> Observability
        |
        v
Core Intelligence Engine
        |
        +--> Conversation Engine
        +--> Context Engine
        +--> Capability Registry
        |
        v
Planner
        |
        v
Execution Gateway

Provider Gateway, Memory Engine, and Learning Engine attach only through
Governance Engine, Audit Engine, and their parent constitutional gates.
```

---

# Component Boundaries

- Core Intelligence Engine coordinates governed request flow.
- Conversation Engine owns conversation lifecycle, not durable memory.
- Context Engine assembles minimum necessary owner-authorized context.
- Capability Registry proves capability existence and metadata.
- Planner creates declarative plans and never executes.
- Execution Gateway governs handoff and preserves owning-service authority.
- Provider Gateway governs external-intelligence necessity and envelopes.
- Memory Engine governs memory decisions and never becomes an app datastore.
- Learning Engine governs adaptation and never rewrites the Constitution.
- Governance Engine applies constitutional precedence and fail-closed checks.
- Audit Engine produces bounded, privacy-minimized, integrity-aware evidence.
- Configuration Layer controls rollout boundaries and disabled-by-default
  behavior.
- Observability detects deviations without leaking sensitive data.
- Testing Framework validates conformance and certification gates.

---

# Non-Goals

This overview does not define classes, functions, schemas, routes, prompts,
tables, providers, deployment settings, tests, or production behavior.
