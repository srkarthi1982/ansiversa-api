# ASTRA-IR-001 Constitution-To-Engineering Conformance Matrix

**Status:** Proposed
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

This matrix maps implementation-relevant constitutional requirements to
engineering ownership, contract categories, evidence expectations,
certification gates, coverage status, and failure posture.

It is a readiness artifact only. It does not authorize implementation and does
not modify the Constitution.

---

# Matrix Rules

Every implementation-relevant constitutional requirement must define:

- stable requirement identifier;
- constitutional source;
- accountable owning component;
- supporting components;
- required contract category;
- required evidence;
- certification or test obligation;
- coverage status; and
- failure posture.

Coverage status values:

- `mapped`;
- `deferred`;
- `not applicable`;
- `amendment required`.

No implementation workstream may be authorized until its applicable
constitutional requirements have accountable owners, contract mappings,
certification obligations, evidence expectations, coverage statuses, and
failure postures.

---

# Initial Conformance Matrix

| Constitutional source | Requirement ID | Requirement | Owning component | Supporting components | Required contract | Required evidence | Certification gate | Coverage | Failure posture |
|---|---|---|---|---|---|---|---|---|---|
| ASTRA-002 | AIR-CM-001 | Local sufficiency before provider use | Core Intelligence Engine | Provider Gateway, Governance Engine | Intelligence decision contract | Local sufficiency decision | Provider-governance certification | mapped | Fail closed or local response |
| ASTRA-003 | AIR-CM-002 | Minimum necessary context | Context Engine | Conversation Engine, Audit Engine | Context envelope contract | Context minimization evidence | Context-isolation certification | mapped | Refuse or clarify |
| ASTRA-004 | AIR-CM-003 | Capability must be registry-backed and not fabricated | Capability Registry | Governance Engine, Testing Framework | Capability metadata contract | Capability proof evidence | Capability certification | mapped | No capability selected |
| ASTRA-005 | AIR-CM-004 | Planning is declarative and does not execute | Planner | Governance Engine, Audit Engine | Planning contract | Plan version and no-mutation evidence | Planning certification | mapped | Do not hand off |
| ASTRA-006 | AIR-CM-005 | Owner acceptance before execution | Execution Gateway | Governance Engine, owning services | Execution handoff contract | Owner acceptance evidence | Execution-governance certification | mapped | Reject |
| ASTRA-007 | AIR-CM-006 | Provider eligibility before provider selection | Provider Gateway | Governance Engine, Configuration Layer | Provider eligibility contract | Eligible provider set evidence | Provider-governance certification | mapped | Provider unavailable |
| ASTRA-008 | AIR-CM-007 | Memory existence does not authorize retrieval | Memory Engine | Governance Engine, Audit Engine | Memory retrieval decision contract | Retrieval authorization evidence | Memory certification | mapped | Do not retrieve |
| ASTRA-009 | AIR-CM-008 | Adaptation eligibility does not activate adaptation | Learning Engine | Governance Engine, Memory Engine | Adaptation activation contract | Activation decision evidence | Learning certification | mapped | Keep adaptation inactive |
| ASTRA-010 | AIR-CM-009 | Unknown constitutional compliance fails closed | Governance Engine | Audit Engine, Configuration Layer | Governance decision contract | Fail-closed decision evidence | Governance certification | mapped | Fail closed |
| ASTRA-010 | AIR-CM-010 | Implementation does not authorize production | Configuration Layer | Governance Engine, Audit Engine | Production gate contract | Explicit production approval evidence | Production readiness gate | mapped | Remain disabled |

---

# Expansion Requirement

The initial matrix is not exhaustive. Future implementation-readiness and
implementation-scope work must expand it for every applicable workstream before
that workstream can be authorized.
