# ASTRA-IMP-007 Implementation Review Package

**Status:** Implemented / Pending Astra Source Review
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

# Runtime Integration

The Runtime registers the Capability Discovery Engine during startup and
exposes lifecycle-aware discovery methods:

- `runtime.discover_capabilities(...)`;
- `runtime.get_capability(...)`;
- `runtime.capability_discovery.discover_for_conversation(...)`;
- `runtime.capability_discovery.health(...)`.

All operations require ready Runtime state at the time of use.

---

# Tests

Focused coverage is in:

```text
tests/test_astra_capability_discovery_engine.py
```

The tests cover immutable metadata, deterministic registry ordering, duplicate
rejection, unknown capability rejection, no public registry mutation method,
runtime registration, lifecycle-aware Runtime ownership, governance-aware
discovery evidence, conversation-scoped informational discovery, structural
health, and absence of provider, Tool Executor, API, route, database,
migration, embedding, vector, audit persistence, and app-main imports.

Updated Runtime regression tests verify the new registered component remains
owned by Runtime and is cleared on shutdown/failure.

---

# Review State

```text
ASTRA-IMP-007               Implemented
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending
Production Authorization    Not approved
Production                  Unchanged
ASTRA-IMP-008               Not authorized
```
