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
model.

## User Journey

Users do not interact with this module directly. They ask Ansiversa AI for app
help, navigation, platform questions, related apps, current capabilities, or
approved future direction. The Assistant retrieves matching public registry
records, creates route-safe actions, and optionally lets OpenAI improve wording
from bounded registry context.

## Database Design

The registry is file-backed and introduces no database tables or migrations.
It does not read user records or private app data. Source traceability records
the allowlisted repository path and section for each public source used during
generation.

## API Design

The module exposes no public API. Its consumer boundary is the Python
`KnowledgeRegistry` adapter. The Assistant API contract remains
`POST /api/v1/assistant/query`; no schema-breaking response fields were added
for Phase 2.

## Shared Components Used

The module uses backend standard library parsing, JSON serialization, bounded
path validation, and the existing Assistant deterministic ranking and route
validation layer. It does not use embeddings, a vector database, crawler APIs,
or OpenAI calls.

## Performance Considerations

`KnowledgeRegistry.load()` is cached with a single loaded artifact per process.
Normal assistant requests do not parse Markdown, overview JSON, FAQ rows, or
route registries. The in-memory registry is bounded to exactly 100 app records,
14 categories, and approved platform/account/legal page records.

## Current Status

Phase 2 is active for Assistant retrieval parity. The Assistant reads from the
Canonical AI Knowledge Registry as the normal retrieval source. Legacy DB/FAQ
retrieval exists only as an explicit logged fallback if the registry cannot load
or validate at runtime.

## Known Limitations

The locked `approved-apps.md` source is still missing from the workspace, so
the registry gap report retains one governance warning. The registry is
internal backend infrastructure and is not published as JSON-LD, `llms.txt`,
sitemap content, robots metadata, or a public API.

## Future Enhancements

Future phases may expose a bounded public subset for search or AI SEO after
visibility filtering and repository-path omission are approved. Future work may
also expand registry source coverage, but assistant facts must continue to come
from the registry rather than independent request-time source reads.

## Current Implementation

The current implementation includes deterministic registry build/check commands,
explicit visibility values, source traceability, current/future separation,
related-app generation, platform/account/legal page records, a cached registry
adapter, Assistant retrieval integration, route-safe actions, OpenAI explanation
boundaries, and focused parity tests.
