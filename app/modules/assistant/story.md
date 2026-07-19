# Ansiversa AI Assistant

## Purpose

Ansiversa AI Assistant is the platform help and navigation assistant. Phase 3
keeps retrieval, routing, and source authority deterministic while allowing a
server-side OpenAI provider to turn approved public context into clearer prose.

## Workflow

The frontend sends a user message to `POST /api/v1/assistant/query`. The
backend builds a public knowledge index from the Apps catalog, public overview
metadata, platform page summaries, and published user-facing FAQs. It first
produces a deterministic answer, validated navigation actions, safe source
metadata, and confidence. Strong app-information queries may then send only
bounded public context to OpenAI for response wording. Platform navigation,
unknown queries, weak matches, and provider failures use the deterministic path.

## API Design

Request:

```json
{ "message": "pricing" }
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

Phase 3 uses the OpenAI Responses API only as an optional explanation layer.
There are no embeddings, vector databases, repository search, tool calls,
backend workflow actions, or schema changes.

## Future Enhancements

Future phases can add richer context, memory, personalization, and safe actions
without replacing the route validation, source filtering, frontend panel,
accessibility behavior, or deterministic action model.
