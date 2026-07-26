# ASTRA-IR-001 Component Breakdown

**Status:** Proposed
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Component Matrix

| Component | Responsibility | Ownership | Primary Interfaces | Certification Focus |
|---|---|---|---|---|
| Core Intelligence Engine | Governed request flow and response planning | Astra AI platform | request, decision, response, evidence | deterministic outcomes |
| Conversation Engine | Conversation lifecycle and transient state | Astra AI platform | session, turn, state, expiry | isolation and no silent memory |
| Context Engine | Need-driven context assembly | Astra AI platform and owning services | context request, context envelope | minimization and ownership |
| Capability Registry | Capability discovery metadata | Owning services and Astra coordination | capability metadata, availability | no fabrication |
| Planner | Declarative execution plan construction | Astra AI platform | plan, step, approval requirement | no execution during planning |
| Execution Gateway | Governed handoff to owner execution | Astra AI platform and owning services | execution request, acceptance, result | owner acceptance |
| Provider Gateway | External intelligence governance | Astra AI platform | eligibility, envelope, provider result | provider independence |
| Memory Engine | Memory write, retrieval, retention, deletion, export governance | Astra AI platform | memory decision, memory reference | ownership and retrieval authorization |
| Learning Engine | Adaptation eligibility and activation governance | Astra AI platform | adaptation decision, conflict result | no hidden drift |
| Governance Engine | Constitutional precedence and policy decisions | Astra AI platform | governance decision, safety class | fail-closed behavior |
| Audit Engine | Evidence, integrity, access, retention, export, deletion | Astra AI platform | evidence record, integrity metadata | sufficiency and minimization |
| Configuration Layer | Feature flags, policy settings, rollout state | Platform infrastructure | configuration decision | disabled by default |
| Observability | Runtime visibility and deviation detection | Platform operations | event, metric, alert | redaction |
| Testing Framework | Conformance and certification validation | Engineering | test evidence, certification report | repeatability |

---

# Boundary Rule

Components may depend on each other only through approved contracts. Direct
access to app-owned databases, bypassing owner services, or treating prompts,
providers, memory, adaptation, or user preference as authority remains
prohibited.
