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
