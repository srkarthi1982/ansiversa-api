# ASTRA-IMP-008 Governed Planning Engine

| Field | State |
|---|---|
| ASTRA-IMP-008 | Certified / Approved |
| Scope | Governed Planning Engine |
| Implementation direction | Approved |
| Astra re-review | Approved (`504db12f`) |
| Constitutional conformance | Approved |
| Product Owner approval | Approved |
| Certification | Passed |
| Production authorization | Not approved |
| Production | Unchanged |
| ASTRA-IMP-009 | Not authorized |

## Discovery and ownership

- IMP-005 supplies sealed registration, lifecycle interfaces, shutdown invalidation, configuration, governance/evidence access, and health.
- IMP-006 supplies immutable snapshots, ownership, freshness, lifecycle eligibility, and atomic mutation boundaries.
- IMP-007 supplies immutable metadata, governed deterministic discovery, owner-issued authority, visibility/status gates, and no handlers.
- Existing Assistant patterns informed naming only; no executable surface is imported.
- Frozen constitutional/readiness documents require no change.

Implemented immutable request/step/plan/health contracts, deterministic graph validation, required current conversation, governed discovery, capability eligibility, governance mapping, approval/acceptance boundaries, evidence-before-release, and Runtime registration.

Focused tests cover registration, lifecycle, authority, conversation rejection, outcome mapping, determinism, dependency rules, bounds, capability eligibility, fixed authorization, evidence atomicity, dependency immutability, and prohibited surfaces.

## Source-review corrections

Commit `ff30c765` received implementation-direction approval with two required corrections. Plan-governance evidence is now appended before allowed or blocked plan preparation and every returned reference resolves in deterministic sink order. Planning health no longer hard-codes conversation availability: it is degraded while unbound and becomes healthy only after a valid certified same-runtime dependency passes ownership/freshness validation.
