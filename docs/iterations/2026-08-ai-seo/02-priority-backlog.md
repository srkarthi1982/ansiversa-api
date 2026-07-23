# Iteration 2 AI SEO Proposed Backlog

**Status:** Architecture approved
**Implementation:** No runtime implementation authorized

Only individually reviewed and frozen tasks may later be considered for
implementation. Iteration approval does not freeze these tasks.

| ID | Task | Priority | Status | Outcome |
|---|---|---:|---|---|
| SEO-001 | AI SEO Platform Architecture | Critical | Completed | Approved architecture artifact and validation evidence recorded |
| SEO-002 | Per-App Public Knowledge Contract | Critical | Frozen | Contract V1 approved; implementation awaits separate Product Owner authorization |
| SEO-003 | Canonical Public Rendering ADR | Critical | Frozen | Hybrid governed pre-rendering accepted; implementation awaits separate authorization |
| SEO-004 | Structured Knowledge Graph Profile | High | Frozen | Profile V1 approved; implementation awaits separate authorization |
| SEO-005 | Compiler And Validation Pipeline | Critical | Frozen | Pipeline approved; implementation awaits separate authorization |
| AI-SEO-IRR | Implementation Readiness Review | Critical | Approved | Architecture is complete and implementation is authorized for separately scoped engineering phases; no SEO-006 created |
| AI-SEO-P1 | Backend Compiler Foundation | Critical | Frozen | Astra review approved commit `5f0f852`; disabled backend foundation accepted |
| AI-SEO-P2 | Compiler Pipeline | Critical | Frozen | Astra approved commit `3136c41` and correction commit `7ede8ae`; Phase 3 separately authorized |
| AI-SEO-P3 | Shadow Comparison | Critical | Frozen | Astra approved commit `0723165` and correction commit `bae87a7`; Phase 4 pending separate authorization |

---

# Recommended Review Order

```text
SEO-001 Platform architecture
    ↓
SEO-002 Per-app contract
    ↓
SEO-003 Rendering ADR
    ↓
SEO-004 Structured knowledge graph profile
    ↓
SEO-005 Compiler and validation pipeline
    ↓
Architecture phase complete after approval
    ↓
Implementation planning only after explicit authorization
```

SEO-003 is the first expensive-to-reverse implementation decision. It must be
resolved before metadata implementation begins.

SEO-001 is complete. SEO-002 Contract V1, SEO-003 Hybrid Governed
Pre-rendering, SEO-004 Structured Knowledge Graph Profile, and SEO-005
Compiler and Validation Pipeline are approved and Frozen. The AI SEO
architecture phase is complete. No runtime AI SEO work is authorized.

The AI SEO Implementation Readiness Review is complete and approved. It is a
governance bridge between architecture and engineering, not another numbered
SEO architecture phase. Implementation is authorized for separately scoped
engineering phases; production change remains unauthorized.

AI SEO Implementation Phase 1 is complete and Frozen after Astra review. It
does not activate the compiler, does not alter the Knowledge registry or
publisher, and does not change production behavior.

AI SEO Implementation Phase 2 is complete and Frozen after Astra source-level
re-review approved commit `3136c41` and correction commit `7ede8ae`. Phase 2
adds an isolated in-memory parser, normalizer, validator, entity resolver,
graph compiler, internal/public manifest model, validation report model, and
pipeline harness. It does not alter runtime, Knowledge publishing, frontend,
deployment, or production behavior. Phase 3 was separately authorized after
Phase 2 freeze.

AI SEO Implementation Phase 3 is implemented as an internal backend-only shadow
comparison framework. It compares current Knowledge publisher output and
candidate compiler output through deterministic in-memory snapshots and reports.
Source-level review requested adapter corrections so equivalent public truth
does not create structural false positives; those corrections are implemented
and approved. Phase 3 is Frozen. It does not replace the Knowledge publisher,
publish artifacts, expose APIs, integrate frontend rendering, alter deployment,
or change production behavior. Phase 4 remains pending separate authorization.

---

# Deferred Topics

These are not reserved as numbered AI SEO architecture phases. Revisit them
only during implementation planning or separate authorization:

- crawler governance;
- sitemap, canonical, freshness, and IndexNow expansion;
- AI search validation and observability;
- `marketing.md` source-authority policy;
- implementation planning and sequencing;
- marketing automation architecture;
- video content pipeline architecture.

---

# Freeze Rule

A task may become Frozen only after:

- repository and external evidence is documented;
- expensive-to-reverse decisions are resolved;
- platform/app ownership is explicit;
- privacy and public-truth rules are approved;
- acceptance criteria and validation are executable;
- rejected options have rationale; and
- Product Owner approval is recorded.
