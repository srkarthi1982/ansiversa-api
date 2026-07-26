# ASTRA-IR-001 Component Breakdown

**Status:** Approved and Frozen
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Component Matrix

| Component | Responsibility | Ownership | Dependency Classification | Certification Focus |
|---|---|---|---|---|
| Core Intelligence Engine | Governed request flow and response planning | Astra AI platform | Prerequisite: Governance Kernel; Runtime collaborators: Context, Capability, Planner; Certification: Audit evidence | deterministic outcomes |
| Conversation Engine | Conversation lifecycle and transient state | Astra AI platform | Prerequisite: conversation contract; Runtime collaborator: Context Engine; Certification: Audit evidence | isolation and no silent memory |
| Context Engine | Need-driven context assembly | Astra AI platform and owning services | Prerequisite: context contract; Runtime collaborator: Conversation Engine; Production: Configuration Layer | minimization and ownership |
| Capability Registry | Capability discovery metadata | Owning services and Astra coordination | Prerequisite: capability contract and minimal configuration; Runtime collaborator: Governance Engine | no fabrication |
| Planner | Declarative execution plan construction | Astra AI platform | Prerequisite: Capability Registry and Governance Engine; Certification: Audit evidence | no execution during planning |
| Execution Gateway | Governed handoff to owner execution | Astra AI platform and owning services | Prerequisite: Planner and Governance Engine; Runtime collaborator: owning services | owner acceptance |
| Provider Gateway | External intelligence governance | Astra AI platform | Prerequisite: Governance, Configuration, provider contract; Runtime collaborator: Core Intelligence | provider independence |
| Memory Engine | Memory write, retrieval, retention, deletion, export governance | Astra AI platform | Prerequisite: Governance, Configuration, memory contract; Runtime collaborator: Context Engine | ownership and retrieval authorization |
| Learning Engine | Adaptation eligibility and activation governance | Astra AI platform | Prerequisite: Governance, Configuration, learning contract; Runtime collaborator: Memory Engine | no hidden drift |
| Governance Engine | Constitutional precedence and policy decisions | Astra AI platform | Bootstrap prerequisite: constitutional contracts and minimal Configuration Layer; Optional extension: Audit Engine | fail-closed behavior |
| Audit Engine | Evidence, integrity, access, retention, export, deletion | Astra AI platform | Bootstrap prerequisite: bounded evidence contract; Runtime collaborator: Governance Engine; Production: Configuration Layer | sufficiency and minimization |
| Configuration Layer | Feature flags, policy settings, rollout state | Platform infrastructure | Bootstrap prerequisite: configuration contract only; Runtime collaborators: Governance and Observability | disabled by default |
| Observability | Runtime visibility and deviation detection | Platform operations | Prerequisite: redacted event contract; Runtime collaborators: Audit and Configuration | redaction |
| Testing Framework | Conformance and certification validation | Engineering | Certification dependency for all components; no runtime prerequisite | repeatability |

---

# Boundary Rule

Components may depend on each other only through approved contracts. Direct
access to app-owned databases, bypassing owner services, or treating prompts,
providers, memory, adaptation, or user preference as authority remains
prohibited.

Circular runtime collaboration must not become an unresolved implementation
bootstrap cycle. Readiness planning must identify prerequisite contracts and
minimal kernels before full runtime integration.
