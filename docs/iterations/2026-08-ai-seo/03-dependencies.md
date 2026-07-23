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
    └──→ SEO-004 Structured Knowledge Graph Profile
    ↓
SEO-003 Canonical Public Rendering ADR
    ↓
SEO-004 Structured Knowledge Graph Profile
    ↓
SEO-005 Compiler And Validation Pipeline
    ↓
AI SEO Implementation Readiness Review
    ↓
AI SEO Implementation Phase 1: Backend Compiler Foundation
    ↓
AI SEO Implementation Phase 2: Compiler Pipeline
    ↓
Implementation planning only after explicit authorization
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
| SEO-005 compiler pipeline | Backend/platform | Frozen | Final architecture layer connecting sources, validation, graph, manifest, and rendering |
| AI SEO Implementation Readiness Review | Product/architecture/engineering | Approved | Authorizes implementation through separately scoped engineering phases without creating SEO-006 |
| AI SEO Implementation Phase 1 | Backend/platform | Frozen | Astra review approved commit `5f0f852`; disabled compiler foundation only; no active pipeline, runtime import, artifact write, or production change |
| AI SEO Implementation Phase 2 | Backend/platform | Implemented | Isolated compiler pipeline only; review pending; no runtime import, artifact write, shadow comparison, or production change |
| Search Console | Product/operations | Operational evidence required later | Deferred implementation/operations evidence |
| Bing Webmaster Tools | Product/operations | Operational evidence required later | Deferred implementation/operations evidence |

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

SEO-003 must not make SEO-004 schema.org decisions or deferred crawler,
sitemap, canonical-governance, freshness, redirect, and archival decisions.

SEO-003 is Frozen with Hybrid Governed Pre-rendering accepted. Its identified
implementation dependencies remain designs only until separate Product Owner
implementation authorization.

SEO-004 is Frozen with the Structured Knowledge Graph Profile V1 accepted. It
depends on SEO-002 Contract V1 for public app truth and on SEO-003 for the
future immutable manifest/page-local rendering boundary. SEO-004 does not
authorize schema.org, JSON-LD, manifest, frontend, backend, sitemap, robots,
cache, deployment, or production implementation.

SEO-005 is Frozen as the final planned AI SEO architecture phase. It depends on
SEO-001 through SEO-004 and defines the compiler/validation pipeline that
connects governed SEO source documents to SEO-004 graph bundles, SEO-003
immutable manifests, hybrid pre-rendering, and validated artifacts. SEO-005
does not authorize compiler, manifest, frontend, backend, artifact, deployment,
or production implementation.
---

# Boundary With Astra

I1-024 remains Frozen and implementation remains unauthorized. Iteration 2:

- does not modify Astra personal-data execution;
- does not change the production feature flag;
- does not consume authenticated/user knowledge;
- does not merge public SEO knowledge with personal context; and
- does not change the accepted persistent-audit architecture.
