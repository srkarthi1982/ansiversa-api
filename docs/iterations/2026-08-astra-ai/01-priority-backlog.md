# Astra AI Architecture Backlog

**Status:** ASTRA-001 frozen; ASTRA-002 frozen
**Implementation:** Not authorized

Only individually reviewed and authorized tasks may later move into
implementation. ASTRA-001 does not authorize any runtime work.

| ID | Task | Priority | Status | Outcome |
|---|---|---:|---|---|
| ASTRA-001 | Vision And Core Architecture | Critical | Frozen | Constitutional architecture, options, ownership, risks, and ADR accepted |
| ASTRA-002 | Platform Intelligence Architecture | Critical | Frozen | Define how Astra thinks: request understanding, intent, context, permission, capability, planning, local-sufficiency check, external-intelligence decision, decision evidence, and response |
| ASTRA-003 | Conversation And Context Architecture | Critical | Pending separate authorization | Documentation-only next phase; define chat/search/voice/contextual interface contracts plus context lifecycle |
| ASTRA-004 | Capability Discovery And Tool Architecture | High | Deferred | Define approved capability discovery, tool metadata, tool ownership, and no-fabrication controls |
| ASTRA-005 | Execution Planning Architecture | Critical | Deferred | Define planning model, impact classification, confirmation, rollback, and proposal behavior before execution |
| ASTRA-006 | External AI Provider Architecture | High | Deferred | Define provider selection, envelopes, routing, retention, failures, and provider-independent governance |
| ASTRA-007 | Memory And Learning Architecture | High | Deferred | Define retention, consent, deletion, export, learning boundaries, and no-silent-memory controls |

---

# Recommended Review Order

```text
ASTRA-001 Vision and core architecture
    ↓
Platform intelligence architecture
    ↓
Conversation and context architecture
    ↓
Capability discovery and tool architecture
    ↓
Execution planning architecture
    ↓
External AI provider architecture
    ↓
Memory and learning architecture
```

ASTRA-002 is approved and Frozen. ASTRA-003 is documentation only next and
requires separate Product Owner authorization before work begins. No
implementation task should start from ASTRA-002 until a separate implementation
scope is authorized.
