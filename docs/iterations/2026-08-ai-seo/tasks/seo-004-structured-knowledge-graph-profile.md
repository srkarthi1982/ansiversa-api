# SEO-004 - Structured Knowledge Graph Profile

**Status:** Proposed
**Priority:** High
**Authorized Scope:** Discovery, specification, and architecture review only
**Implementation:** Not authorized
**Product Owner Discovery Authorization:** Recorded 2026-07-23
**Architecture Review:** Pending Astra Review
**Product Owner Architecture Approval:** Pending
**ADR:** Proposed

---

# Objective

Define the governed structured knowledge graph profile for Ansiversa public AI
SEO projections after SEO-002 and SEO-003.

Canonical specification:

```text
docs/ai-seo-structured-knowledge-graph-profile.md
```

Discovery:

```text
docs/iterations/2026-08-ai-seo/seo-004-discovery.md
```

Architecture review:

```text
docs/iterations/2026-08-ai-seo/seo-004-architecture-review.md
```

Proposed ADR:

```text
docs/architecture/decisions/ai-seo-structured-knowledge-graph-profile.md
```

---

# Deliverables

- [x] Repository graph and publisher discovery.
- [x] Existing SEO-001 through SEO-003 boundary review.
- [x] Primary-source structured-data evidence reviewed.
- [x] Problem definition and non-goals.
- [x] Supported entity type profile.
- [x] Stable `@id` policy.
- [x] SEO-002 field-to-schema mapping.
- [x] Relationship vocabulary.
- [x] Prohibited property list.
- [x] SEO-003 manifest interaction.
- [x] Failure, cache, validation, and rollback requirements.
- [x] Architecture options and recommendation.
- [x] Proposed ADR.

---

# Freeze Criteria

- [ ] Astra architecture review approved.
- [ ] Product Owner approval recorded.
- [ ] ADR accepted or explicitly marked not required.
- [ ] Graph entity type allowlist accepted.
- [ ] Stable ID rules accepted.
- [ ] Relationship vocabulary accepted.
- [ ] Prohibited property list accepted.
- [ ] Validation and partial-failure matrix accepted.
- [ ] SEO-004 status updated to Frozen only after approval.

---

# Non-Goals

- graph implementation;
- registry/compiler changes;
- frontend rendering changes;
- metadata, sitemap, robots, crawler, redirect, cache, or deployment changes;
- automatic `marketing.md` compiler participation;
- crawler submission;
- provider monitoring implementation;
- runtime or production changes.

---

# Current Boundary

```text
SEO-004                 Proposed
Discovery               Complete
Specification           Complete
Architecture Review     Pending Astra Review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```
