# Ansiversa AI Assistant

## Purpose

Ansiversa AI Assistant is the platform help and navigation assistant. Phase 4
keeps routing and source authority deterministic while using session-only
frontend context to improve relevance. AI Knowledge Foundation Phase 2 migrates
retrieval to the Canonical AI Knowledge Registry. OpenAI remains only an
optional server-side explanation layer for approved grounded results.

## Workflow

The frontend sends a user message and optional session context to
`POST /api/v1/assistant/query`. The backend builds a public knowledge index from
the cached Canonical AI Knowledge Registry. The registry already contains the
approved app catalog facts, overview routes, platform/account/legal page
knowledge, categories, aliases, capabilities, user problems, related apps,
future direction, visibility, and source traceability. The assistant first
applies deterministic context handling for current page/app follow-ups,
last-opened-app navigation, recent app references, and favorite/recent
preference. It then produces a deterministic answer, validated navigation
actions, safe source metadata, and confidence. Strong app-information queries
may send only bounded public context plus concise session context to OpenAI for
response wording. Platform navigation, unknown queries, weak matches, explicit
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

Phase 2 retrieval parity supports the frozen assistant architecture:

```text
User -> Knowledge Retriever -> Canonical AI Knowledge Registry -> OpenAI -> User
```

The Assistant now reads from the Canonical AI Knowledge Registry as the normal
retrieval source. There are no embeddings, vector databases, repository search,
new OpenAI calls, permanent memory, tool calls, backend workflow actions,
migrations, or schema-breaking changes.

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
