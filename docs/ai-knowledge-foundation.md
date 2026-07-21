# Ansiversa AI Knowledge Foundation

## Purpose and architecture

Phase 1 created a deterministic internal registry from approved public metadata
and canonical route identity. Phase 2 makes the Ansiversa AI Assistant consume
that registry as its normal retrieval source. AI SEO Public Knowledge
Publishing Phase 1 exposes only governed public knowledge as deterministic
machine-readable artifacts.

```text
allowlisted documentation and registries
  -> deterministic builder and validator
  -> app/modules/knowledge/data/ansiversa-knowledge.json
  -> cached backend adapter
  -> assistant deterministic retriever
  -> public knowledge publisher
  -> llms.txt, llms-full.txt, AI sitemap, JSON-LD, public AI JSON, metadata
```

The backend owns generation, visibility enforcement, assistant retrieval, and
public AI publishing. The frontend must not import the internal registry
artifact.

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

### Platform identity priority

Platform identity questions are reputation-sensitive. They must be answered
from authoritative public identity knowledge before app retrieval, contextual
retrieval, fuzzy matching, or fallback behavior. Registry schema v2 adds
public, source-traceable `platformIdentityKnowledge` records. Security and
professional-safety handling still precede identity, and OpenAI cannot rewrite
identity facts. Karthikeyan Ramalingam is Founder and Chief Architect; Ansila
Adamkutty is official owner and legal license holder; no separate operating
entity is published. Astra is the built-in AI assistant. Provider/model routing
remains private.

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
embedding, vector storage, crawler submission, or frontend import is added.

## Public Knowledge Publishing

The public publisher generates a bounded public knowledge surface from the
Canonical AI Knowledge Registry. It publishes only records with
`visibility: public` and omits source references, authenticated/account-only
records, internal records, restricted records, future direction, story paths,
certification language, promotion documents, user data, and implementation
notes.

Generated artifacts live under `public/`:

```text
public/llms.txt
public/llms-full.txt
public/ai-sitemap.xml
public/public-ai-knowledge.json
public/public-ai-jsonld.json
public/public-ai-metadata.json
public/robots.txt
```

Read-only routes serve the generated files:

```text
/llms.txt
/llms-full.txt
/ai-sitemap.xml
/public-ai-knowledge.json
/public-ai-jsonld.json
/public-ai-metadata.json
/robots.txt
/api/v1/knowledge/public
/api/v1/knowledge/public/jsonld
/api/v1/knowledge/public/metadata
```

Production deployment uses the backend as the canonical publisher and the
frontend host as the canonical public discovery domain. The frontend Vercel
configuration rewrites only the approved public AI artifact paths to
`https://api.ansiversa.com`, so crawlers can discover the files at
`https://ansiversa.com` without duplicating generated content in the frontend
bundle. Deployment operations and smoke verification are documented in
`docs/ai-seo-public-deployment.md`.

The public JSON export includes platform facts, public pages, 14 categories,
100 public apps, aliases, capabilities, canonical routes, relationships,
visibility, schema version, and a deterministic generated timestamp. The
JSON-LD graph uses schema.org `Organization`, `WebSite`, `CollectionPage`,
`FAQPage`, and one `SoftwareApplication` node per app. `llms.txt` follows the
emerging convention of a single H1, blockquote summary, and structured Markdown
link sections; `llms-full.txt` provides expanded public app context.

Build and check commands:

```bash
python -m app.modules.knowledge.build_public
python -m app.modules.knowledge.check_public
python -m app.modules.knowledge.verify_public_deployment --base-url https://ansiversa.com --api-base-url https://api.ansiversa.com
```

Publisher validation enforces exactly 100 public apps, 14 categories, no
duplicate routes, canonical Ansiversa URLs, valid JSON, valid XML, valid
schema.org JSON-LD shape, public visibility only, and forbidden-content
screening.

Readiness is 100/100 for purpose, audience, current capabilities, aliases,
related apps, assistant retrieval parity, public AI publishing, and
traceability. Sixty-nine internal registry app records have an explicitly marked
future section, but future direction is not exposed in public publishing
artifacts. There are zero app extraction gaps and one governance warning for the
missing locked catalog source.
