# ASTRA-IMP-011 — Diagnostic Evidence Projection Engine

Status: Implemented; pending Astra source review.

## Boundary

The Runtime-owned engine converts exact certified immutable snapshots and Runtime-sink evidence references into immutable, bounded, redacted, internal-only diagnostic projections. It is observational: it creates no authority, correlation, explanation, execution, data access, external exposure, or production activation.

Certified tests and ASTRA-VAL-001 retain direct Runtime access. Future APIs, UIs, dashboards, telemetry, monitoring, and external services require separately authorized projections and consumers.

## Request authority and accepted inputs

Runtime issues an exact request object backed by an opaque engine-owned token and bounded private issuance registry. Copies, reconstructions, field changes, foreign Runtime requests, expired requests, unknown requests, and post-shutdown requests fail. Requests expire after 15 minutes, select fixed projection kinds/sections, and allow at most 50 timeline entries.

Accepted inputs are exact Runtime-produced `AstraRuntimeHealthSnapshot`, `AstraIntentResolution`, `AstraProposedPlan`, `AstraReadAuthorizationDecision`, and certified component-health contracts. A conversation snapshot additionally requires current ownership validation through its certified Conversation Context Engine at request issuance. Dictionaries, Runtime objects, stores, registries, proof issuers, tokens, and mutable interfaces are rejected.

Projection kinds are `runtime_summary`, `request_diagnostic`, `evidence_summary`, and `component_health_summary`. There is no list-all or global enumeration operation.

## Explicit correlation model

The projection-owned manifest reports only links already explicit in certified contracts:

- conversation to current turn;
- intent to conversation/current turn;
- plan to conversation;
- objects to their declared evidence references.

Supplying two objects together, shared IDs, equal timestamps, capability similarity, or ordering never proves a relationship. Intent-to-plan remains `missing` with `certified_intent_plan_reference_absent`; conflicting certified references remain `conflicting`. Historical links are never reconstructed and missing stages do not receive synthetic timeline entries.

## Evidence matrix

| Projection | Required | Optional | Missing behavior |
|---|---|---|---|
| Runtime summary | exact Runtime health; projection-operation evidence | requested component evidence | required → unavailable; optional → partial |
| Request diagnostic | each requested exact stage object; all object-declared evidence; operation evidence | unproven cross-stage links and unrequested stages | required → unavailable; missing correlation → partial |
| Evidence summary | every requested sink reference; valid evidence contract; operation evidence | none | missing → unavailable |
| Component health | each requested exact health snapshot; operation evidence | unrequested components | missing requested → unavailable; unrequested → not applicable |

## Structural integrity

Evidence is resolved only through the owning Runtime Evidence Sink. Summaries independently report reference, contract, provenance, digest, and overall statuses. `resolved_structural` means only that the exact reference resolved, validated as `BoundedEvidence`, matched its ID, and contained structurally valid provenance metadata.

The default digest status is `not_reproducible`. The engine does not claim external audit, factual correctness, legal attestation, independent digest recomputation, or production approval. `verified` is unavailable until a separately certified producer-owned verification contract exists.

## Completeness and redaction

Overall precedence is:

```text
unavailable > redacted > partial > complete
```

Missing required evidence is unavailable. Sensitivity-required omission is redacted. Missing optional evidence/correlation or timeline truncation is partial. `not_applicable` is a stage state, not overall completeness. Strict minimization permits references, fixed states, timestamps, reason codes, and structural metadata only.

## Timeline

Timelines include only supplied certified objects and resolved evidence. Ordering uses certified timestamps followed by reference and stage. Maximum length is 50. Overflow sets `truncated=true`, `remaining_entries_unavailable=true`, completeness `partial`, and reason `timeline_truncated`. Pagination and continuation tokens do not exist.

## Evidence-before-release

```text
validate lifecycle and exact request
→ validate certified inputs
→ resolve Runtime evidence
→ calculate explicit correlation
→ minimize/redact
→ calculate completeness and timeline
→ prepare projection
→ append projection-operation evidence
→ release projection
```

Append failure releases no projection, advances no successful sequence, and returns no manifest or timeline.

## Health and exposure

Projection health means only that truthful bounded projections can be produced. It may be healthy while authoritative configuration is disabled, governance fails closed, planning is blocked, and read authorization is degraded.

Every projection fixes:

```text
internal_only                 true
api_exposure_authorized       false
ui_exposure_authorized        false
public_access_authorized      false
production_exposure_approved  false
```

No API, UI, authentication, persistence, telemetry, monitoring integration, database, SQL, ORM, retrieval, execution, provider, prompt, model, deployment, or production behavior is introduced.
