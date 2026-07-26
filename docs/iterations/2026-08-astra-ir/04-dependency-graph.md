# ASTRA-IR-001 Dependency Graph

**Status:** Proposed
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Dependency Graph

```text
Configuration Layer
        |
        v
Governance Engine
        |
        +--> Audit Engine
        |       |
        |       v
        |   Observability
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

Provider Gateway
        ^ depends on Governance, Audit, Configuration, Core Intelligence

Memory Engine
        ^ depends on Governance, Audit, Configuration, Context

Learning Engine
        ^ depends on Governance, Audit, Configuration, Memory

Testing Framework
        ^ validates all components and contracts
```

---

# Dependency Rules

- Governance Engine precedes high-impact behavior.
- Audit Engine precedes state-changing, provider, memory, learning, and
  production-sensitive behavior.
- Configuration Layer precedes rollout and production activation.
- Provider Gateway depends on local sufficiency and provider governance.
- Memory Engine depends on ownership, retrieval authorization, retention,
  deletion, and export governance.
- Learning Engine depends on adaptation activation and conflict governance.
- Execution Gateway depends on planning and owning-service acceptance.

---

# Independent Build Candidates

Potentially independent planning tracks:

- Configuration Layer readiness
- Audit evidence model readiness
- Testing Framework readiness
- Component contract inventory
- Observability redaction requirements

These tracks still require separate implementation authorization before code.
