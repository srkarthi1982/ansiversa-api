# Ansiversa AI Assistant

## Purpose

Ansiversa AI Assistant is the platform help and navigation assistant. Phase 4
keeps retrieval, routing, and source authority deterministic while using
session-only frontend context to improve relevance. OpenAI remains only an
optional server-side explanation layer for approved grounded results.

## Workflow

The frontend sends a user message and optional session context to
`POST /api/v1/assistant/query`. The backend builds a public knowledge index from
the Apps catalog, public overview metadata, platform page summaries, and
published user-facing FAQs. It first applies deterministic context handling for
current page/app follow-ups, last-opened-app navigation, recent app references,
and favorite/recent preference. It then produces a deterministic answer,
validated navigation actions, safe source metadata, and confidence. Strong
app-information queries may send only bounded public context plus concise
session context to OpenAI for response wording. Platform navigation, unknown
queries, weak matches, and provider failures use the deterministic path.

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

- Public Apps catalog facts
- Public overview routes and descriptions
- Public platform, account, and legal page summaries
- Published user-facing FAQ content

Internal governance files, credentials, environment details, certification
evidence, user records, test data, raw operational instructions, and unreleased
promises are excluded.

OpenAI receives only the user question, a concise system instruction, public
source titles, source types, categories, summaries, and permitted action labels.
It does not receive routes, internal docs, database internals, repository
content, secrets, certification evidence, private user data, or speculative
roadmap material.

## Retrieval Design

The retrieval service is a deterministic hybrid matcher. It supports exact app
names, aliases, slugs, title phrases, categories, keywords, and platform page
terms. Ranking favors exact canonical app names first, then aliases, slugs,
title phrases, category matches, description keywords, and platform keywords.
Session context can boost matching favorite and recent apps, resolve current
page/app follow-up questions, and answer "go back" requests through the last
opened app. Context improves retrieval only; it does not authorize new routes,
new actions, or general chat behavior.

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

Phase 4 supports the frozen assistant architecture:

```text
Context improves retrieval.
Retrieval stays deterministic.
OpenAI only explains grounded results.
```

There are no embeddings, vector databases, repository search, permanent memory,
tool calls, backend workflow actions, migrations, or schema-breaking changes.

## Knowledge Foundation Phase 1 Boundary

The backend now owns a generated canonical knowledge registry and a cached,
public-by-default lookup adapter. Focused parity tests cover app names, aliases,
categories, user problems, current capabilities, future-state labeling,
related apps, and visibility filtering. Phase 1 does not replace
`build_knowledge_index` or change `/assistant/query`; production answers and
OpenAI gating remain exactly as before. The registry is ready for a controlled
Phase 2 retriever comparison after the missing locked `approved-apps.md` source
is restored or formally superseded.

## Future Enhancements

Future phases can add richer context, memory, personalization, and safe actions
without replacing the route validation, source filtering, frontend panel,
accessibility behavior, or deterministic action model.
