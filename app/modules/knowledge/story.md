# AI Knowledge Foundation Backend Story

## Purpose

The Knowledge module owns the Canonical AI Knowledge Registry for Ansiversa.
It exists so platform AI features retrieve from one governed knowledge source
instead of rereading app catalogs, overview files, route registries, FAQs, or
Markdown documents independently.

## Workflow

Approved public metadata is processed by `build_registry.py` through the
deterministic builder. The committed artifact is
`app/modules/knowledge/data/ansiversa-knowledge.json`. `check_registry.py`
regenerates the registry in memory and fails if the committed artifact drifts.
The Assistant loads the registry through the cached `KnowledgeRegistry.load()`
adapter and converts registry records into its existing deterministic retrieval
model. Public AI publishing then converts the same registry into generated
public artifacts under `public/` without rereading upstream source files during
publication.

## User Journey

Users do not interact with this module directly. They ask Ansiversa AI for app
help, navigation, platform questions, related apps, current capabilities, or
approved future direction. The Assistant retrieves matching public registry
records, creates route-safe actions, and optionally lets OpenAI improve wording
from bounded registry context.

AI crawlers and search systems can read the generated public knowledge files:
`llms.txt`, `llms-full.txt`, `ai-sitemap.xml`, `public-ai-knowledge.json`,
`public-ai-jsonld.json`, `public-ai-metadata.json`, and `robots.txt`. These
files describe only approved public platform, category, page, app, alias,
capability, and relationship facts.

In production, the canonical discovery URLs live on `https://ansiversa.com`.
The frontend host rewrites only the approved public AI artifact paths to the
backend publisher on `https://api.ansiversa.com`, preserving one generated
source while avoiding React SPA fallback for crawler files.

## Database Design

The registry is file-backed and introduces no database tables or migrations.
It does not read user records or private app data. Source traceability records
the allowlisted repository path and section for each public source used during
generation.

## API Design

The internal registry consumer boundary is the Python `KnowledgeRegistry`
adapter. The Assistant API contract remains `POST /api/v1/assistant/query`.
Public AI publishing exposes read-only generated artifacts at root paths such
as `/llms.txt` and `/public-ai-knowledge.json`, plus convenience API routes
under `/api/v1/knowledge/public`.

The root artifact routes return deterministic cached responses from the
registry-derived publisher. This keeps production serving healthy even when the
deployment runtime does not expose the repository `public/` directory as a
filesystem path.

## Shared Components Used

The module uses backend standard library parsing, JSON serialization, XML
generation, bounded path validation, the existing Assistant deterministic
ranking and route validation layer, and FastAPI file responses. It does not use
embeddings, a vector database, crawler APIs, RAG, or OpenAI calls.

## Performance Considerations

`KnowledgeRegistry.load()` is cached with a single loaded artifact per process.
Normal assistant requests do not parse Markdown, overview JSON, FAQ rows, or
route registries. The in-memory registry is bounded to exactly 100 app records,
14 categories, and approved platform/account/legal page records. Public
publishing writes deterministic files from the cached registry, so public
artifact serving reads static generated files rather than rebuilding knowledge
on each request.

## Current Status

Phase 2 is active for Assistant retrieval parity, and AI SEO Public Knowledge
Publishing Phase 1 is active for public crawler artifacts. The Assistant reads
from the Canonical AI Knowledge Registry as the normal retrieval source. Legacy
DB/FAQ retrieval exists only as an explicit logged fallback if the registry
cannot load or validate at runtime. Public publishing does not change Assistant
behavior.

## Known Limitations

The locked `approved-apps.md` source is still missing from the workspace, so
the registry gap report retains one governance warning. The public publisher
does not expose future direction, source references, `AGENTS.md`, story files,
certification documents, promotion documents, authenticated records, internal
records, restricted records, or user data.

## Future Enhancements

Future phases may connect public metadata into frontend page rendering or
deployment automation after approval. Future work may also expand registry
source coverage, but assistant facts and public AI facts must continue to come
from the registry rather than independent request-time source reads.

## Current Implementation

The registry contains a governed `platformIdentityKnowledge` section. Every
record has public visibility, question intents, aliases, a deterministic
answer, facts, validated actions, and source references. Platform identity
questions must resolve from these records before app, contextual, fuzzy, or
fallback retrieval.

The current implementation includes deterministic registry build/check commands,
explicit visibility values, source traceability, current/future separation,
related-app generation, platform/account/legal page records, a cached registry
adapter, Assistant retrieval integration, route-safe actions, OpenAI explanation
boundaries, public AI artifact generation, public artifact routes, production
deployment smoke verification, JSON/XML validation, forbidden-content screening,
and focused parity tests.
