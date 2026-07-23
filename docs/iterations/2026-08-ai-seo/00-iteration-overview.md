# Iteration 2 — AI SEO Architecture

**Status:** Architecture complete; implementation readiness review complete
**Approved:** 2026-07-23
**Architecture review:** Approved
**Product Owner architecture approval:** Recorded
**Implementation:** Authorized for separately scoped engineering phases
**Production changes:** Not authorized

---

# Objective

Establish the architecture through which Ansiversa's approved public product
truth becomes consistently understandable to people, conventional search
engines, AI answer systems, and future machine consumers.

This iteration starts from the existing Canonical AI Knowledge Registry and
public publishing foundation. It does not create a competing registry.

---

# Discovery Finding

The repository already implements substantial AI SEO infrastructure:

- deterministic 100-app/14-category knowledge;
- public JSON and JSON-LD;
- `llms.txt` and `llms-full.txt`;
- AI sitemap and robots hints;
- deployment rewrites and public routes; and
- production artifact verification.

The principal gap is canonical page delivery: public SPA routes do not provide
route-specific initial HTML metadata, canonical links, or in-page structured
data. Iteration 2 must resolve this before expanding machine artifacts.

---

# Deliverables

- [AI SEO architecture](../../ai-seo-architecture.md)
- [Per-app public knowledge contract](../../ai-seo-per-app-public-knowledge-contract.md)
- [Structured knowledge graph profile](../../ai-seo-structured-knowledge-graph-profile.md)
- [Compiler and validation pipeline](../../ai-seo-compiler-validation-pipeline.md)
- [Discovery evidence](01-discovery-evidence.md)
- [SEO-004 discovery](seo-004-discovery.md)
- [SEO-004 architecture review](seo-004-architecture-review.md)
- [SEO-005 discovery](seo-005-discovery.md)
- [SEO-005 architecture review](seo-005-architecture-review.md)
- [SEO-005 architecture completeness assessment](seo-005-architecture-completeness-assessment.md)
- [AI SEO implementation readiness review](../../ai-seo-implementation-readiness-review.md)
- [AI SEO implementation roadmap](ai-seo-implementation-roadmap.md)
- [AI SEO implementation phase plan](ai-seo-implementation-phase-plan.md)
- [AI SEO implementation risk assessment](ai-seo-implementation-risk-assessment.md)
- [AI SEO certification plan](ai-seo-certification-plan.md)
- [AI SEO implementation Phase 1 task](tasks/ai-seo-implementation-phase-1-backend-compiler-foundation.md)
- [AI SEO implementation Phase 2 task](tasks/ai-seo-implementation-phase-2-compiler-pipeline.md)
- [Proposed backlog](02-priority-backlog.md)
- [Dependencies](03-dependencies.md)
- [Risk register](04-risk-register.md)
- [Validation strategy](05-validation-strategy.md)

---

# Lifecycle

```text
Discovery
    ↓
Architecture proposals
    ↓
Architecture review
    ↓
Product Owner approval
    ↓
Task freeze
    ↓
Separate implementation authorization
```

Architecture approval, task freeze, implementation authorization, deployment,
and production release remain separate decisions.

SEO-001 is completed. SEO-002 Contract V1, SEO-003 Hybrid Governed
Pre-rendering, SEO-004 Structured Knowledge Graph Profile, and SEO-005
Compiler and Validation Pipeline are approved and Frozen; implementation
remains unauthorized. The AI SEO architecture phase is complete. The
implementation readiness review is complete and accepted. Implementation is
authorized for separately scoped, reviewable, certifiable engineering phases.
It is not SEO-006 and does not authorize production change.

AI SEO Implementation Phase 1 is complete and Frozen as a disabled backend
compiler foundation after Astra review approved commit `5f0f852`.

AI SEO Implementation Phase 2 is implemented as an isolated backend compiler
pipeline. Astra approved the reported governance scope for commit `3136c41`,
and source-level review requested fail-closed corrections. Those corrections
are implemented for Astra re-review; Phase 2 freeze remains pending. It does
not integrate with runtime routes, the Knowledge publisher, frontend rendering,
deployment, or production behavior.

---

# Success Criteria

The planning iteration succeeds when:

- current implementation is accurately inventoried;
- platform and app responsibilities are explicit;
- source-document roles and precedence are defined;
- the canonical rendering gap has an evidence-backed decision path;
- vendor-specific assumptions are evidence-rated;
- a reviewable task backlog, dependencies, risks, and validation strategy exist;
- no implementation has occurred; and
- runtime and production behavior remain unchanged.

---

# Non-Goals

- runtime implementation;
- metadata or route changes;
- registry/schema changes;
- sitemap, robots, or crawler-policy changes;
- provider submissions;
- frontend/backend/configuration changes;
- marketing or video automation; and
- production authorization.
