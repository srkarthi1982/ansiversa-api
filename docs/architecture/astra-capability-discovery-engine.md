# Astra Capability Discovery Engine

**Status:** Implemented / Corrections Applied / Pending Astra Re-review
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

Capability metadata is released only after the Runtime-owned Governance Kernel
returns `allow` and the resulting bounded evidence is appended successfully.
Non-allow outcomes such as `fail_closed`, `refuse`, `contain`, `defer`, or
`clarify` produce no discovered capability records. Capability lookup is also
governance-gated; a non-allow outcome fails without returning metadata.

Operation sequence advancement happens only after evidence append succeeds, so
capacity or evidence failures do not create partial discovery progress.

---

# Request Context And Visibility

Discovery uses a governed requester context rather than caller-selected
visibility.

Supported requester classes:

- `public`;
- `authenticated` is modeled but unavailable in ASTRA-IMP-007 until a future
  authoritative authenticated-principal issuer exists;
- `internal_runtime`.

Visibility is capped by the trusted context:

- public requesters can see only public metadata;
- callers cannot self-assert authenticated visibility;
- internal runtime requesters can see internal metadata only when the context is
  issued by the owning `AstraRuntime` and carries its opaque runtime-owned
  authority token.

Callers cannot broaden visibility by passing a requested visibility above the
context ceiling. Knowing the runtime instance identifier is not sufficient to
mint internal discovery authority.

---

# Conversation Integration

Conversation-scoped discovery is informational only. A conversation snapshot
must be paired with the certified `AstraConversationContextEngine` that owns it.
The Capability Discovery Engine verifies the conversation type, runtime
ownership, engine ownership, snapshot freshness, and eligible lifecycle state
before discovery.

Fabricated, stale, foreign-runtime, unregistered, closed, or faulted
conversation snapshots are rejected before capability metadata is released. The
operation does not mutate conversation state and does not create planning or
execution paths.

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
Implementation Direction    Approved
Astra Re-review             Pending
Constitutional Conformance  Pending Astra Re-review
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-008               Not authorized
Requires separate authorization
```
