# ADR: ASTRA-IMP-006 Conversation Context Engine

**Status:** Proposed
**Date:** 2026-07-26
**Task:** ASTRA-IMP-006
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Context

ASTRA-IMP-005 certified the Runtime Core as the lifecycle owner for the Astra
foundations. The next implementation layer needs bounded conversation/session
representation before any provider, prompt, planning, memory, or execution
behavior can be considered.

---

# Decision

Implement `AstraConversationContextEngine` under
`app/modules/astra_ai/conversation_context.py`.

The engine:

- requires a ready certified `AstraRuntime` owner;
- creates immutable conversation metadata;
- returns immutable conversation snapshots instead of mutable session handles;
- enforces explicit lifecycle states;
- stores bounded current-turn metadata only;
- maintains bounded rolling short-context history;
- emits governance evidence through the Runtime Core;
- commits conversation mutations only after evidence append succeeds;
- enforces monotonic lifecycle and current-turn timestamps;
- provides structural health that references Runtime health;
- remains provider-independent and non-executing.

---

# Consequences

Astra gains a bounded internal conversation representation while preserving the
separation from memory, planning, execution, learning, providers, APIs,
databases, and production activation.

Conversation observation remains read-only. Runtime-owned engine operations are
the only mutation path, and failed evidence append leaves conversation state
unchanged.

ASTRA-IMP-007 remains unauthorized.

---

# Review State

```text
ASTRA-IMP-006               Implemented
Implementation Direction    Approved
Astra Re-review             Pending
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending
Production Authorization    Not approved
Production                  Unchanged
ASTRA-IMP-007               Not authorized
```
