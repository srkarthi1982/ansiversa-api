# SEO-005 Discovery - Compiler and Validation Pipeline

**Task:** SEO-005
**Status:** Proposed
**Discovery:** Complete
**Specification:** Complete
**Architecture Review:** Pending Astra Review
**Product Owner Approval:** Pending
**ADR:** Proposed
**Implementation:** Not authorized
**Production:** Unchanged
**Created:** 2026-07-23

---

# Resolved Subject

SEO-005 is the final planned AI SEO architecture phase. It defines the
governed compiler and validation pipeline that connects app-level SEO source
documents, SEO-002 public truth, SEO-004 structured graph compilation, SEO-003
immutable manifest delivery, and hybrid governed pre-rendering.

SEO-005 is not the earlier crawler-governance task from the initial backlog.
That older subject is deferred into future implementation planning and
operational policy review. The approved SEO-005 subject is:

```text
Governed SEO source documents
        |
        v
Parser and normalizer
        |
        v
Validation and conflict detection
        |
        v
Entity resolution
        |
        v
SEO-004 knowledge graph compiler
        |
        v
Immutable SEO manifest
        |
        v
SEO-003 hybrid governed pre-rendering
        |
        v
Validated deployment artifacts
```

---

# Repository Evidence

Current evidence shows a partial foundation already exists:

- `app/modules/knowledge/builder.py` parses allowlisted backend and frontend
  sources, normalizes text, validates 100 app identities, blocks App #101,
  scans for secrets, computes source digests, and writes the canonical registry.
- `app/modules/knowledge/publisher.py` converts the registry into public
  knowledge JSON, JSON-LD, metadata, `llms.txt`, `llms-full.txt`,
  `ai-sitemap.xml`, and `robots.txt`.
- `app/modules/knowledge/check_registry.py` performs a read-only registry drift
  check.
- `app/modules/knowledge/check_public.py` performs a read-only public artifact
  drift and syntax check.
- `app/modules/knowledge/verify_public_deployment.py` performs read-only
  public deployment smoke checks for artifact reachability, content types,
  counts, forbidden content, and canonical URLs.
- `app/modules/knowledge/story.md` records that the Knowledge module is
  file-backed, deterministic, public-only for SEO artifacts, and not a user
  data or runtime AI feature.

The future SEO-005 pipeline must build on this foundation without silently
turning current scripts into an approved implementation. Existing code remains
evidence, not authorization.

---

# Current Gap

The current foundation does not yet define a complete governed release
pipeline for AI SEO:

- source inputs are known but not yet formalized as SEO source packages;
- severity levels are not governed across source, entity, graph, manifest,
  page, artifact, deployment, and observation checks;
- entity resolution is not formalized for replacements, retired identities,
  aliases, and category membership;
- SEO-004 graph validation is not yet a compiler stage;
- the immutable SEO manifest required by SEO-003 is not yet specified as a
  pipeline output;
- full versus incremental compilation policy is not defined;
- artifact version compatibility and release pairing are not defined;
- stale-output and last-known-good behavior are not expressed as release gates;
- validation reports and audit evidence are not standardized; and
- implementation sequencing is not bounded into safe phases.

---

# Problem Statement

Ansiversa needs one governed AI SEO compiler and validation pipeline so every
public SEO artifact is reproducible from approved sources, validated against
frozen contracts, and delivered as an immutable release package without runtime
or production behavior changing before authorization.

---

# Goals

- Define authoritative inputs and source ownership.
- Define parser, normalization, validation, conflict, and entity-resolution
  stages.
- Define SEO-004 graph-profile compilation.
- Define immutable SEO manifest generation for SEO-003.
- Define deterministic output and compatibility rules.
- Define severity levels and release blocking behavior.
- Define stale-output, fallback, rollback, and last-known-good policy.
- Define full and incremental compilation boundaries.
- Define validation reports, observability, and audit evidence.
- Define repository ownership and security/privacy boundaries.
- Define phased future implementation sequencing.
- Close the AI SEO architecture phase after SEO-005 review and approval.

---

# Non-Goals

- implementing the compiler;
- modifying registry, publisher, validation, manifest, or frontend code;
- creating runtime scaffolding or prototype branches;
- changing generated artifacts;
- changing APIs, routes, database schemas, migrations, dependencies,
  environment files, build scripts, Vercel config, or production behavior;
- adding crawler submission, IndexNow, analytics, dashboards, or provider
  automation;
- adding AI-generated SEO content;
- adding App #101 or changing the fixed 100-app catalog;
- approving implementation.
