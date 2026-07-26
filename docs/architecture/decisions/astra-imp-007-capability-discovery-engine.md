# ADR: ASTRA-IMP-007 Capability Discovery Engine

**Status:** Accepted
**Date:** 2026-07-26
**Task:** ASTRA-IMP-007
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Context

ASTRA-IMP-006 certified bounded conversation context. Before planning,
providers, memory, learning, or execution can be considered, Astra needs a
deterministic way to discover what platform capabilities exist.

Discovery must not become execution authority.

---

# Decision

Implement `AstraCapabilityDiscoveryEngine` under
`app/modules/astra_ai/capability_discovery.py`.

The engine:

- requires Runtime ownership;
- exposes immutable capability metadata only;
- uses a sealed read-only registry;
- rejects duplicate and unknown capability identifiers;
- returns deterministic discovery ordering;
- integrates with Runtime Core as a registered component;
- emits bounded governance evidence through Runtime Core;
- releases discovery metadata only after an `allow` governance outcome and
  successful evidence append;
- keeps non-allow discovery outcomes metadata-empty and non-allow lookups
  metadata-denied;
- keeps public discovery limited to public metadata, keeps authenticated
  discovery unavailable until an authoritative issuer exists, and requires
  internal discovery contexts to be issued by the owning Runtime Core;
- supports conversation-scoped informational discovery through certified
  Conversation Context Engine ownership verification;
- exposes structural capability health;
- remains provider-independent and non-executing.

---

# Consequences

Astra gains governed awareness of available capabilities while preserving the
separation from planning, execution, provider interaction, memory, learning,
APIs, databases, and production activation.

ASTRA-IMP-008 remains unauthorized.

---

# Review State

```text
ASTRA-IMP-007               Certified / Approved
Implementation Direction    Approved
Astra Re-review             Approved
Constitutional Conformance  Approved
Product Owner Approval      Approved
Certification               Passed
Production Authorization    Not approved
Production                  Unchanged
ASTRA-IMP-008               Not authorized
```
