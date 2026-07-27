# ASTRA-IMP-008 Constitution-to-code mapping

| Source | Mapping |
|---|---|
| ASTRA-001 | Runtime identity and one runtime-owned engine |
| ASTRA-002 | Rule-based canonical construction; no model or autonomy |
| ASTRA-003 | Bounded references; no conversation payload or memory conversion |
| ASTRA-004 | Governed metadata visibility never grants execution |
| ASTRA-005 | Proposal, intent, and approval metadata stay non-authoritative |
| ASTRA-006 | No execution; owner acceptance required and not accepted |
| ASTRA-007 | No providers, prompts, SDKs, or model influence |
| ASTRA-008 | No memory, embeddings, vectors, or retrieval |
| ASTRA-009 | No learning, adaptation, or mutable policy |
| ASTRA-010 | Safety/authority, fail closed, empty non-ALLOW steps, evidence integrity, production separation |
| ASTRA-IR-001 | Certified dependency order extended only to planning |
| IMP-001/002 | Reused contracts and authoritative configuration |
| IMP-003/004 | Reused deterministic governance and bounded evidence |
| IMP-005 | Reused ownership, registration, lifecycle, invalidation, health |
| IMP-006 | Verified engine ownership, fresh snapshot, runtime, lifecycle |
| IMP-007 | Used owner-issued context and governed metadata only |

| Requirement | Code |
|---|---|
| Request/plan contracts | `AstraPlanningRequest`, `AstraProposedPlan` |
| Step/dependency model | `AstraRequestedPlanStep`, `_validate_graph` |
| Status table | `_status_for`, `_blocked_plan` |
| Evidence atomicity | `_append_evidence_then_release` |
| Runtime integration | `AstraRuntimePlanningInterface`, `planning` registration |
| Structural health | `AstraPlanningHealthSnapshot` |
