# Architecture Decision: AI SEO Canonical Public Rendering

**Status:** Accepted
**Created:** 2026-07-23
**Accepted:** 2026-07-23
**Task:** SEO-003
**Decision Owner:** Karthikeyan Ramalingam
**Architecture Reviewer:** Astra — Approved 2026-07-23
**Product Owner:** Karthikeyan Ramalingam — Approved 2026-07-23
**Evidence Agent:** Codex

Option E, Hybrid Governed Pre-rendering, is the accepted architecture. SEO-003
is Frozen. Implementation requires a later, separate Product Owner
authorization.

---

# Decision

How should Ansiversa publish governed public knowledge as canonical HTML while
keeping human-visible content and machine-readable projections synchronized?

Evidence:

```text
docs/iterations/2026-08-ai-seo/seo-003-rendering-evidence.md
```

---

# Decision Drivers

- AI SEO Engineering Law #1: every public claim has exactly one approved source
  of truth.
- AI SEO Engineering Law #2: every published artifact is reproducible from one
  immutable approved revision.
- SEO-002 Contract V1 is the stable public entity shape.
- Initial HTML must contain unique, approved visible truth.
- The 100-app catalog is fixed and changes through governance.
- Private workflows remain outside public compilation.
- Frontend and backend deploy separately.
- Failed generation preserves the last approved release.
- Runtime complexity requires evidence.

---

# Options

## A — Client rendering only

Preserves the current application but lacks route-specific truth in initial
HTML and cannot generate the canonical head with the visible page.

**Recommendation:** Reject.

## B — Static generation for all routes

Produces deterministic HTML but incorrectly extends public compilation into
authenticated and interactive workflows.

**Recommendation:** Reject.

## C — Runtime SSR

Produces request-time HTML but introduces a renderer, server-safe migration,
cache coherence, deployment coupling, and a new failure surface for content
that is not request-specific.

**Recommendation:** Do not select for Contract V1.

## D — Incremental regeneration

Reduces rebuild pressure but adds invalidation and stale-content policy that the
fixed, approval-driven catalog does not presently require.

**Recommendation:** Defer unless measured evidence justifies it.

## E — Hybrid governed pre-rendering

Pre-renders only approved public routes from one immutable compiler artifact
and retains client rendering for private and interactive routes.

**Advantages**

- canonical public initial HTML;
- deterministic and auditable deployment;
- preserved private workflow boundary;
- no request-time rendering dependency; and
- strong fit for the governed update cadence.

**Costs**

- router/build adaptation;
- immutable cross-repository artifact handoff;
- server-safe public components and hydration parity; and
- coordinated build validation and rollback.

**Recommendation:** Preferred candidate.

---

# Accepted Architecture

```text
Approved lifecycle sources
        ↓
Canonical AI Knowledge Registry
        ↓
SEO-002 Contract V1 validation
        ↓
Immutable Public Rendering Manifest
        ├── public machine projections
        └── frontend pre-render build
                ├── visible canonical HTML
                ├── metadata and canonical link
                ├── embedded structured projection
                └── hydration from the same revision

Private and interactive routes
        ↓
Existing client-rendered runtime
```

The backend remains the sole compiler. The frontend consumes only the public
manifest and may not parse source documents, import the internal registry, or
maintain a second schema.

The manifest is immutable and revision-pinned. Schema, registry revision, route
set, freshness, and digest mismatches fail the build. Mutable “latest” fetches
are not an acceptable release input.

Canonical HTML is generated in the frontend build using the same entity that
hydration receives. Visible content, metadata, canonical URLs, and structured
projections are pure projections of that entity.

Only allowlisted Contract V1 public routes are pre-rendered. Authenticated,
personalized, internal, preview, and workflow routes retain client rendering.

---

# Consequences

The accepted decision means:

- a governed frontend pre-render entry/build path is required;
- public presentation accepts manifest-supplied initial data;
- CI hands off and verifies one immutable manifest;
- HTML and machine artifacts form an atomic revision pair;
- SEO-004 through SEO-006 retain schema.org, crawler, sitemap, redirect, and
  archival decisions; and
- acceptance does not authorize implementation.

---

# Acceptance Record

- [x] Architecture Reviewer approved the recommendation and boundaries.
- [x] Product Owner accepted the decision.
- [x] Manifest identity, handoff, and fail-closed rules accepted.
- [x] Public/private route ownership accepted.
- [x] Hydration and public-truth parity controls accepted.
- [x] Validation and rollback matrices accepted.
- [x] AI SEO Engineering Law #2 adopted.
- [x] SEO-003 frozen.

---

# Status Boundary

```text
Repository evidence           Collected
Architecture                 Hybrid governed pre-rendering
Architecture acceptance       Approved
ADR                           Accepted
SEO-003                       Frozen
Implementation                Not authorized
Runtime                       Unchanged
Production                    Unchanged
```
