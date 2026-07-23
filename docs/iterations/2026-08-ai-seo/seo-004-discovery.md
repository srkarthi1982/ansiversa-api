# SEO-004 Discovery - Structured Knowledge Graph Profile

**Task:** SEO-004
**Status:** Frozen
**Discovery:** Complete
**Specification:** Complete
**Architecture Review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
**Implementation:** Not authorized
**Production:** Unchanged
**Created:** 2026-07-23

---

# Resolved Subject

SEO-004 is the Structured Knowledge Graph Profile stage from the Iteration 2
AI SEO backlog. It is separate from SEO-003.

SEO-003 answered how approved public truth should become canonical HTML:
Hybrid Governed Pre-rendering from one immutable backend compiler artifact.

SEO-004 answers what governed graph shape that artifact may contain for public
structured knowledge:

- supported entity types;
- stable public entity IDs;
- allowed relationship vocabulary;
- schema.org JSON-LD projections;
- graph validation rules; and
- failure behavior when graph truth is incomplete, stale, or misleading.

SEO-004 does not implement the profile. It does not change the registry,
publisher, frontend rendering, metadata, sitemap, robots, cache behavior,
routes, deployment, or production.

---

# Documents And Source Evidence Read

Repository governance:

- root `AGENTS.md`;
- `ansiversa-api/AGENTS.md`;
- `ansiversa/AGENTS.md`.

SEO architecture:

- `docs/ai-seo-architecture.md`;
- `docs/ai-seo-per-app-public-knowledge-contract.md`;
- `docs/ai-seo-public-deployment.md`;
- `docs/architecture/decisions/ai-seo-canonical-public-rendering.md`;
- `docs/iterations/2026-08-ai-seo/00-iteration-overview.md`;
- `docs/iterations/2026-08-ai-seo/01-discovery-evidence.md`;
- `docs/iterations/2026-08-ai-seo/02-priority-backlog.md`;
- `docs/iterations/2026-08-ai-seo/03-dependencies.md`;
- `docs/iterations/2026-08-ai-seo/04-risk-register.md`;
- `docs/iterations/2026-08-ai-seo/05-validation-strategy.md`;
- SEO-001, SEO-002, and SEO-003 task documents.

Astra governance:

- `astra/sources/00-README.md`;
- `astra/sources/01-ansiversa-platform-overview.md`;
- `astra/sources/02-ansiversa-governance.md`;
- `astra/sources/03-ansiversa-known-decisions.md`;
- `astra/sources/08-ansiversa-documentation-registry.json`;
- `astra/sources/14-coding-standards.md`;
- `astra/sources/17-ansiversa-quality-process.md`;
- `astra/sources/19-ansiversa-roadmap.md`.

Current implementation evidence:

- `app/modules/knowledge/builder.py`;
- `app/modules/knowledge/publisher.py`;
- `app/modules/knowledge/router.py`;
- `app/modules/knowledge/registry.py`;
- `app/modules/knowledge/check_public.py`;
- `app/modules/knowledge/verify_public_deployment.py`;
- `app/modules/knowledge/story.md`;
- frontend `vercel.json` AI SEO rewrites;
- frontend `index.html` SPA metadata baseline.

Current external primary references reviewed on 2026-07-23:

- Google Search Central structured data guidelines:
  https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- Google Search Central structured data introduction:
  https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- Google Search Central `SoftwareApplication` structured data:
  https://developers.google.com/search/docs/appearance/structured-data/software-app
- Schema.org `SoftwareApplication`:
  https://schema.org/SoftwareApplication
- Schema.org `Organization`:
  https://schema.org/Organization
- Schema.org `FAQPage`:
  https://schema.org/FAQPage

---

# Current Architecture

The backend currently owns the Canonical AI Knowledge Registry and public
publisher. The publisher emits:

- public knowledge JSON;
- public JSON-LD;
- public metadata JSON;
- `llms.txt`;
- `llms-full.txt`;
- `ai-sitemap.xml`;
- `robots.txt`.

The current JSON-LD graph includes:

- one `Organization`;
- one `WebSite`;
- one `CollectionPage` for `/apps`;
- one platform `FAQPage`;
- one `SoftwareApplication` per public app.

The frontend deployment rewrites approved public AI SEO artifact paths to the
backend before the SPA fallback. Normal app routes still return SPA HTML with
platform-wide metadata. SEO-003 has accepted a later hybrid pre-rendering
architecture to close that page-level gap, but implementation remains
unauthorized.

---

# Capability Gap

The existing graph is useful but too implicit to freeze as an implementation
contract:

- supported node types are not governed in a profile document;
- stable `@id` rules are only present in code;
- category nodes are not first-class graph entities;
- relationship semantics are not typed beyond human-readable reasons;
- app detail pages do not yet have page-local graph bundles;
- schema.org properties are not mapped field-by-field to SEO-002 authority;
- forbidden properties such as ratings, prices, offers, reviews, and
  guarantees are not formally prohibited by profile;
- graph validation does not yet prove page-visible parity for SEO-003; and
- rollback/failure rules for graph drift are not specified separately from
  general public artifact checks.

---

# Problem Statement

Ansiversa needs a governed public knowledge graph profile that makes the
platform, fixed 100-app catalog, categories, public pages, app entities,
relationships, and FAQs understandable without allowing structured data to
publish claims that are absent from visible current product truth.

The profile must be precise enough for a later implementation task to build
validators and projections without redesigning the graph.

---

# Goals

- Freeze a bounded graph vocabulary for the initial approved public profile.
- Bind every graph property to SEO-002 Contract V1 authority.
- Preserve SEO-001 Law #1 and SEO-003 Law #2.
- Keep JSON-LD representative of visible canonical pages.
- Support all 100 apps without hand-authored per-app schema duplication.
- Define stable `@id` rules that survive wording changes.
- Separate platform, category, app, page, FAQ, and relationship ownership.
- Fail closed on unsupported, stale, private, future, or conflicting claims.

---

# Non-Goals

- implementing graph code;
- changing generated JSON-LD;
- changing metadata, sitemap, robots, redirects, routes, or Vercel config;
- adding new app catalog members;
- adding user data, authenticated workflows, analytics, ratings, reviews,
  prices, offers, or paywall claims;
- adding AI-generated content;
- deciding crawler/search/training policy;
- deciding sitemap/freshness/IndexNow policy;
- deciding validation dashboards; and
- adding automatic `marketing.md` compiler participation without separate
  source-authority approval.
