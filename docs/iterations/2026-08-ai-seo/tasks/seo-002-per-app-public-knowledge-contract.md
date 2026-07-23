# SEO-002 — Per-App Public Knowledge Contract

**Status:** Discussing
**Priority:** Critical
**Authorized Scope:** Discovery, specification, and architecture review only
**Implementation:** Not authorized
**Product Owner Authorization:** Recorded 2026-07-23

---

# Objective

Define the permanent implementation-independent contract governing what
Ansiversa may say publicly about every application.

Canonical specification:

```text
docs/ai-seo-per-app-public-knowledge-contract.md
```

---

# Deliverables

- versioned logical public app schema;
- required, conditional, optional, derived, generated, and prohibited fields;
- field ownership and approval matrix;
- field-level and item-level provenance;
- source authority and precedence;
- visibility and privacy rules;
- current/future/lifecycle rules;
- freshness and review ownership;
- conflict behavior;
- relationship rules;
- representative fixtures;
- pass/fail validation strategy; and
- architecture-review questions.

---

# Freeze Criteria

- [x] Repository schema and source extraction inspected.
- [x] Logical V1 schema proposed.
- [x] Ownership matrix proposed.
- [x] Provenance contract proposed.
- [x] Source-specific authority proposed.
- [x] Current/future rules proposed.
- [x] Visibility/prohibited fields proposed.
- [x] Freshness windows proposed.
- [x] Conflict taxonomy and failure behavior proposed.
- [x] Validation strategy proposed.
- [ ] Architecture Reviewer approval recorded.
- [ ] Product Owner contract approval recorded.
- [ ] Open review questions resolved.
- [ ] SEO-002 frozen.

---

# Non-Goals

- registry/compiler changes;
- frontend/backend changes;
- rendering or SEO-003;
- metadata/JSON-LD implementation;
- sitemap/robots changes;
- `marketing.md` parser implementation;
- runtime or configuration changes;
- crawler submission; and
- production changes.

---

# Current Boundary

```text
Specification             Drafted
Architecture review       Pending
SEO-002                    Discussing
Implementation            Not authorized
SEO-003                    Unresolved
Production                Unchanged
```
