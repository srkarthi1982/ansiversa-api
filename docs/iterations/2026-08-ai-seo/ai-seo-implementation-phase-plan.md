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
Implementation complete; governance review approved; source review pending
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
- internal evidence is absent from public render output.

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
Source-level Astra review pending.
Phase 2 freeze pending.
Phase 3 not authorized.
Production unchanged.
```

---

# Phase 3: Shadow Comparison

Status:

```text
Not authorized
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

Validation:

- current public files remain unchanged unless explicitly approved;
- candidate output has exactly 100 apps and 14 categories;
- graph and manifest revisions match;
- validation report contains no secrets or private data.

---

# Phase 4: Frontend Consumer

Repository:

```text
ansiversa
```

Scope:

- consume immutable public render manifest;
- pre-render allowed public routes;
- preserve shell behavior;
- hydrate from the same manifest revision;
- fail closed on missing or incompatible manifests.

Validation:

- raw route HTML contains approved metadata and visible truth;
- hydration produces no material mismatch;
- private and workflow routes are excluded;
- desktop, tablet, and mobile checks pass.

---

# Phase 5: Deployment Dry Run

Repositories:

```text
ansiversa-api
ansiversa
```

Scope:

- production-shaped build;
- artifact digest verification;
- rollback rehearsal;
- smoke checks in approved environment;
- no live production behavior change until approval.

Validation:

- current production remains unchanged;
- candidate release package is complete;
- rollback restores the last known good release;
- HTML, graph, manifest, and public artifacts share one release identity.

---

# Phase 6: One-App Rollout

Default sequence:

```text
Canonical 100-app catalog order
```

Scope per app:

- approve source package;
- compile entity;
- compile graph bundle;
- compile page bundle;
- validate canonical route;
- certify production-shaped artifact;
- record Astra review and Partner approval.

Exit rule:

```text
One app approved does not approve the next app.
```

---

# Phase 7: Legacy Path Retirement

This phase is optional and must be separately approved after stable rollout.

Scope:

- identify inactive duplicate Knowledge publisher paths;
- preserve audit history;
- remove only redundant implementation;
- update current-state `story.md` documentation.

Non-goal:

- no retirement before the SEO-005 path is certified and stable.
