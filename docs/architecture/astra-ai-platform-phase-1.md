# Astra AI Platform Phase 1

**Status:** Implemented, pending Product Owner review and Astra source-level review
**Created:** 2026-07-24
**Scope:** Backend-only, internal, disabled by default

## Current State Findings

Ansiversa already has a user-facing Assistant route at `/api/v1/assistant`
from previous approved work, a Knowledge registry, public Knowledge routes,
an Assistant tool framework, a tool registry, a user-context provider, and
limited prior Quiz and Course Tracker Astra tool pilots. Those existing
surfaces remain unchanged by this Phase 1 foundation.

The requested `docs/ansiversa-three-level-code-review-rule.md` file was not
present in this repository at implementation time. The three-level review rule
from the assigned task is therefore carried here: Codex self-review, Product
Owner review, then Astra source-level review. This document does not mark
Phase 1 approved or frozen.

## Package

The isolated package lives at:

```text
app/modules/astra_ai
```

It contains contracts, deterministic platform fixtures, context resolution,
intent classification, policy evaluation, response planning, audit evidence,
and orchestration. It is not imported by FastAPI startup, not registered as a
route, and not connected to existing Assistant runtime behavior.

## Contracts

Phase 1 defines typed internal contracts for assistant requests,
authenticated user context, conversation context, platform context, assistant
intent, clarification, refusal, action proposal, execution status, response
classification, evidence, and audit metadata.

## Intent Vocabulary

The bounded V1 platform intent vocabulary includes platform information, app
discovery, app comparison, category discovery, navigation guidance, account
guidance, pricing/subscription guidance, legal/policy guidance, help/FAQ,
capability clarification, unsupported request, and future app-action request.

## Context Ownership

The context resolver accepts only an approved platform source bundle. It has no
database session argument, reads no arbitrary files, inspects no app records,
and does not access environment values or secrets. The default fixture
represents catalog, route registry, documentation registry, and approved
platform knowledge sources.

Permanent rule:

```text
Refuse to store or access what Astra AI does not own.
```

## Safety And Authorization

Policy evaluation is fail-closed for private app records, cross-user access,
secret/internal-data requests, prompt conflicts, anonymous private-account
requests, unsupported scope, and ambiguous prompts. Public platform guidance is
read-only. Authenticated context is treated as authorization context only, not
permission to inspect app databases.

## Orchestration

The deterministic internal flow is:

```text
Request
  ↓
Context Resolution
  ↓
Intent Classification
  ↓
Policy Evaluation
  ↓
Response Planning
  ↓
Internal Response Contract
```

No external LLM provider is called and no new provider dependency is added.

## Action Boundary

Action contracts exist only as proposals. Phase 1 never creates, updates,
deletes, sends, schedules, pays, writes to a database, or executes app
workflow behavior. Action execution status is `proposed_not_executed`.

## Audit Evidence

Audit metadata records request ID, resolved intent, policy decision,
authorization result, context sources used, refusal or clarification reason,
proposed action type, execution status, response classification, and disabled
runtime state. Evidence is deterministic and secret-scanned. It must not store
tokens, passwords, database URLs, private records, raw secrets, or uncontrolled
exception text.

## Deferred Scope

Phase 1 does not integrate any of the 100 app workflows, does not add a public
API, does not register runtime routes, does not add migrations, does not touch
frontend chat, does not modify authentication or authorization outside the
isolated policy layer, does not modify AI SEO, and does not begin Phase 2.

## Phase 2 Dependencies

Future phases require Product Owner authorization and Astra review before any
runtime route, external LLM use, persistent audit sink, consent control,
personal-data access, app database access, action execution, frontend
exposure, production configuration, or app integration can be added.
