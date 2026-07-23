# SEO-004 Architecture Review - Structured Knowledge Graph Profile

**Task:** SEO-004
**Status:** Frozen
**Discovery:** Complete
**Specification:** Complete
**Architecture Review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
**Implementation:** Not authorized
**Production:** Unchanged
**Prepared:** 2026-07-23

---

# Review Decision

Architecture Review approved the Structured Knowledge Graph Profile as the
right bounded architecture for Ansiversa public graph projections after SEO-002
and SEO-003.

Canonical specification:

```text
docs/ai-seo-structured-knowledge-graph-profile.md
```

Accepted ADR:

```text
docs/architecture/decisions/ai-seo-structured-knowledge-graph-profile.md
```

Discovery:

```text
docs/iterations/2026-08-ai-seo/seo-004-discovery.md
```

---

# Architecture Summary

SEO-004 accepts a narrow, governed V1 graph profile:

- `Organization`;
- `WebSite`;
- `WebPage`;
- `CollectionPage`;
- `SoftwareApplication`;
- conditional `FAQPage`, `Question`, `Answer`, and `Audience`.

The graph is produced only from the Canonical AI Knowledge Registry and
SEO-002-approved fields. SEO-003 later consumes the graph through an immutable
public rendering manifest so visible page content, metadata, and JSON-LD come
from the same revision.

---

# Options Considered

## Option A - Keep the current implicit JSON-LD graph

This keeps current code untouched but leaves node types, IDs, relations,
allowed properties, and visible-content parity as code conventions rather than
governed architecture.

**Recommendation:** Reject as a long-term profile.

## Option B - Adopt a broad schema.org graph immediately

This would model more properties and schema types early, including offers,
ratings, reviews, actions, images, and richer app detail.

**Recommendation:** Reject. The current product truth and visible-page parity
do not authorize those claims.

## Option C - Use a narrow governed profile with strict allowlists

This freezes only the public entities and properties needed for platform,
catalog, category, app, relationship, and FAQ understanding. Optional
properties are omitted until visible parity and source authority are proven.

**Decision:** Accepted as V1.

## Option D - Defer all graph decisions until rendering implementation

This avoids a separate architecture document but forces implementers to design
structured data while changing rendering, increasing risk of drift and
unsupported claims.

**Recommendation:** Reject.

---

# Recommended Architecture

Adopt Option C:

- backend-owned graph validation;
- deterministic stable `@id` rules;
- explicit schema.org type allowlist;
- SEO-002 field-to-property mapping;
- prohibited property list;
- approved relationship vocabulary;
- page-local graph bundles for SEO-003;
- aggregate graph projection from the same immutable revision;
- fail-closed validation for identity, visibility, truth, stale required
  fields, broken edges, and page-visible mismatch.

---

# Review Resolution

Architecture Review approved the separation between SEO-003 delivery and
SEO-004 structured knowledge representation. Product Owner approval accepted
the ADR and froze SEO-004. Remaining implementation details must be handled in
future authorized implementation tasks without weakening this profile.

---

# Acceptance Criteria For Freezing SEO-004

- [x] Astra approves or revises the graph profile.
- [x] Product Owner approves the profile.
- [x] ADR is accepted or explicitly marked not required.
- [x] Supported entity types are frozen for V1.
- [x] Stable `@id` rules are frozen for V1.
- [x] Relationship vocabulary is frozen for V1.
- [x] Prohibited properties are frozen for V1.
- [x] SEO-002 field-to-schema mapping is accepted.
- [x] SEO-003 manifest relationship is accepted.
- [x] Validation and rollback expectations are accepted.
- [x] Status metadata is updated from Proposed to Frozen only after approval.

---

# Explicit Boundary

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
