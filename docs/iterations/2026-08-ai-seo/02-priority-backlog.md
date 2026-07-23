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
| SEO-005 | Discovery And Crawler Governance | High | Proposed | Separate search, training, user-fetch, robots, WAF, and provider policies |
| SEO-006 | Sitemap, Canonical, And Freshness Architecture | High | Proposed | Define standard sitemap ownership, `lastmod`, redirects, duplicates, and optional IndexNow |
| SEO-007 | AI Search Validation And Observability | High | Proposed | Define crawl, indexing, citation, referral, accuracy, and correction evidence |
| SEO-008 | `marketing.md` Knowledge Participation | Medium | Proposed | Decide typed approved inputs without publishing aspirations as current facts |
| SEO-009 | AI SEO Implementation Plan | High | Deferred | Convert accepted ADRs/contracts into small frozen implementation tasks |
| SEO-010 | Marketing Automation Architecture | Medium | Deferred | Begin only after AI SEO source and validation contracts are proven |
| SEO-011 | Video Content Pipeline Architecture | Medium | Deferred | Begin only after truthful marketing-source governance is proven |

---

# Recommended Review Order

```text
SEO-001 Platform architecture
    ↓
SEO-002 Per-app contract
    ↓
SEO-003 Rendering ADR
    ↓
SEO-004 Knowledge graph profile
    ↓
SEO-005 Crawler governance
    ↓
SEO-006 Sitemap and freshness
    ↓
SEO-007 Validation and observability
    ↓
SEO-008 marketing.md participation
    ↓
SEO-009 Implementation planning
```

SEO-003 is the first expensive-to-reverse implementation decision. It must be
resolved before metadata implementation begins.

SEO-001 is complete. SEO-002 Contract V1, SEO-003 Hybrid Governed
Pre-rendering, and SEO-004 Structured Knowledge Graph Profile are approved and
Frozen. No runtime AI SEO work is authorized.

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
