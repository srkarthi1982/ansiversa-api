# SEO-005 Architecture Review - Compiler and Validation Pipeline

**Task:** SEO-005
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

Review whether the proposed compiler and validation pipeline correctly connects
SEO-002 public truth, SEO-004 graph compilation, SEO-003 immutable manifest
delivery, and hybrid governed pre-rendering.

Canonical specification:

```text
docs/ai-seo-compiler-validation-pipeline.md
```

Discovery:

```text
docs/iterations/2026-08-ai-seo/seo-005-discovery.md
```

Proposed ADR:

```text
docs/architecture/decisions/ai-seo-compiler-validation-pipeline.md
```

Architecture completeness assessment:

```text
docs/iterations/2026-08-ai-seo/seo-005-architecture-completeness-assessment.md
```

---

# Options Considered

## Option A - Extend current builder scripts directly

This is the shortest path but risks turning existing implementation details
into architecture without explicit source-package, manifest, severity, and
release-gate contracts.

**Recommendation:** Reject as the architecture, preserve as implementation
evidence.

## Option B - Build a new independent SEO compiler

This could produce a clean implementation boundary but would create a second
knowledge pipeline and violate the existing one-compiler principle.

**Recommendation:** Reject.

## Option C - Governed compiler pipeline layered over the existing Knowledge foundation

This defines explicit stages, severity, validation reports, graph compilation,
manifest generation, and release gating while preserving backend ownership and
the existing registry foundation.

**Recommendation:** Accept as the proposed architecture.

## Option D - Runtime validation and regeneration

This would validate or regenerate SEO output on request.

**Recommendation:** Reject. SEO output must be immutable, build-time, and
auditable.

---

# Recommended Architecture

Adopt Option C:

- backend-owned compiler and validation pipeline;
- allowlisted source package;
- deterministic parser and normalizer stages;
- SEO-002 authority and conflict validation;
- stable entity resolution;
- SEO-004 graph-profile compilation;
- immutable SEO manifest generation for SEO-003;
- page/artifact parity validation;
- severity-based release gates;
- last-known-good and rollback policy;
- deterministic validation reports and audit evidence.

---

# Review Questions

1. Should SEO-005 adopt AI SEO Engineering Law #3 as proposed?
2. Are the severity levels sufficient for source, entity, graph, manifest, and
   deployment validation?
3. Should incremental compilation remain deferred until full compilation is
   proven in implementation?
4. Does the manifest metadata list contain enough compatibility and rollback
   evidence?
5. Does the repository ownership split preserve backend truth and frontend
   consumer responsibilities?
6. Should SEO-005 formally close the AI SEO architecture phase after approval?
7. Which crawler/sitemap/observability topics should move into implementation
   planning rather than new architecture phases?

---

# Acceptance Criteria For Freezing SEO-005

- [ ] Astra approves or revises the compiler pipeline architecture.
- [ ] Product Owner approves the architecture.
- [ ] ADR is accepted or explicitly marked not required.
- [ ] AI SEO Engineering Law #3 is accepted, revised, or rejected.
- [ ] Authoritative inputs are accepted.
- [ ] Pipeline stages are accepted.
- [ ] Severity levels and release gates are accepted.
- [ ] Manifest generation boundary is accepted.
- [ ] Failure, stale-output, fallback, and rollback policy is accepted.
- [ ] Repository ownership is accepted.
- [ ] Architecture-completeness assessment is accepted.
- [ ] Status metadata is updated from Proposed to Frozen only after approval.

---

# Explicit Boundary

```text
SEO-005                 Proposed
Discovery               Complete
Specification           Complete
Architecture Review     Pending Astra Review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```
