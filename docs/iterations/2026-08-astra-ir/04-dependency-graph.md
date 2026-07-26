# ASTRA-IR-001 Dependency Graph

**Status:** Approved and Frozen
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Dependency Graph

This graph shows baseline build order. Mature runtime collaboration may be
bidirectional, but bootstrap dependencies must remain acyclic.

```text
Stage 0: Constitutional Contracts
        |
        v
Stage 1: Minimal Configuration Foundation
        |
        v
Stage 2: Minimal Governance Kernel
        |
        v
Stage 3: Minimal Evidence Sink
        |
        v
Stage 4: Full Governance And Audit Integration
        |
        v
Stage 5: Higher Components
        |
        +--> Conversation Engine
        +--> Context Engine
        +--> Capability Registry
        +--> Core Intelligence Engine
        +--> Planner
        +--> Execution Gateway
        +--> Provider Gateway
        +--> Memory Engine
        +--> Learning Engine
        +--> Observability

Testing Framework
        ^ certification dependency for all stages
```

---

# Dependency Classes

| Dependency Class | Meaning |
|---|---|
| Prerequisite | Must exist before dependent work begins |
| Runtime collaborator | Interacts after both components exist |
| Optional extension | Adds later capability without blocking base component |
| Certification dependency | Required before approval or release |
| Production dependency | Required before production activation |

---

# Dependency Rules

- Circular runtime collaboration must not become an unresolved implementation
  bootstrap cycle.
- Configuration Layer starts with a minimal disabled-by-default foundation that
  does not depend on Governance Engine or Observability.
- Governance Engine starts with a minimal kernel that can emit bounded evidence
  without requiring the full Audit Engine.
- Audit Engine starts with a minimal evidence sink that has no governance
  decision authority.
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
