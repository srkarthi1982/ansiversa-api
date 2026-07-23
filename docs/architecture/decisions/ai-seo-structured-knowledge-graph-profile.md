# Architecture Decision: AI SEO Structured Knowledge Graph Profile

**Status:** Accepted
**Created:** 2026-07-23
**Accepted:** 2026-07-23
**Task:** SEO-004
**Decision Owner:** Karthikeyan Ramalingam
**Architecture Reviewer:** Astra - Approved 2026-07-23
**Product Owner:** Karthikeyan Ramalingam - Approved 2026-07-23
**Evidence Agent:** Codex
**Implementation:** Not authorized
**Production:** Unchanged

---

# Decision

Should Ansiversa adopt a governed V1 structured knowledge graph profile for
public AI SEO projections?

Adopt a narrow, backend-validated graph profile that projects SEO-002 public
truth into a bounded schema.org JSON-LD graph and SEO-003 page-local graph
bundles.

Canonical specification:

```text
docs/ai-seo-structured-knowledge-graph-profile.md
```

---

# Decision Drivers

- AI SEO Engineering Law #1: every public claim has exactly one approved source
  of truth.
- AI SEO Engineering Law #2: every published artifact is reproducible from one
  immutable approved revision.
- SEO-002 Contract V1 defines public app truth and provenance.
- SEO-003 requires canonical HTML, metadata, and structured projections from
  the same immutable manifest.
- Google structured-data guidance requires structured data to represent visible
  page content and does not guarantee rich results.
- The Ansiversa catalog is fixed at exactly 100 solution apps.
- Public graph output must not expose authenticated, internal, user-specific,
  future, or unsupported claims.

---

# Options

## A - Keep implicit current graph conventions

The current publisher already emits useful JSON-LD. Keeping it implicit avoids
new architecture work but does not freeze type, ID, relation, property,
validation, or visible-parity rules.

**Recommendation:** Reject.

## B - Broad schema.org adoption

This would model a richer graph early, including reviews, ratings, offers,
actions, images, or deeper workflow schema.

**Recommendation:** Reject for V1. These properties are not yet governed by
SEO-002 source authority and visible page parity.

## C - Narrow governed profile

This emits only approved platform, page, collection, app, relationship,
audience, and FAQ graph entities. It uses stable IDs, strict property
allowlists, prohibited properties, and fail-closed validation.

**Decision:** Accepted.

## D - Defer graph decisions to implementation

This keeps planning shorter but would couple structured-data design to future
rendering implementation.

**Recommendation:** Reject.

---

# Accepted Architecture

```text
SEO-002 approved public entity truth
        |
        v
Canonical AI Knowledge Registry
        |
        v
SEO-004 graph profile validation
        - stable node IDs
        - allowed schema.org types
        - allowed/prohibited properties
        - relationship vocabulary
        - visibility and provenance checks
        |
        v
Immutable Public Rendering Manifest
        - aggregate JSON-LD graph
        - page-local graph bundles for SEO-003
```

The backend remains the only graph compiler. The frontend may embed page-local
JSON-LD only from the validated immutable manifest. It may not parse source
documents or maintain a second graph schema.

---

# Consequences

If accepted:

- graph implementation work must validate against this profile;
- existing JSON-LD becomes a baseline, not the final contract;
- category, FAQ, and relationship graph output must follow explicit authority;
- prohibited properties stay absent until a later profile revision;
- SEO-003 rendering implementation receives bounded graph bundles;
- SEO-005 through SEO-007 still own crawler policy, sitemap/freshness, and
  observability decisions; and
- implementation remains separately unauthorized.

---

# Acceptance Record

- [x] Architecture Reviewer approved the recommendation and boundaries.
- [x] Product Owner accepted the decision.
- [x] Supported entity types accepted.
- [x] Stable `@id` policy accepted.
- [x] Relationship vocabulary accepted.
- [x] Prohibited property list accepted.
- [x] Failure, cache, validation, and rollback boundaries accepted.
- [x] SEO-004 frozen.

---

# Status Boundary

```text
Repository evidence           Collected
Architecture                 Narrow governed structured graph profile
Architecture acceptance       Approved
ADR                           Accepted
SEO-004                       Frozen
Implementation                Not authorized
Runtime                       Unchanged
Production                    Unchanged
```
