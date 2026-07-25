# Astra AI Architecture Backlog

**Status:** ASTRA-001 frozen; ASTRA-002 frozen; ASTRA-003 frozen; ASTRA-004 frozen; ASTRA-005 frozen; ASTRA-006 proposed
**Implementation:** Not authorized

Only individually reviewed and authorized tasks may later move into
implementation. ASTRA-001 does not authorize any runtime work.

| ID | Task | Priority | Status | Outcome |
|---|---|---:|---|---|
| ASTRA-001 | Vision And Core Architecture | Critical | Frozen | Constitutional architecture, options, ownership, risks, and ADR accepted |
| ASTRA-002 | Platform Intelligence Architecture | Critical | Frozen | Define how Astra thinks: request understanding, intent, context, permission, capability, planning, local-sufficiency check, external-intelligence decision, decision evidence, and response |
| ASTRA-003 | Conversation And Context Architecture | Critical | Frozen | Define conversation lifecycle, context classes, state, assembly, providers, authority resolution, isolation, expiration, clarification, privacy, and future interface support |
| ASTRA-004 | Capability Discovery And Tool Architecture | High | Frozen | Define approved capability discovery, tool metadata, tool ownership, and no-fabrication controls |
| ASTRA-005 | Execution Planning And Action Governance | Critical | Frozen | Define declarative execution plans, actions, execution steps, approval gates, approval binding, idempotency, retry, rollback, compensation, cancellation, delegation, evidence, and planner/executor boundaries |
| ASTRA-006 | Tool Execution Architecture | Critical | Proposed | Define execution requests, responses, acceptance, rejection, authorization recheck, owner validation, idempotency enforcement, monitoring, timeout reconciliation, retries, cancellation, evidence, and Planner versus Executor ownership boundaries |
| ASTRA-007 | External Intelligence And Provider Architecture | High | Deferred | Define provider selection, envelopes, routing, retention, failures, token governance, evidence, and provider-independent governance |
| ASTRA-008 | Memory Architecture | High | Deferred | Define conversation, working memory, long-term memory, Knowledge, user context, expiration, ownership, privacy, and forgetting rules |
| ASTRA-009 | Learning And Adaptation Architecture | High | Deferred | Define explainable personalization, repeated corrections, preferred workflows, adaptive planning, and no-opaque-training boundaries |
| ASTRA-010 | Safety, Audit And Governance Architecture | Critical | Deferred | Define auditing, traceability, AI evidence, governance logs, explainability, security, compliance, and constitutional enforcement |

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
Tool execution architecture
    ↓
External intelligence and provider architecture
    ↓
Memory architecture
    ↓
Learning and adaptation architecture
    ↓
Safety, audit, and governance architecture
```

ASTRA-002 is approved and Frozen. ASTRA-003 is approved and Frozen as the
conversation and context architecture layer. ASTRA-004 is approved and Frozen
as the capability discovery and tool architecture layer. ASTRA-005 Execution
Planning and Action Governance is approved and Frozen after Astra re-review of
commit `ffe6710` and Product Owner approval. ASTRA-006 Tool Execution
Architecture is Proposed after documentation and architecture authorization and
is pending Astra review. No implementation task should start from ASTRA-004,
ASTRA-005, or ASTRA-006 unless a separate implementation scope is authorized.
