# SEO-004 Architecture Review - Structured Knowledge Graph Profile

**Task:** SEO-004
**Status:** Proposed
**Discovery:** Complete
**Specification:** Complete
**Architecture Review:** Pending Astra Review
**Product Owner Approval:** Pending
**ADR:** Proposed
**Implementation:** Not authorized
**Production:** Unchanged
**Prepared:** 2026-07-23

---

# Review Objective

Review whether the proposed Structured Knowledge Graph Profile is the right
bounded architecture for Ansiversa public graph projections after SEO-002 and
SEO-003.

Canonical specification:

```text
docs/ai-seo-structured-knowledge-graph-profile.md
```

Proposed ADR:

```text
docs/architecture/decisions/ai-seo-structured-knowledge-graph-profile.md
```

Discovery:

```text
docs/iterations/2026-08-ai-seo/seo-004-discovery.md
```

---

# Architecture Summary

SEO-004 recommends a narrow, governed V1 graph profile:

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

**Recommendation:** Accept as Proposed V1.

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

# Review Questions

1. Does the proposed node allowlist cover the initial public graph without
   over-modeling?
2. Should category collection nodes be published before category pages are
   canonical public pages?
3. Is `featureList` acceptable for app capabilities once visible parity exists,
   or should capability lists remain unstructured in V1?
4. Should app FAQ JSON-LD wait until every app page visibly renders approved
   FAQ content?
5. Are the prohibited properties complete enough for V1 risk control?
6. Does the relationship vocabulary preserve SEO-002 authority without becoming
   a recommendation engine?
7. Does the failure matrix correctly distinguish release blockers from safe
   optional omissions?
8. Is a Proposed ADR required and acceptable for this profile?

---

# Acceptance Criteria For Freezing SEO-004

- [ ] Astra approves or revises the graph profile.
- [ ] Product Owner approves the profile.
- [ ] ADR is accepted or explicitly marked not required.
- [ ] Supported entity types are frozen for V1.
- [ ] Stable `@id` rules are frozen for V1.
- [ ] Relationship vocabulary is frozen for V1.
- [ ] Prohibited properties are frozen for V1.
- [ ] SEO-002 field-to-schema mapping is accepted.
- [ ] SEO-003 manifest relationship is accepted.
- [ ] Validation and rollback expectations are accepted.
- [ ] Status metadata is updated from Proposed to Frozen only after approval.

---

# Explicit Boundary

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
