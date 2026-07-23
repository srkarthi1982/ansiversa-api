# SEO-003 — Canonical Public Rendering ADR

**Status:** Frozen
**Priority:** Critical
**Authorized Scope:** Discovery, evidence collection, and ADR drafting only
**Implementation:** Not authorized
**Product Owner Discovery Authorization:** Recorded 2026-07-23
**Architecture Review:** Approved 2026-07-23
**Product Owner Architecture Approval:** Approved 2026-07-23

---

# Objective

Determine the permanent architecture for publishing governed public knowledge
as canonical HTML and synchronized machine-readable projections.

---

# Deliverables

- [x] Repository rendering and deployment evidence.
- [x] Current frontend/backend truth-path analysis.
- [x] Primary-source feasibility evidence.
- [x] Static, SSR, incremental, and hybrid comparison.
- [x] Architecture recommendation.
- [x] Proposed ADR.
- [x] Validation and rollback design.
- [x] Backlog, dependency, risk, and validation updates.

Evidence:

```text
docs/iterations/2026-08-ai-seo/seo-003-rendering-evidence.md
```

ADR:

```text
docs/architecture/decisions/ai-seo-canonical-public-rendering.md
```

---

# Freeze Criteria

- [x] Repository and deployment topology documented.
- [x] Alternatives evaluated without implementation.
- [x] One recommendation recorded.
- [x] Canonical HTML generation boundary defined.
- [x] Human/machine parity design defined.
- [x] Public/private route boundary defined.
- [x] Immutable compiler-artifact handoff defined.
- [x] Failure, cache, freshness, and rollback strategy defined.
- [x] Implementation validation matrix proposed.
- [x] Architecture Reviewer approval recorded.
- [x] Product Owner architecture approval recorded.
- [x] Rejected-option rationale accepted.
- [x] AI SEO Engineering Law #2 adopted.
- [x] SEO-003 frozen.

---

# Non-Goals

- rendering implementation;
- frontend, backend, compiler, registry, or schema changes;
- JSON-LD implementation;
- sitemap, robots, canonical-route, crawler, or redirect changes;
- SEO-004 through SEO-008 decisions;
- runtime or configuration changes; and
- deployment or production changes.

---

# Current Boundary

```text
Discovery authorization       Approved
Evidence                      Collected
ADR                           Accepted
Architecture                  Hybrid governed pre-rendering
Architecture approval         Approved
SEO-003                       Frozen
Implementation                Not authorized
Production                    Unchanged
```
