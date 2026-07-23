# Architecture Decision: AI SEO Compiler and Validation Pipeline

**Status:** Proposed
**Created:** 2026-07-23
**Task:** SEO-005
**Decision Owner:** Karthikeyan Ramalingam
**Architecture Direction:** Astra - Approved pending minor revision verification
**Freeze:** Pending minor revisions verification
**Product Owner:** Karthikeyan Ramalingam - Pending Approval
**Evidence Agent:** Codex
**Implementation:** Not authorized
**Production:** Unchanged

---

# Decision

Should Ansiversa adopt a governed compiler and validation pipeline as the final
planned AI SEO architecture phase?

Recommended decision:

Adopt a backend-owned, build-time compiler and validation pipeline that turns
governed SEO source documents into validated SEO-002 entities, SEO-004 graph
bundles, and an immutable SEO manifest for SEO-003 hybrid governed
pre-rendering.

Canonical specification:

```text
docs/ai-seo-compiler-validation-pipeline.md
```

---

# Proposed Architecture Law

## AI SEO Engineering Law #3

> No public SEO artifact may be emitted unless its required source, entity,
> graph, manifest, and revision-parity validations pass for the same immutable
> approved release.

Law #3 is directionally approved by Astra with this parity-scope clarification:
page-bound artifacts require visible-page parity, while release-bound non-page
artifacts require release-revision parity. All deployed artifacts must belong
to the same approved immutable release.

---

# Options

## A - Extend current builder scripts directly

**Recommendation:** Reject as architecture. Existing scripts are useful
evidence but not enough as the permanent release contract.

## B - Build a new independent SEO compiler

**Recommendation:** Reject. This creates a second knowledge pipeline.

## C - Governed compiler pipeline over the Knowledge foundation

**Recommendation:** Preferred candidate.

## D - Runtime validation and regeneration

**Recommendation:** Reject. Public SEO output must be build-time,
deterministic, immutable, and auditable.

---

# Proposed Architecture

```text
Governed SEO source documents
        |
        v
Parser and normalizer
        |
        v
Validation and conflict detection
        |
        v
Entity resolution
        |
        v
SEO-004 knowledge graph compiler
        |
        v
Immutable SEO manifest
        |
        v
SEO-003 hybrid governed pre-rendering
        |
        v
Validated deployment artifacts
```

The backend owns source parsing, precedence, validation, entity resolution,
graph compilation, manifest generation, public machine projections, and
validation reports. The frontend consumes only a compatible immutable manifest
for public pre-rendering and page-local parity.

---

# Consequences

If accepted:

- SEO-005 becomes the final planned AI SEO architecture phase.
- Implementation remains blocked until a separate implementation plan and
  authorization.
- Crawler, new sitemap architecture, observability, marketing participation,
  and provider automation move into implementation planning or separately
  approved tasks, not automatic numbered SEO architecture expansion.
- The Internal Release Manifest remains governance-only by default, while the
  frontend consumes only a limited Public Render Manifest or page bundle.
- V1 implementation uses full compilation only; incremental compilation is
  architecturally defined but implementation-deferred.
- Future compiler work must be phased, evidence-backed, and fail closed.
- Public SEO artifacts must be released as complete immutable revision pairs.

---

# Acceptance Record

- [x] Architecture direction approved pending minor revision verification.
- [ ] Product Owner accepted the decision.
- [x] AI SEO Engineering Law #3 direction accepted with parity-scope clarification.
- [ ] Pipeline stages accepted.
- [ ] Severity and release-gate model accepted.
- [x] Manifest internal/public boundary added for verification.
- [ ] Repository ownership accepted.
- [ ] SEO-001 through SEO-005 architecture completeness accepted.
- [ ] SEO-005 frozen.

---

# Status Boundary

```text
Repository evidence           Collected
Architecture                 Governed compiler and validation pipeline
Architecture direction        Approved pending minor revision verification
ADR                           Proposed
SEO-005                       Proposed
Implementation                Not authorized
Runtime                       Unchanged
Production                    Unchanged
```
