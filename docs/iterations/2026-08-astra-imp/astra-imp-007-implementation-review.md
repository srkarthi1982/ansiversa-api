# ASTRA-IMP-007 Implementation Review Package

**Status:** Certified / Approved
**Task:** ASTRA-IMP-007
**Implementation Scope:** Capability Discovery Engine
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Discovery Findings

Codex inspected:

- `app/modules/astra_ai/runtime.py`, the certified Runtime Core;
- `app/modules/astra_ai/conversation_context.py`, the certified Conversation
  Context Engine;
- `app/modules/astra_ai/governance.py`, the certified Governance Kernel;
- `app/modules/astra_ai/evidence_sink.py`, the certified Evidence Sink;
- `app/modules/assistant/tools.py`, the existing Assistant tool registry;
- `app/modules/knowledge`, the existing public knowledge registry patterns.

Existing Assistant tool registries include executable handlers and are
therefore not imported into ASTRA-IMP-007. ASTRA-IMP-007 reuses the registry
shape but stores bounded metadata only.

No frozen constitutional document or implementation-readiness document required
modification.

---

# Implemented Surfaces

ASTRA-IMP-007 adds:

- `AstraCapabilityDiscoveryEngine`;
- `AstraCapabilityRegistry`;
- `AstraCapabilityMetadata`;
- `AstraCapabilityDiscoveryResult`;
- `AstraCapabilityHealthSnapshot`;
- capability type, status, visibility, and execution-authority enums.

Runtime Core receives a narrow ASTRA-IMP-007 compatibility extension so it owns
and registers exactly one Capability Discovery Engine.

---

# Astra Review Corrections

After source-level review of commit `7946f9df`, ASTRA-IMP-007 received three
targeted corrections:

- discovery and lookup now enforce the `GovernanceDecision` outcome before
  releasing capability metadata;
- requester visibility now comes from governed request context rather than
  caller-selected visibility;
- conversation-scoped discovery now verifies certified conversation engine
  ownership, snapshot freshness, runtime ownership, and eligible lifecycle
  state.

After source-level re-review of commit `3fb109eb`, ASTRA-IMP-007 received one
remaining authority-proof correction. Internal discovery contexts are now
issued only by the owning Runtime Core using an opaque runtime-owned authority
token, knowing the runtime instance identifier is insufficient to mint internal
authority, and authenticated visibility remains unavailable until a future
authoritative authenticated-principal issuer exists.

---

# Runtime Integration

The Runtime registers the Capability Discovery Engine during startup and
exposes lifecycle-aware discovery methods:

- `runtime.discover_capabilities(...)`;
- `runtime.get_capability(...)`;
- `runtime.capability_discovery.discover_for_conversation(...)`;
- `runtime.capability_discovery.health(...)`.

All operations require ready Runtime state at the time of use.

Discovery metadata is released only for `allow` governance outcomes after
bounded evidence append succeeds. Non-allow discovery outcomes return no
capabilities, and non-allow lookup outcomes fail without returning capability
metadata.

---

# Tests

Focused coverage is in:

```text
tests/test_astra_capability_discovery_engine.py
```

The tests cover immutable metadata, deterministic registry ordering, duplicate
rejection, unknown capability rejection, no public registry mutation method,
runtime registration, lifecycle-aware Runtime ownership, governance-aware
discovery evidence, non-allow metadata suppression, governed visibility
ceilings, runtime-issued internal authority contexts, rejection of forged and
foreign internal contexts, authenticated self-assertion rejection, no result
release before successful evidence append,
conversation-scoped informational discovery, fabricated/stale/foreign/closed
conversation rejection, structural health, and absence of provider, Tool
Executor, API, route, database, migration, embedding, vector, audit
persistence, and app-main imports.

Updated Runtime regression tests verify the new registered component remains
owned by Runtime and is cleared on shutdown/failure.

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
