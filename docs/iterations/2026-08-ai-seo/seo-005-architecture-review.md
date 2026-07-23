# SEO-005 Architecture Review - Compiler and Validation Pipeline

**Task:** SEO-005
**Status:** Proposed
**Discovery:** Complete
**Specification:** Complete
**Architecture Direction:** Approved pending minor revision verification
**Freeze:** Pending minor revisions verification
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

1. Law #3 direction is approved with page-bound versus release-bound parity
   clarification.
2. Severity model direction is approved; implementation readiness must identify
   exact omission policy before compiler work.
3. V1 implementation is full compilation only; incremental compilation is
   architecturally defined but implementation-deferred.
4. Manifest metadata is approved after adding release ID, rollback base,
   backend/frontend revisions, creation mode, and release status.
5. Repository ownership split is approved.
6. Architecture phase closure is approved after these revisions and freeze.
7. Crawler/provider topics move to later implementation/operations planning.

---

# Acceptance Criteria For Freezing SEO-005

- [x] Astra approves the compiler pipeline architecture direction.
- [ ] Astra verifies the requested minor documentation revisions.
- [ ] Product Owner approves the architecture.
- [ ] ADR is accepted or explicitly marked not required.
- [x] AI SEO Engineering Law #3 is approved with parity-scope clarification.
- [ ] Authoritative inputs are accepted.
- [ ] Pipeline stages are accepted.
- [ ] Severity levels and release gates are accepted.
- [x] Manifest internal/public boundary is documented for verification.
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
Architecture Direction  Approved
Freeze                  Pending minor revisions verification
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```
