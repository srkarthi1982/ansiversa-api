# ASTRA-IMP-007 Registry Diagram

**Status:** Implemented / Pending Astra Source Review
**Production Authorization:** Not approved

---

# Runtime Placement

```text
AstraRuntime
      |
      +-- Configuration
      +-- Governance
      +-- Evidence Sink
      +-- Capability Discovery
              |
              +-- Sealed Capability Registry
                      |
                      +-- Immutable Capability Metadata
```

---

# Discovery Flow

```text
Caller
  |
  v
Runtime-owned discovery interface
  |
  v
Ready-state check
  |
  v
Registry metadata lookup
  |
  v
Governance evidence emission
  |
  v
Immutable discovery result
```

The flow does not call providers, execute tools, create plans, retrieve memory,
learn, persist data, expose APIs, or activate production behavior.

---

# Conversation-Scoped Discovery

```text
Conversation Snapshot
  |
  v
Runtime ownership check
  |
  v
Capability Discovery Engine
  |
  v
Metadata-only result
```

Conversation-scoped discovery is informational only.
