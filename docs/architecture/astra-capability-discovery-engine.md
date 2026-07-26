# Astra Capability Discovery Engine

**Status:** Implemented / Pending Astra Source Review
**Task:** ASTRA-IMP-007
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 through ASTRA-IMP-006 Certified / Approved
**Implementation Scope:** Capability Discovery Engine
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-008:** Not authorized

---

# Purpose

ASTRA-IMP-007 implements a provider-independent Capability Discovery Engine
owned by the certified Astra Runtime Core.

The engine discovers immutable capability metadata only. It does not execute
capabilities, create plans, call providers, create prompts, invoke models,
retrieve memory, learn, expose APIs, persist data, or activate production
behavior.

---

# Discovery Findings

Codex inspected:

- certified Runtime Core lifecycle and component-registration patterns;
- certified Conversation Context Engine runtime ownership and evidence
  integration;
- certified Governance Kernel bounded evaluation contracts;
- existing Assistant tool registry patterns;
- existing Knowledge registry patterns.

Assistant tool registries contain executable handlers, so ASTRA-IMP-007 does
not wire to them directly. It reuses the registry pattern only and stores
metadata-only capability records.

---

# Capability Model

Capability metadata is immutable and bounded:

- `capability_id`;
- `capability_name`;
- `capability_type`;
- `owning_module`;
- `version`;
- `status`;
- `visibility`;
- `governance_reference`;
- `execution_authority`;
- `description`.

`execution_authority` is metadata only. It does not grant execution authority
and does not contain executable references.

---

# Registry Structure

`AstraCapabilityRegistry` is sealed after deterministic construction.

Rules:

- records are registered in deterministic capability-id order;
- duplicate capability identifiers fail;
- unknown capability lookup fails;
- discovery returns immutable metadata copies;
- public mutation methods are not exposed;
- disabled and deprecated records are excluded unless explicitly requested.

---

# Runtime Ownership

`AstraRuntime` registers exactly one `AstraCapabilityDiscoveryEngine` during
startup alongside the certified foundation components.

Runtime-owned discovery uses:

- `runtime.discover_capabilities(...)`;
- `runtime.get_capability(...)`;
- `runtime.capability_discovery.discover_for_conversation(...)`;
- `runtime.capability_discovery.health(...)`.

All operational access checks Runtime ready state at use time. Handles obtained
before shutdown cannot discover or look up capabilities after shutdown.

---

# Governance And Evidence

Discovery operations emit bounded governance evidence through Runtime Core.

Governance evidence does not turn discovery into execution authority. The
engine records the governance outcome in discovery results, while returned
capability records remain metadata-only.

---

# Conversation Integration

Conversation-scoped discovery is informational only. A conversation snapshot
may be used to verify runtime ownership before discovery, but the operation
does not mutate conversation state and does not create planning or execution
paths.

---

# Structural Health

Capability health reports only:

- registry loaded;
- capability count;
- duplicate-free state;
- registry validity;
- structural health outcome.

It does not report provider status, planning status, execution status, user
activity, memory state, or production readiness.

---

# Final Draft State

```text
ASTRA-IMP-007               Implemented
Implementation Scope        Capability Discovery Engine
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-008               Not authorized
Requires separate authorization
```
