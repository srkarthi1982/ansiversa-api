# ASTRA-IMP-007 Registry Diagram

**Status:** Certified / Approved
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
Governed request context validation
  |
  +-- public context: public ceiling only
  +-- authenticated context: unavailable until authorized issuer exists
  +-- internal context: Runtime-issued token required
  |
  v
Governance evidence emission
  |
  v
Allow?
  |
  +-- no --> Empty discovery result / denied lookup
  |
  +-- yes
        |
        v
Registry metadata lookup within visibility ceiling
  |
  v
Immutable discovery result
```

The flow does not call providers, execute tools, create plans, retrieve memory,
learn, persist data, expose APIs, or activate production behavior.

---

# Conversation-Scoped Discovery

```text
Conversation Engine + Snapshot
  |
  v
Certified type and ownership check
  |
  v
Snapshot freshness and lifecycle check
  |
  v
Capability Discovery Engine
  |
  v
Metadata-only result
```

Conversation-scoped discovery is informational only.
