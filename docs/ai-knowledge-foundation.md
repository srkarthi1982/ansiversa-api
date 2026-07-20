# Ansiversa AI Knowledge Foundation

## Purpose and architecture

Phase 1 created a deterministic internal registry from approved public metadata
and canonical route identity. Phase 2 makes the Ansiversa AI Assistant consume
that registry as its normal retrieval source. It introduces no public SEO
surface.

```text
allowlisted documentation and registries
  -> deterministic builder and validator
  -> app/modules/knowledge/data/ansiversa-knowledge.json
  -> cached backend adapter
  -> assistant deterministic retriever
```

The backend owns generation, visibility enforcement, and assistant retrieval.
The frontend must not import the internal artifact; a future phase may expose a
bounded public subset.

## Source hierarchy and current limitation

Identity order, names, slugs, and canonical overview routes come from the
frontend `APP_OVERVIEW_APPS` registry. Public purpose, category, capability,
audience, use-case, and workflow metadata come from backend overview JSON.
Stories are parsed only through approved headings. Approved `Future Version
Ideas` may populate `futureDirection`, always marked `state: future`.

The catalog synchronization script points to a locked `approved-apps.md`, but
that file is absent from the current workspace and repositories. This is a
governance gap. Phase 1 does not query production or copy private database
records to compensate. Stable IDs and lifecycle values follow the locked
catalog convention and are validated against the 100 route identities.

## Visibility

Every record and reference uses `public`, `authenticated`, `internal`, or
`restricted`. The adapter defaults to public records. Restricted records must
never enter public retrieval.

## Deterministic parsing and security

The builder reads only known JSON and Markdown below the repository roots. It
rejects path escape and symlinks, bounds input/output, strips comments, code
fences, and links without execution, performs no network calls, and scans for
credentials, tokens, authorization values, private keys, environment values,
and database URLs. Environment files, databases, user records, `AGENTS.md`, and
internal incidents are excluded.

Supported headings include Purpose, Audience/Who It Is For/Target Users,
Problem/Core User Problems, Current Capabilities/Features,
Limitations/Non Goals/Boundary, Safety, Use Cases/Journey, and Future
Direction/Future Version Ideas. Missing sections stay empty.

## Build, validation, and drift detection

```bash
python -m app.modules.knowledge.build_registry
python -m app.modules.knowledge.check_registry
```

Build writes only changed artifacts. Check regenerates in memory, never writes,
and fails when stale. Source revisions are content SHA-256 identifiers;
`generatedAt` is the schema release timestamp rather than a volatile build
clock. Validation enforces 100 unique apps, no App #101, canonical routes, 14
categories, versions, visibility, sources, relationships, current/future
separation, length bounds, and secret exclusion.

## Consumer boundaries and readiness

`KnowledgeRegistry` is a cached reader supporting public-by-default exact,
alias, category, problem, capability, page, and related-app lookup. The
Assistant converts cached registry records into its existing deterministic
retrieval model, preserving the `/api/v1/assistant/query` API contract,
validated actions, confidence handling, response modes, OpenAI provider
boundary, session context behavior, and fallback behavior.

The Assistant no longer reads the Apps catalog, overview JSON, FAQ rows, route
registry, page metadata, or Markdown files during normal requests. Those sources
remain upstream inputs to the registry builder only. If registry loading fails,
the backend logs the failure and uses the previous deterministic DB/FAQ
retriever as an explicit compatibility fallback.

OpenAI remains the explanation layer only. It may rewrite grounded public app
answers from bounded registry context, but it cannot create routes, actions,
apps, capabilities, prices, policies, future plans, or source facts. No
embedding, vector storage, public API, JSON-LD, `llms.txt`, sitemap, robots,
crawler submission, or frontend import is added.

Readiness is 100/100 for purpose, audience, current capabilities, aliases,
related apps, assistant retrieval parity, and traceability. Sixty-nine apps
have an explicitly marked future section. There are zero app extraction gaps and
one governance warning for the missing locked catalog source. A future
public-subset API must filter visibility and omit repository paths before use by
Search or AI SEO.
