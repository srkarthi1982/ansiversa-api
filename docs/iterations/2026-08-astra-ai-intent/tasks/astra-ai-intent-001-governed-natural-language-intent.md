# ASTRA-AI-INTENT-ARCH-001 — Governed Natural-Language Intent Boundary

Status: Architecture Proposed / Pending Astra Review

Canonical task: `srkarthi1982/ansiversa-api#5`

Gate release: issue comment `5215395273`

Authorization: documentation and contract only; implementation not authorized

Production: NOT APPROVED

## Objective

Propose the boundary that translates a current natural-language question into
one untrusted candidate for a certified Subscription Manager read, then
independently validates it before invoking unchanged ASTRA-CHAT-001.

## Deliverables

- architecture, threat-model, and contract documents;
- this future implementation design record;
- Astra natural-language architecture memory;
- Astra current checkpoint update;
- permanent GitHub-first governed capability-delivery workflow source; and
- required backend and Astra task-log updates.

## Proposed Decisions

- separate `POST /api/v1/astra/agent/query` endpoint;
- current-turn, intent-only provider boundary;
- exact deterministic mapping before provider use;
- app-owned certified catalog as sole provenance;
- strict candidate with no authority fields;
- deterministic capability/parameter validation;
- server construction of existing `AstraChatRequest`;
- no tools, DB, writes, model answer, or persistent memory;
- default-off server-owned non-production configuration; and
- safe metadata observability with no raw prompt persistence by default.

## Future Implementation Design — Not Authorized

A separate approved GitHub issue may add only:

1. intent schemas and validator;
2. metadata projector over the existing app-owned catalog;
3. exact-question server fast path;
4. intent-specific provider client with structured output and zero retries;
5. authenticated, non-production, default-off agent endpoint;
6. in-process handoff to certified chat;
7. safe evidence and bounded failures; and
8. unit, security, API, provenance, browser, and owner-isolation tests.

It must identify its exact base, certify the new boundary separately, stop
before frontend work, and avoid changing certified components for convenience.

## Frozen Prerequisites

```text
ASTRA-RUNTIME-ACT-001       Certified / Frozen
ASTRA-READ-AUTH-BIND-001    Certified / Approved / Closed
ASTRA-META-ACT-BIND-001     Certified / Approved / Frozen
ASTRA-READ-EXEC-001         Certified / Approved
ASTRA-CHAT-001              Certified / Approved
ASTRA-FE-CHAT-001           Certified / Approved / Closed
Production                  NOT APPROVED
```

Certified backend chat: `4d7d25fd1f95ef7fd3912a1cdc21ef43729e8646`.

Certified frontend: `32930b69e8d296f383e2c9846bf5e69c231589a1`.

## Explicit Non-Goals

No executable source, provider/model call, route, frontend, Runtime, chat,
authority, execution, Subscription Manager, DB, schema, migration,
configuration, dependency, tool/function calling, RAG, embedding, vector DB,
memory, autonomous agent, write, adapter, deployment, merge, or production
change is authorized.

## Completion Gate

Commit and push backend documentation, synchronize and separately push Astra
sources, open a draft architecture PR, report exact commits/files/findings in
issue #5, then stop.

```text
ASTRA-AI-INTENT-ARCH-001 — Architecture Proposed / Pending Astra Review
```
