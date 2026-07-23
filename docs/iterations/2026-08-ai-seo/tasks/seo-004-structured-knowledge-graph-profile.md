# SEO-004 - Structured Knowledge Graph Profile

**Status:** Frozen
**Priority:** High
**Authorized Scope:** Discovery, specification, and architecture review only
**Implementation:** Not authorized
**Product Owner Discovery Authorization:** Recorded 2026-07-23
**Architecture Review:** Approved 2026-07-23
**Product Owner Architecture Approval:** Approved 2026-07-23
**ADR:** Accepted

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

Accepted ADR:

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

- [x] Astra architecture review approved.
- [x] Product Owner approval recorded.
- [x] ADR accepted or explicitly marked not required.
- [x] Graph entity type allowlist accepted.
- [x] Stable ID rules accepted.
- [x] Relationship vocabulary accepted.
- [x] Prohibited property list accepted.
- [x] Validation and partial-failure matrix accepted.
- [x] SEO-004 status updated to Frozen only after approval.

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
SEO-004                 Frozen
Discovery               Complete
Specification           Complete
Architecture Review     Approved
Product Owner Approval  Approved
ADR                     Accepted
Implementation          Not authorized
Production              Unchanged
```
