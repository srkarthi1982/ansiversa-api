# Astra AI Architecture Backlog

**Status:** ASTRA-001 frozen; ASTRA-002 frozen; ASTRA-003 frozen; ASTRA-004 frozen; ASTRA-005 frozen; ASTRA-006 frozen; ASTRA-007 frozen; ASTRA-008 frozen; ASTRA-009 frozen; ASTRA-010 proposed
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
| ASTRA-006 | Tool Execution Architecture | Critical | Frozen | Define execution requests, responses, admission, owner acceptance, rejection, authorization recheck, owner validation, cross-owner boundaries, idempotency enforcement, monitoring, timeout reconciliation, retries, cancellation, evidence, and Planner versus Executor ownership boundaries |
| ASTRA-007 | External Intelligence And Provider Architecture | High | Frozen | Define local-first necessity, provider independence, eligibility, selection, envelopes, routing, prompt governance, response validation, failures, token and cost governance, privacy, evidence, and provider-independent governance |
| ASTRA-008 | Memory Architecture | High | Frozen | Define what Astra may remember, what it must forget, conversation state, working memory, long-term memory, preferences, memory ownership and references, retrieval authorization, app-owned data boundaries, retrieval, retention, deletion, export, audit, privacy, and forgetting rules |
| ASTRA-009 | Learning And Adaptation Architecture | High | Frozen | Define learning, adaptation, learning versus memory, explainable personalization, correction handling, feedback classification, preference evolution, eligibility, activation, conflict resolution, confidence, drift prevention, provider/model boundaries, and no-opaque-training boundaries |
| ASTRA-010 | Safety, Audit And Constitutional Governance Architecture | Critical | Proposed | Define the Astra Constitution model, constitutional precedence, safety boundaries, governance validation, audit evidence, explainability, violation handling, approval authority, implementation/production gates, compliance, emergency restrictions, amendments, and cross-architecture conflict resolution |

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
Architecture is approved and Frozen after Astra re-review of commit `0d01e3f8`
and Product Owner approval. ASTRA-007 External Intelligence And Provider
Architecture is approved and Frozen after Astra re-review of commit `fa0c6919`
and Product Owner approval. No implementation task should start from
ASTRA-004, ASTRA-005, ASTRA-006, or ASTRA-007 unless a separate implementation
scope is authorized. ASTRA-008 Memory Architecture is approved and Frozen
after Astra re-review of commit `ce14300` and Product Owner approval. No
implementation task should start from ASTRA-008 unless a separate
implementation scope is authorized. ASTRA-009 Learning And Adaptation
Architecture is approved and Frozen after Astra re-review of commit `3db6222`
and Product Owner approval. No implementation task should start from ASTRA-009
unless a separate implementation scope is authorized. ASTRA-010 Safety, Audit
And Constitutional Governance Architecture is Proposed after documentation and
architecture authorization. Astra approved the architecture direction for
commit `2af0a3b` and requested two targeted documentation refinements. The ADR
is Proposed. ASTRA-010 inherits ASTRA-001 through ASTRA-009 and defines the
umbrella constitutional governance,
precedence, safety, audit, evidence, explainability, violation, approval,
implementation-gate, production-gate, conformance, emergency-restriction, and
amendment model. The current revision bounds Product Owner authorization by
binding constraints and the accepted Constitution, and adds audit-evidence
integrity and correction governance. No implementation task should start from
ASTRA-010 unless a separate implementation scope is authorized.
