# Astra Governed Planning Engine

Status: ASTRA-IMP-008 implemented; source review and certification pending. Production authorization is not approved and production is unchanged.

## Boundary and contracts

`AstraRuntime` owns exactly one lifecycle-bound `AstraPlanningEngine`. It prepares immutable advisory proposals and has no handler, callable, command, provider, prompt, Tool Executor, persistence, business payload, API, or execution method. Governance allow, discovery visibility, conversation ownership, user intent, approval metadata, and runtime readiness do not authorize execution.

Planning without a conversation is rejected. Every request names a current immutable snapshot owned by the supplied certified `AstraConversationContextEngine`, from the same runtime, and not closed or faulted. Only its identifier and version enter the plan.

`AstraPlanningRequest` and `AstraRequestedPlanStep` are frozen, extra-forbidden, bounded metadata contracts. `AstraProposedPlanStep` contains capability, ordering, reference, dependency, authority, safety, approval, owner-acceptance, and fixed authorization metadata only. `AstraProposedPlan` contains deterministic identity, bounded references, status, governance, ordered steps, evidence, approval/acceptance, failure posture, and provenance.

```text
execution_authorization_state = not_authorized
production_authorization_state = not_approved
```

## Deterministic rule and dependency model

The caller supplies the complete ordered shape; the engine does not invent strategy.

| Rule | Result |
|---|---|
| Valid, governed ALLOW input | `proposed`, ordered metadata-only steps |
| CLARIFY | `clarification_required`, no steps |
| DEFER | `deferred`, no steps |
| REFUSE | `refused`, no steps |
| CONTAIN | `contained`, no steps |
| FAIL_CLOSED | `governance_blocked`, no steps |
| Invalid graph or ineligible capability | reject before planning commit |

Sequence starts at one and is contiguous. Step and capability identifiers are unique. Dependencies are unique, exist, and point backward, excluding self/forward dependencies and cycles. The maximum is twenty.

## Capability, conversation, and evidence flow

```text
validated request -> ready runtime -> current owned conversation
  -> dependency graph -> governed discovery metadata -> capability eligibility
  -> plan governance -> immutable plan -> bounded evidence append -> release
```

Capability data comes only through governed Capability Discovery with runtime-issued authority, never registry private storage. Evidence is references-only and append-before-release. Append failure releases no plan and does not advance the successful sequence or mutate dependencies.

## Registration and structural health

| Identifier | Owner | Implementation | Access |
|---|---|---|---|
| `planning` | Astra Runtime Core | ASTRA-IMP-008 | lifecycle-bound interface |

Health covers registration/availability, configuration, discovery, conversation dependency, governance, evidence, last successful sequence, outcome, and timestamp. It contains no provider, execution, model, database, workflow, or user-content health.
