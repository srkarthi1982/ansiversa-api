# Iteration 2 AI SEO Dependencies

**Status:** Proposed

---

# Dependency Graph

```text
Existing Canonical AI Knowledge Registry
Existing public AI publisher and deployment
Four-document platform/app lifecycle
Canonical frontend route registry
    ↓
SEO-001 Platform Architecture
    ↓
SEO-002 Per-App Public Knowledge Contract
    Frozen: Contract V1 approved; implementation authorization pending
    ├──→ SEO-004 Structured Knowledge Graph Profile
    └──→ SEO-008 marketing.md Participation
    ↓
SEO-003 Canonical Public Rendering ADR
    ↓
SEO-005 Discovery And Crawler Governance
    ↓
SEO-006 Sitemap, Canonical, And Freshness Architecture
    ↓
SEO-007 Validation And Observability
    ↓
SEO-009 Implementation Plan
    ↓
Separate Product Owner implementation authorization
```

---

# Repository Dependencies

| Dependency | Owner | Current state | Iteration use |
|---|---|---|---|
| Canonical AI Knowledge Registry | Backend/platform | Implemented | Sole normalized knowledge source |
| Public publisher | Backend/platform | Implemented | Existing projection pipeline |
| App overview metadata | App/platform | Implemented | Current public presentation truth |
| Four lifecycle documents | App and platform owners | Complete for 100 apps | Governed authored source candidates |
| Existing registry schema v2 | Backend/platform | Implemented | Evidence baseline only; no SEO-002 runtime change |
| Frontend route registry | Frontend/platform | Implemented | Canonical app identity and routes |
| SPA deployment | Frontend/platform | Implemented | Rendering gap to resolve |
| Search Console | Product/operations | Operational evidence required later | Google crawl/index evidence |
| Bing Webmaster Tools | Product/operations | Operational evidence required later | Bing/Copilot and optional IndexNow evidence |

---

# External Dependencies

External crawler names, IP lists, webmaster features, structured-data
eligibility, and AI-answer reporting are temporally unstable. Before any
implementation task freezes, it must cite current first-party documentation and
record a review date.

`llms.txt` is additive. No task may depend on it as the only route to discovery.

SEO-003 depends on an accepted and frozen SEO-002 contract. Rendering
architecture must not infer or invent its own public entity shape.

SEO-003 evidence identifies these future implementation dependencies without
authorizing them:

- an immutable Public Rendering Manifest emitted by the backend compiler;
- a revision-pinned backend-to-frontend build artifact handoff;
- a Contract V1 public-route allowlist;
- a pre-render-capable frontend build/router boundary;
- server-safe public presentation components;
- hydration from the same manifest revision; and
- atomic validation, deployment, and rollback of HTML and machine projections.

SEO-003 must not make SEO-004 schema.org, SEO-005 crawler, or SEO-006 sitemap,
canonical-governance, freshness, redirect, and archival decisions.
---

# Boundary With Astra

I1-024 remains Frozen and implementation remains unauthorized. Iteration 2:

- does not modify Astra personal-data execution;
- does not change the production feature flag;
- does not consume authenticated/user knowledge;
- does not merge public SEO knowledge with personal context; and
- does not change the accepted persistent-audit architecture.
