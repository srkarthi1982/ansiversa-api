# Ansiversa AI Assistant

## Purpose

Ansiversa AI Assistant is the platform help and navigation assistant. Phase 2
keeps the assistant deterministic and backend-owned while preparing the system
for a future AI provider.

## Workflow

The frontend sends a user message to `POST /api/v1/assistant/query`. The
backend builds a public knowledge index from the Apps catalog, public overview
metadata, platform page summaries, and published user-facing FAQs. It returns a
grounded answer, validated navigation actions, safe source metadata, and a
confidence value.

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
  "confidence": "high"
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

## Retrieval Design

The retrieval service is a deterministic hybrid matcher. It supports exact app
names, aliases, slugs, title phrases, categories, keywords, and platform page
terms. Ranking favors exact canonical app names first, then aliases, slugs,
title phrases, category matches, description keywords, and platform keywords.

## Route Safety

Every returned action route is validated against the known public routes in the
index. The assistant never emits arbitrary routes derived from user text.

## Current Status

Phase 2 is backend retrieval foundation only. It does not call OpenAI, external
AI providers, embeddings, tools, or backend workflow actions.

## Future Enhancements

Future phases can replace the response provider with OpenAI while keeping the
same API contract, route validation, frontend panel, accessibility behavior,
and navigation action model.
