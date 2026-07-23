# AI SEO Implementation Phase 2: Compiler Pipeline

**Status:** Implemented
**Created:** 2026-07-23
**Phase:** 2
**Implementation:** Authorized
**Astra governance review:** Approved
**Source-level Astra review:** Changes requested; corrections implemented for re-review
**Product Owner approval:** Pending
**Production:** Unchanged
**Phase 3:** Not authorized

---

# Objective

Implement the backend-only compiler pipeline on top of the frozen Phase 1
foundation while keeping the compiler isolated from runtime routes, current
Knowledge publishing, frontend rendering, deployment, and production behavior.

---

# Scope Implemented

- Parser layer for allowlisted JSON, Markdown, and constrained registry source
  fixtures.
- Normalization layer for text, slugs, routes, canonical URLs, enums, stable
  lists, and digest inputs.
- Validation and conflict detection with `blocker`, `critical`, `major`,
  `minor`, and `info` severities.
- Entity resolution boundaries for platform, public pages, categories, and the
  fixed 100-app catalog.
- SEO-004 graph compilation for fixture entities using approved node types,
  stable IDs, deterministic ordering, and relationship resolution.
- Internal Release Manifest model for non-public release evidence.
- Public Render Manifest model that excludes governance-only and internal
  evidence.
- Internal validation report model.
- Isolated in-memory compiler pipeline harness.
- Focused Phase 2 tests using synthetic fixtures only.
- Source-review corrections for fail-closed graph and manifest release gates.

---

# Boundaries Preserved

- no FastAPI route import;
- no application startup import;
- no Knowledge builder or publisher integration;
- no current registry output change;
- no current public artifact change;
- no API change;
- no migration or database schema change;
- no dependency change;
- no frontend change;
- no environment, build, deployment, or production configuration change;
- no feature flag enablement;
- no shadow comparison;
- no Phase 3 work.

---

# Validation Coverage

Focused tests cover:

- deterministic parsing;
- deterministic normalization;
- stable serialization and digest behavior;
- conflict detection;
- unsupported visibility and prohibited content rejection;
- exactly 100-app boundary;
- App #101 rejection;
- duplicate identity rejection;
- unresolved relationship rejection;
- stable graph ordering;
- unsupported graph-property rejection;
- every emitted graph node type property allowlist enforcement;
- internal/public manifest separation;
- public manifest suppression after manifest-boundary failure;
- no manifest generation after graph validation failure;
- governance-only field exclusion from public render output;
- blocker, critical, and major release behavior;
- fail-closed output behavior;
- repeated compilation equivalence.

---

# Phase 2 Decision

Phase 2 implementation is complete and Astra has approved the reported
governance scope and completion state for commit
`3136c41 feat: add AI SEO compiler pipeline`.

```text
Phase 2 Implementation       Complete
Governance Review            Approved
Automated Validation         Passed
Source-Level Astra Review    Changes requested; corrections implemented
Phase 2 Freeze               Pending
Phase 3                      Blocked
Production                   Unchanged
```

Phase 2 is not frozen. Source-level Astra re-review and Product Owner approval
are required before Phase 2 can freeze or Phase 3 can begin.

---

# Source Review Corrections

The source-level review identified three required corrections. The Phase 2
correction package addresses them without runtime integration:

1. `compile_candidate` suppresses `public_render_manifest` when public manifest
   boundary validation blocks release.
2. `compile_candidate` stops before manifest generation when graph validation
   blocks release.
3. `major` validation findings block V1 release by default until an approved
   omission policy exists.

The correction also hardens graph validation by applying property allowlists to
every supported graph node type, not only `SoftwareApplication`.

---

# Source Review Checklist

Source-level review must verify:

1. Parsers only accept allowlisted source types and bounded sections.
2. Normalization does not silently resolve authoritative conflicts.
3. Validation ordering and severity summaries are deterministic.
4. Release validation enforces exactly 100 apps and 14 categories.
5. Duplicate IDs, numbers, slugs, routes, canonical URLs, and graph `@id`
   values fail closed.
6. Graph properties and relationships use the frozen SEO-004 allowlists.
7. Internal manifest fields cannot leak through nested public-manifest objects.
8. Release IDs and digests are deterministic, with no timestamp or random
   value dependency.
9. `compile_candidate` emits no releasable public output after blocker,
   critical, or major findings.
10. Package exports do not create runtime imports or side effects.
