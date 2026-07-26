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
- enforces explicit lifecycle states;
- stores bounded current-turn metadata only;
- maintains bounded rolling short-context history;
- emits governance evidence through the Runtime Core;
- provides structural health that references Runtime health;
- remains provider-independent and non-executing.

---

# Consequences

Astra gains a bounded internal conversation representation while preserving the
separation from memory, planning, execution, learning, providers, APIs,
databases, and production activation.

ASTRA-IMP-007 remains unauthorized.

---

# Review State

```text
ASTRA-IMP-006               Implemented
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending
Production Authorization    Not approved
Production                  Unchanged
ASTRA-IMP-007               Not authorized
```
