# AI SEO Implementation Phase Plan

**Status:** Complete
**Created:** 2026-07-23
**Scope:** Engineering sequencing only
**Implementation:** Authorized
**Production:** Unchanged

---

# Phase Plan

The implementation must be split into small, reviewable phases. Each phase
requires its own task, validation, Astra review, and Partner approval.

---

# Phase 1: Backend Compiler Foundation

Status:

```text
Completed and frozen
```

Repository:

```text
ansiversa-api
```

First implementation commit:

```text
Add a disabled AI SEO compiler foundation with source inventory models,
validation fixtures, and deterministic tests only.
```

Boundaries:

- no runtime imports from API routes;
- no generated public artifact changes;
- no database migrations;
- no dependency additions unless separately approved;
- no production configuration changes.

Phase 1 output:

- disabled `app/modules/ai_seo_compiler` package;
- source inventory models;
- bounded validation fixture helpers;
- deterministic serialization and digest helpers;
- focused foundation tests;
- current-state task documentation.

Review status:

```text
Astra review approved commit 5f0f852.
Production unchanged.
```

Validation:

- backend compile;
- unit tests for deterministic source inventory;
- schema fixture validation;
- secret and visibility fixture checks.

---

# Phase 2: Compiler Pipeline

Status:

```text
Completed and Frozen
```

Repository:

```text
ansiversa-api
```

Scope:

- parser and normalizer;
- validation and conflict detection;
- entity resolution;
- graph-profile compilation;
- internal release manifest generation;
- public render manifest generation;
- validation report generation.

Validation:

- full compilation is deterministic;
- invalid sources fail closed;
- release IDs and digests are stable;
- internal evidence is absent from public render output;
- blocking graph validation stops manifest generation;
- public manifest boundary failures suppress public render output.

Phase 2 output:

- parser layer;
- normalization layer;
- validation and conflict detection;
- entity resolution;
- SEO-004 graph compiler;
- Internal Release Manifest;
- Public Render Manifest;
- internal validation reports;
- isolated in-memory pipeline harness;
- focused Phase 2 tests.

Boundary:

```text
No runtime serving, no Knowledge publisher integration, no generated artifact
changes, no frontend changes, no shadow comparison, no production changes.
```

Review status:

```text
Commit 3136c41 reported scope accepted by Astra.
Correction commit 7ede8ae approved by Astra source-level re-review.
Phase 2 Frozen.
Phase 3 separately authorized and implemented.
Production unchanged.
```

---

# Phase 3: Shadow Comparison

Status:

```text
Completed and Frozen
```

Repository:

```text
ansiversa-api
```

Scope:

- compare SEO-005 candidate output with current Knowledge publisher output;
- identify intentional differences;
- keep the current publisher as production behavior;
- record candidate evidence without serving it publicly.
- generate deterministic internal comparison reports;
- project Knowledge and compiler outputs into one canonical semantic comparison
  shape;
- keep Phase 4 blocked until separate authorization.

Validation:

- current public files remain unchanged unless explicitly approved;
- candidate output has exactly 100 apps and 14 categories;
- graph and manifest revisions match;
- validation report contains no secrets or private data.
- comparison detects entity, graph, manifest, metadata, canonical URL, digest,
  missing, unexpected, duplicate, ordering, and severity differences;
- repeated comparisons against identical snapshots produce identical reports.
- actual Knowledge-versus-compiler adapters compare equivalent public truth
  without false positives.
- Astra review approved commit 0723165 and correction commit bae87a7.

Boundary:

```text
No Knowledge publisher replacement, no registry generation replacement, no
artifact publishing, no public serving, no API exposure, no frontend
integration, no deployment change, no runtime startup change, no production
change.
```

---

# Phase 4: Controlled Integration Framework

Status:

```text
Completed and Frozen
```

Repository:

```text
ansiversa-api
```

Scope:

- integrate the AI SEO compiler into backend build orchestration behind an
  internal disabled-by-default control;
- preserve the current Knowledge publisher as the only authoritative
  production publisher;
- optionally run compiler execution from current in-memory Knowledge artifacts;
- collect internal comparison evidence;
- fail open for current publishing and fail closed for compiler evidence.

Validation:

- disabled control attempts no compiler execution;
- enabled internal execution produces deterministic evidence;
- compiler failures expose stable failure metadata without raw exception text;
- compiler failure does not replace or block current Knowledge artifacts;
- no API, frontend, migration, dependency, deployment, runtime startup, or
  production configuration changes occur;
- generated production artifacts remain unchanged.

Boundary:

```text
No Knowledge publisher replacement, no compiler artifact publication, no public
serving, no API exposure, no frontend integration, no deployment change, no
runtime startup change, no production change, and no Phase 5 work.
```

Review status:

```text
Commit e869666 implemented the controlled integration framework.
Correction commit 0aef627 sanitized compiler failure evidence.
Astra source re-review approved both commits.
Phase 4 Frozen.
Phase 5 remains pending separate authorization.
Production unchanged.
```

---

# Phase 5: Production Readiness Validation

Status:

```text
Completed and Frozen
```

Repository:

```text
ansiversa-api
```

Scope:

- execute complete internal compiler runs through controlled integration;
- validate full-catalog, graph, manifest, metadata, canonical URL, parity,
  deterministic release, deterministic evidence, controlled failure, and
  rollback readiness behavior;
- produce internal readiness reports only;
- keep the existing Knowledge publisher as the sole authoritative production
  publisher.

Validation:

- full catalog readiness passes for 100 apps and 14 categories;
- repeated readiness validation is deterministic;
- readiness fails closed when compiler execution or required artifacts fail;
- rollback evidence proves compiler failure preserves current Knowledge
  artifacts;
- no API, frontend, migration, dependency, deployment, runtime startup, or
  production configuration changes occur;
- generated production artifacts remain unchanged.

Boundary:

```text
No deployment dry run, no frontend repository change, no Knowledge publisher
replacement, no compiler artifact publication, no public serving, no API
exposure, no runtime startup change, no production change, and no Phase 6 work.
```

Review status:

```text
Commit c629ef1 implemented production readiness validation.
Correction commit 5346a12 strengthened readiness gates.
Astra source re-review approved both commits.
Phase 5 Frozen.
Phase 6 Operational Validation was separately authorized and implemented.
Production unchanged.
```

---

# Phase 6: Operational Validation

Status:

```text
Implemented, pending Astra source review
```

Repository:

```text
ansiversa-api
```

Scope:

- run repeated controlled compiler/readiness cycles;
- validate repeated semantic parity;
- validate repeated evidence determinism;
- validate repeated rollback and failure recovery behavior;
- produce internal operational evidence only;
- preserve the current Knowledge publisher as the sole authoritative production
  publisher.

Validation:

- repeated executions produce stable operational reports;
- repeated readiness evidence digests remain stable;
- parity remains stable across cycles;
- rollback probes repeatedly preserve current Knowledge artifacts;
- compiler failure evidence remains sanitized and deterministic;
- no API, frontend, migration, dependency, deployment, runtime startup, or
  production configuration changes occur;
- generated production artifacts remain unchanged.

Boundary:

```text
No production cut-over, no one-app rollout, no Knowledge publisher replacement,
no compiler artifact publication, no public serving, no API exposure, no
frontend integration, no deployment change, no runtime startup change, no
production change, and no Phase 7 work.
```

Review status:

```text
Phase 6 implementation is complete.
Astra source review remains pending.
Phase 6 is not Frozen.
Phase 7 is not authorized.
Production unchanged.
```

---

# Future Phase: Production Enablement or Rollout

Status:

```text
Not authorized and not defined in this phase.
```

Future production enablement, app rollout, or legacy-path retirement must be
defined and authorized separately after Phase 6 review.

Any rollout must preserve the established rule:

```text
One approved app does not approve the next app.
```

Non-goals for Phase 6:

- no rollout;
- no production enablement;
- no legacy path retirement;
- no production artifact replacement.
