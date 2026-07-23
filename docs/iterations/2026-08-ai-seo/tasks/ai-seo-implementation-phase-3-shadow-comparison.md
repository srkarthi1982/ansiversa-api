# AI SEO Implementation Phase 3: Shadow Comparison

**Status:** Frozen
**Created:** 2026-07-23
**Phase:** 3
**Implementation:** Authorized
**Astra review:** Approved
**Product Owner approval:** Approved
**Production:** Unchanged
**Phase 4:** Pending separate authorization

---

# Objective

Implement the backend-only shadow comparison framework that lets the SEO-005
compiler candidate output compare itself against current Knowledge publisher
output without replacing, publishing, serving, or activating compiler artifacts.

The existing Knowledge publisher remains the only active production publisher.

---

# Scope Implemented

- Internal `shadow.py` comparison models.
- Deterministic comparable item snapshots for entities, graph nodes, manifests,
  and metadata.
- Snapshot adapter for compiler candidate output.
- Snapshot adapter for current Knowledge public artifacts.
- Canonical semantic comparison projection shared by both adapters.
- Canonical comparison manifest key `manifest:public-seo-projection`.
- Deterministic shadow comparison report.
- Detection for:
  - entity differences;
  - graph differences;
  - manifest differences;
  - metadata differences;
  - canonical URL differences;
  - missing items;
  - unexpected items;
  - duplicate items;
  - ordering differences;
  - digest mismatches;
  - validation severity differences;
  - fail-closed candidate validation state.
- Focused Phase 3 tests using synthetic snapshots and in-memory current
  Knowledge artifacts.
- End-to-end Knowledge-adapter versus compiler-adapter parity tests.

---

# Boundaries Preserved

- no Knowledge publisher replacement;
- no registry generation replacement;
- no compiler artifact publication;
- no generated production artifact changes;
- no public serving;
- no new API;
- no frontend integration;
- no deployment change;
- no runtime startup change;
- no feature flag enablement;
- no Phase 4 work.

---

# Validation Coverage

Focused tests cover:

- identical output comparison;
- metadata differences;
- graph differences;
- entity differences;
- canonical URL differences;
- digest mismatches;
- missing entities;
- unexpected entities;
- duplicate entities;
- ordering differences;
- validation severity differences;
- deterministic repeated reports;
- fail-closed comparison behavior;
- in-memory Knowledge artifact snapshot conversion.
- equivalent Knowledge-versus-compiler adapter comparison without structural
  false positives;
- intentional adapter-level metadata difference with the exact expected
  finding.

---

# Source Review Corrections

Astra source-level review found that the generic comparator was deterministic,
but the real Knowledge and compiler adapters could not compare equivalent
public truth without false positives. The correction package addresses that by:

1. projecting both adapters into the same canonical semantic comparison shape;
2. using one canonical manifest identity, `manifest:public-seo-projection`;
3. comparing semantic values such as app count, route set digest, canonical URL
   set digest, entity projection digest, graph projection digest, and metadata
   projection digest;
4. sorting both adapter snapshots by comparable item identity;
5. keeping system-specific release IDs and envelope metadata outside parity
   payloads; and
6. adding end-to-end adapter parity and intentional-difference tests.

Astra source-level re-review approved the corrected adapter projection.

---

# Phase 3 Decision

Phase 3 implementation is complete, reviewed, approved, and frozen.

```text
AI SEO Implementation   Authorized
Phase 1                 Frozen
Phase 2                 Frozen
Phase 3                 Completed
Phase 3 Review          Approved
Phase 3                 Frozen
Phase 4                 Pending separate authorization
Production              Unchanged
```

Phase 4 remains blocked until separate Product Owner authorization.
