# Ansiversa AI Assistant

## Purpose

Ansiversa AI Assistant is the platform help and navigation assistant. Phase 4
keeps routing and source authority deterministic while using session-only
frontend context to improve relevance. AI Knowledge Foundation Phase 2 migrates
retrieval to the Canonical AI Knowledge Registry. OpenAI remains only an
optional server-side explanation layer for approved grounded results. I1-002
adds the governed Astra Tool Framework for approved read-only tools without
changing the public response contract. I1-006 adds deterministic Learning
Intelligence that composes approved Quiz and Course Tracker tool results
without querying app databases directly.

## Workflow

The frontend sends a user message and optional session context to
`POST /api/v1/assistant/query`. The backend builds a public knowledge index from
the cached Canonical AI Knowledge Registry. The registry already contains the
approved app catalog facts, overview routes, platform/account/legal page
knowledge, categories, aliases, capabilities, user problems, related apps,
future direction, visibility, and source traceability. The assistant first
applies deterministic context handling for current page/app follow-ups,
last-opened-app navigation, recent app references, and favorite/recent
preference. It checks approved Learning Intelligence intents before single-tool
intents, after identity, safety, and restricted-request handling. Learning
Intelligence executes at most one Quiz tool and one Course Tracker tool through
the Tool Registry and combines structured results into deterministic learning
guidance. Single-tool intents still use the approved registry execution path.
The assistant then produces a deterministic answer, validated navigation
actions, safe source metadata, and confidence. Strong app-information queries
may send only bounded public context plus concise session context to OpenAI for
response wording. Tool facts are not sent to OpenAI or rewritten by OpenAI in
I1-002 or I1-006. Platform navigation, unknown queries, weak matches, explicit
future questions, and provider failures use the deterministic path.

## API Design

Request:

```json
{
  "message": "What do I get?",
  "context": {
    "currentRoute": "/pricing",
    "currentPage": "Pricing",
    "recentAppKeys": ["course-tracker"],
    "favoriteAppIds": ["app_123"],
    "conversationHistory": []
  }
}
```

Response:

```json
{
  "answer": "Pricing explains Ansiversa plans, platform access, and subscription options.",
  "actions": [{ "type": "platform", "label": "Open Pricing", "route": "/pricing" }],
  "sources": [{ "id": "platform:pricing", "title": "Pricing", "type": "platform" }],
  "confidence": "high",
  "responseMode": "deterministic"
}
```

## Knowledge Scope

Only public knowledge enters the index:

- Public app facts from the Canonical AI Knowledge Registry
- Public overview and explore routes from the registry
- Public platform, account, and legal page summaries from the registry
- Public categories, aliases, problems, capabilities, and related-app links
- Approved future direction only when explicitly asked, marked as future

Internal governance files, credentials, environment details, certification
evidence, user records, test data, raw operational instructions, and unreleased
promises are excluded.

OpenAI receives only the user question, a concise system instruction, public
source titles, source types, categories, summaries, and permitted action labels.
It does not receive routes, internal docs, database internals, repository
content, secrets, certification evidence, private user data, or speculative
roadmap material.

## Retrieval Design

Platform identity questions are reputation-sensitive. They are answered from
authoritative public identity knowledge before page context, app retrieval,
category matching, fuzzy matching, or fallback behavior. Security/restricted
requests and medical, legal, or financial boundaries remain higher priority.
Identity responses are deterministic, public-only, and use validated relevant
actions. OpenAI is not invoked for identity answers. Karthikeyan Ramalingam is
Founder and Chief Architect; Ansila Adamkutty is official owner and legal
license holder; no separate operating entity is published. Astra is the
built-in AI assistant and its model/provider configuration is not public.

General Python, live weather, sports-result, and point-to-point transport
questions receive a clear Ansiversa scope response with no actions. Bare
`code` does not match QR Code Creator.

The retrieval service is a deterministic hybrid matcher. It supports exact app
names, aliases, slugs, title phrases, categories, user problems, capabilities,
related-app requests, platform page terms, and bounded fuzzy app-name matching
for common typos. Ranking favors exact canonical names first, then aliases,
slugs, title phrases, category matches, bounded phrase matches, token overlap,
and app-only fuzzy title or slug matches. Specific app references win over
broader family collections so app questions do not drift into category or page
answers.

The assistant has deterministic branches for public catalog counts, public
category counts, app-family collections such as builder or tracker, and curated
recommendation groups for common user intents such as students, writing,
productivity, AI apps, planners, personal finance, expenses, interviews, small
business workflows, invoices, and textbook scanning. Recommendation answers may
list the requested number of apps, while navigation actions remain route-safe
and compact. Future-direction retrieval is intent-aware: temporal phrases such
as "next week" do not trigger roadmap/future-direction answers.

Session context can boost matching favorite and recent apps, resolve current
page/app follow-up questions, and answer "go back" requests through the last
opened app. Context improves retrieval only; it does not authorize new routes,
new actions, or general chat behavior.

The registry is loaded through the cached `KnowledgeRegistry.load()` adapter.
The assistant does not parse overview JSON, FAQ rows, route registries, or
Markdown files during normal requests. If registry loading fails or the registry
is corrupt, the backend logs the failure and uses the previous deterministic
DB/FAQ retriever as an explicit compatibility fallback.

## Context Layer

The assistant accepts session-only context from the frontend:

- current route and page
- current app and category when inside a solution app
- last opened app
- recent app keys
- favorite app IDs
- bounded grounded conversation history

The backend treats this as relevance input, not permanent memory. It does not
persist the context, create embeddings, ingest repository documents, perform
autonomous actions, or generate routes from user text.

## Tool Framework

The I1-002 Astra Tool Framework introduces:

- `AssistantToolDefinition`
- `AssistantToolContext`
- `AssistantToolRegistry`
- `AssistantToolExecutor`
- `AssistantToolResult`
- `AssistantToolCatalogEntry`

The executor enforces authentication, Phase 1 read-only policy, argument
validation, result bounds, route-safe actions, timeout boundaries, and safe
audit metadata. Tool callers and models cannot provide user IDs, owner IDs, or
tenant IDs. Structured failures are returned without exposing stack traces, SQL,
secrets, tokens, or raw personal payloads.

I1-012 extends the registry into the permanent Astra Tool Registry. Registered
capabilities now declare handler-free discovery metadata for owning app,
supported intents, authentication, owner scope, read-only mode, permission
scope, input/output schemas, timeout, version, enabled/disabled state,
deprecated state, visibility, result limit, and documentation path. The
Assistant resolves supported deterministic tool intents through registry lookup
before execution.

The first demonstration tool is `get_user_favorites_summary`. It is a
platform-level Favorites summary tool that calls the existing Favorites service,
returns only favorite app names, slugs, routes, count metadata, and route-safe
actions, and remains owner-scoped to the authenticated user. It is not a
solution-app integration and does not move app business logic into Astra.

Because Favorites are authenticated personal data, personal-data tool execution
is disabled by default behind the backend-owned
`ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` gate. When disabled, the Assistant
does not build the tool registry, does not query Favorites, returns no personal
data, and does not fall through to unrestricted retrieval. Tests may enable the
gate deliberately; production remains disabled until persisted audit logging,
user controls, deletion/export handling, and seeded verification gates are
approved and implemented.

## Learning Intelligence

I1-006 adds `app/modules/assistant/learning_intelligence.py`.

Learning Intelligence supports cross-app learning prompts such as:

- What should I study today?
- Should I continue my course or revise Quiz?
- Which Quiz topic should I revise?
- What am I closest to completing?
- What have I ignored recently?
- I have one hour to study.
- Give me my learning summary.

It builds a bounded tool plan using only registered Quiz and Course Tracker
capabilities. The plan may execute at most two tools total and at most one tool
per source app. It then applies deterministic ranking rules for urgent Course
Tracker deadlines, nearest course completion, repeated weak Quiz topics,
stalled courses, recent learning continuity, next Quiz platforms, and
insufficient data.

Learning Intelligence does not import Quiz or Course Tracker models, services,
database sessions, or SQL queries. Quiz and Course Tracker remain authoritative
for app facts and app-owned recommendations; Astra owns only cross-app
orchestration and explanation. It does not add write actions, memory, OpenAI
tool orchestration, frontend contract changes, migrations, or App #101.

## Route Safety

Every returned action route is validated against the known public routes in the
index. The assistant never emits arbitrary routes derived from user text or
model output. OpenAI responses are never parsed for navigation actions.

## Response Modes

`responseMode` documents how the answer was produced:

- `deterministic`: backend retrieval generated the user-facing answer.
- `openai_grounded`: OpenAI rewrote a strong app answer from deterministic,
  bounded public context.
- `fallback`: deterministic retrieval did not find a useful public match.

Provider timeouts, HTTP errors, rejected requests, empty output, and unavailable
configuration fall back to the deterministic answer without exposing provider
details to the user.

## Current Status

Phase 2 retrieval parity, I1-002 tool framework, I1-012 registry, and I1-003
user context provider support the frozen Assistant architecture. I1-004 and
I1-005 add the Quiz and Course Tracker app pilots, and I1-006 composes those
approved capabilities for deterministic learning guidance:

```text
User -> Assistant -> Knowledge Registry / Approved Tools / Learning Intelligence -> Deterministic Response / OpenAI Grounded Public Answer -> User
```

The Assistant now reads from the Canonical AI Knowledge Registry as the normal
retrieval source and may execute registry-discovered approved read-only tools
for authenticated tool intents. It can also answer approved platform-level
personal-context questions through bounded deterministic context summaries and
combine Quiz plus Course Tracker structured tool outputs for learning
guidance. There are no embeddings, vector databases, repository search, new
OpenAI calls, permanent memory, write tools, backend workflow actions,
migrations, schema-breaking changes, or App #101 changes.

## User Context Provider

I1-003 adds the governed Platform User Context Provider in
`app/modules/assistant/user_context.py`.

The provider builds bounded context profiles:

- `minimal`
- `personalization`
- `attention`
- `tool_execution`

It validates current routes, resolves current app from the canonical catalog,
loads owner-scoped Favorites through the existing Favorites service, validates
frontend-local recent app hints against the catalog, summarizes Activity through
the existing Activity Timeline service, summarizes unread Notifications through
the existing Notifications service, and reads safe preference flags without
creating or updating preference rows.

Identity, safety, and public-knowledge questions do not load personal context.
Platform-level personal-context questions use deterministic responses. The
provider does not expose emails, tokens, backend user IDs, raw activity
metadata, full notification bodies, private app records, SQL, or source paths to
OpenAI context.

## Knowledge Foundation Phase 1 Boundary

The backend owns a generated canonical knowledge registry and a cached,
public-by-default lookup adapter. Focused parity tests cover app names, aliases,
categories, user problems, current capabilities, future-state labeling,
related apps, platform pages, route-safe actions, fallback behavior, cache
loading, and visibility filtering. The missing locked `approved-apps.md` source
remains a governance warning in the registry gap report; it is not bypassed by
assistant request-time reads.

## Future Enhancements

Future phases can add richer context, memory, personalization, and safe actions
without replacing the route validation, source filtering, frontend panel,
accessibility behavior, or deterministic action model.
