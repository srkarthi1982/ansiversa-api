# Astra AI Architecture Backlog

**Status:** ASTRA-001 frozen; later tasks pending authorization
**Implementation:** Not authorized

Only individually reviewed and authorized tasks may later move into
implementation. ASTRA-001 does not authorize any runtime work.

| ID | Task | Priority | Status | Outcome |
|---|---|---:|---|---|
| ASTRA-001 | Vision And Core Architecture | Critical | Frozen | Constitutional architecture, options, ownership, risks, and ADR accepted |
| ASTRA-002 | Conversation And Interface Contract | Critical | Pending separate authorization | Documentation-only next phase; define chat/search/voice/contextual interface contracts |
| ASTRA-003 | Context And Memory Architecture | Critical | Deferred | Define retention, consent, deletion, export, and model-context boundaries |
| ASTRA-004 | Planning And Action Proposal Contract | High | Deferred | Define planning model, impact classification, confirmation, and refusal rules |
| ASTRA-005 | Controlled Execution Readiness | Critical | Deferred | Define execution gates, audit, rollback, and production-readiness evidence |
| ASTRA-006 | Cross-App Orchestration Architecture | High | Deferred | Define app-owned coordination without central app-data ownership |
| ASTRA-007 | Interface Expansion Strategy | Medium | Deferred | Define voice, notifications, command palette, and workflow UI sequencing |

---

# Recommended Review Order

```text
ASTRA-001 Vision and core architecture
    ↓
Conversation/interface contract
    ↓
Context and memory architecture
    ↓
Planning/action proposal contract
    ↓
Controlled execution readiness
    ↓
Cross-app orchestration
```

ASTRA-001 is reviewed, approved, and Frozen. No later task should start without
separate Product Owner authorization and Astra review scope.
