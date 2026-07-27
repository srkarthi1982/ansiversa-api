# ASTRA-VAL-002 — Projection Integrity and Privacy Validation

Status: Implemented; pending Astra source review.

## Architecture

ASTRA-VAL-002 is an observational local validation harness over the certified
ASTRA-IMP-011 Runtime interface. One shared runner supplies pytest and a thin
CLI. It creates isolated deterministic Runtime assemblies, invokes only
certified construction and operation paths, and compares actual immutable
outputs with fixed expectations. It does not implement projection logic,
replace outcomes, create authority, or modify parent state.

Reports are bounded immutable scenario results. Text and stable sorted JSON are
written to stdout only. Reports, temporary files, and generated certification
artifacts are not persisted.

## Deterministic comparison contract

Fixtures fix Runtime IDs, request/object/evidence IDs, timestamps, ordering, and
capacities. The narrow semantic serializer excludes only independently issued
request/evidence identity and issuance time. It compares exactly:

- projection kind, completeness, and redaction;
- Runtime/configuration and component states;
- correlation relationships, proof states, and reason codes;
- evidence contract, provenance, digest, and overall-integrity states;
- timeline content, timestamps, ordering, redaction, and truncation;
- internal-only exposure flags.

No meaningful state is normalized or omitted.

## Privacy inspection and strict-redaction matrix

The complete serialized projection is inspected recursively at the root and
through its manifest, links, components, evidence summaries, timeline, and
reason metadata. Tests search for actual protected fixture references and
prohibited authority, credential, raw-message, prompt, hidden-reasoning,
database, provider, and Runtime-handle vocabulary.

The inspector is itself validated with controlled test-only negative fixtures
for authority tokens, proof objects, credentials, query strings, provider
payloads, protected evidence/conversation references, and Runtime handles.
Every injected violation must produce a deterministic finding path; a clean
redacted control must produce none.

| Strict field | Expected |
|---|---|
| conversation/current-turn/intent/plan/read references | `null` |
| component references | `null` |
| manifest evidence references | empty |
| correlation source/target references | `[redacted]` |
| evidence reference | `[redacted]` |
| source system/provenance/recorded digest | `null` |
| timeline reference | `[redacted]` |
| timeline evidence reference | `null` |
| completeness/redaction/reason | `redacted` / `redacted` / `redacted_by_sensitivity` |

Stage names, bounded states, integrity statuses, reason codes, and permitted
timestamps may remain. Unknown sensitivity is rejected by the certified
contract and never falls back to permissive exposure.

## Correlation and evidence integrity

Only explicit certified links may be proven. Conversation-to-turn,
intent-to-conversation/current-turn, and plan-to-conversation links are checked.
Intent-to-plan remains missing even for the same Runtime, conversation,
capability, or timestamps. Different certified conversation references remain
conflicting. Missing relationships do not create timeline events.

Evidence resolves through the owning Runtime Evidence Sink only. A structurally
resolved record must report `resolved`, `valid`, `valid_structural`,
`not_reproducible`, and `resolved_structural`. Digest format never becomes
verification. Missing or foreign references remain missing. Every returned
projection evidence reference must resolve in the owning sink, proving
projection-operation evidence was appended before release.

## Completeness, timeline, atomicity, and lifecycle

Validation preserves:

```text
unavailable > redacted > partial > complete
```

`not_applicable`, `missing`, `blocked`, `not_reached`, and `conflicting` remain
distinct stage/proof states. Timelines use certified timestamps, deterministic
reference/stage tie-breaking, a maximum of 50 entries, explicit truncation, and
no pagination, continuation, enumeration, or synthetic gap entries.

Atomic failure uses a Runtime constructed with bounded Evidence Sink capacity,
fills that capacity through certified append, and invokes projection normally.
Append failure releases no projection, advances no successful sequence, changes
no parent Runtime state, and leaves evidence count bounded. No append
monkeypatch or private Evidence Sink mutation is used.

Captured Runtime interfaces fail after shutdown; stopped component health is
truthful; projection health may be healthy while operational read authorization
remains fail-closed/degraded.

## CLI and exposure boundary

```text
python -m validation.astra_val_002.cli --list
python -m validation.astra_val_002.cli --scenario strict_redaction_no_leak
python -m validation.astra_val_002.cli --scenario deterministic_projection --format json
python -m validation.astra_val_002.cli --all --format text
python -m validation.astra_val_002.cli --all --format json
```

Exit codes are 0 pass, 1 expectation mismatch, 2 invalid use/unknown scenario,
and 3 setup failure. The harness adds no API, route, UI, telemetry, monitoring,
persistence, database, ORM, SQL, retrieval, mutation, provider, prompt, model,
execution, deployment, production configuration, or production activation.

Tests independently parse the runner contract, text CLI rows, and JSON CLI
object for the same strict scenario and require exact equality across passed
state, expected/actual outcome, projection kind, completeness, and redaction.
This proves the CLI is presentation only.
