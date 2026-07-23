# Iteration 2 — AI SEO Architecture

**Status:** Discovery and specification
**Approved:** 2026-07-23
**Architecture review:** Approved
**Product Owner architecture approval:** Recorded
**Implementation:** Runtime implementation not authorized
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
- [Discovery evidence](01-discovery-evidence.md)
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

SEO-001 is completed. SEO-002 Contract V1 is approved and Frozen; implementation
remains unauthorized. SEO-003 through SEO-008 remain Proposed and unauthorized.
SEO-003 remains unresolved.

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
