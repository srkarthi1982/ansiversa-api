# ASTRA-IR-001 Interface Contracts Overview

**Status:** Approved and Frozen
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

This overview names contract categories required before implementation. It
does not define schemas, code, APIs, tables, prompts, providers, or runtime
interfaces.

---

# Contract Categories

| Contract | Purpose | Constitutional Source |
|---|---|---|
| Request contract | Represent user/system request intent and scope | ASTRA-002 |
| Conversation contract | Represent transient conversation state | ASTRA-003 |
| Context contract | Request and receive minimized owner-authorized context | ASTRA-003 |
| Capability contract | Describe capability metadata and availability | ASTRA-004 |
| Planning contract | Represent declarative plan and approval requirements | ASTRA-005 |
| Execution handoff contract | Represent owner acceptance and execution result | ASTRA-006 |
| Provider contract | Represent eligibility, envelope, routing, and response validation | ASTRA-007 |
| Memory contract | Represent memory eligibility, retrieval, retention, deletion, and export | ASTRA-008 |
| Learning contract | Represent adaptation eligibility, activation, conflict, and controls | ASTRA-009 |
| Governance contract | Represent safety class, precedence, authorization, and fail-closed outcome | ASTRA-010 |
| Audit contract | Represent evidence, integrity, access, retention, deletion, and export | ASTRA-010 |
| Configuration contract | Represent flags, environment boundaries, and rollout state | ASTRA-010 |
| Observability contract | Represent redacted events and deviations | ASTRA-010 |
| Certification contract | Represent review and conformance evidence | ASTRA-010 |
| Conformance matrix contract | Map constitutional requirement to owner, contract, evidence, certification, coverage, and failure posture | ASTRA-010 |

---

# Contract Requirements

Every future contract must define:

- owner;
- purpose;
- allowed inputs;
- allowed outputs;
- prohibited fields;
- authority source;
- privacy classification;
- audit evidence;
- failure behavior;
- certification expectations.

No implementation workstream may be authorized until applicable conformance
matrix rows identify the owning component, contract category, evidence,
certification obligation, coverage status, and failure posture.
