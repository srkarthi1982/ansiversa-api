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
| SEO-005 | Compiler And Validation Pipeline | Critical | Proposed | Final planned architecture phase; discovery/spec complete and architecture review pending |
| SEO-006 | Discovery And Crawler Governance | Deferred | Deferred | Revisit during implementation planning only if separately authorized |
| SEO-007 | Sitemap, Canonical, And Freshness Architecture | Deferred | Deferred | Revisit during implementation planning only if separately authorized |
| SEO-008 | AI Search Validation And Observability | Deferred | Deferred | Revisit during implementation planning only if separately authorized |
| SEO-009 | `marketing.md` Knowledge Participation | Deferred | Deferred | Revisit only after source and validation contracts are proven |
| SEO-010 | AI SEO Implementation Plan | High | Deferred | Convert accepted ADRs/contracts into small implementation tasks after explicit authorization |
| SEO-011 | Marketing Automation Architecture | Medium | Deferred | Begin only after AI SEO source and validation contracts are proven |
| SEO-012 | Video Content Pipeline Architecture | Medium | Deferred | Begin only after truthful marketing-source governance is proven |

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
Pre-rendering, and SEO-004 Structured Knowledge Graph Profile are approved and
Frozen. SEO-005 is the final planned architecture phase and remains Proposed
pending review. No runtime AI SEO work is authorized.

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
