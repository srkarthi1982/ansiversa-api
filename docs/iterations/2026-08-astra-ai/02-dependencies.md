# Astra AI Architecture Dependencies

**Status:** ASTRA-001 frozen; ASTRA-002 frozen; ASTRA-003 frozen; ASTRA-004 frozen; ASTRA-005 frozen; ASTRA-006 frozen; ASTRA-007 frozen; ASTRA-008 frozen; ASTRA-009 frozen

| Dependency | Current state | ASTRA-001 relationship |
|---|---|---|
| Astra AI Platform Phase 1 | Frozen | Internal foundation to reconcile, not reopen |
| Existing Assistant route/service | Implemented | Current runtime surface that future Astra phases may evolve |
| Knowledge Registry | Implemented and current | Governed platform truth consumed by Astra AI |
| Public Knowledge and AI SEO artifacts | Implemented/frozen phases | Public projections that Astra may consume; not replaced by Astra |
| Tool Framework and Tool Registry | Implemented | Capability discovery and execution boundary |
| User Context Provider | Implemented | Bounded platform user context provider |
| Authentication | Implemented | External identity truth source |
| Authorization/app ownership | Implemented per app/service | External permission and record ownership truth |
| Operational readiness spec | Frozen | Required before production personal-data execution |
| App `astra-ai.md` contracts | Existing for pilot apps only | Required before future app-level integration |
| Frontend shell/search/navigation | Existing in frontend repo | Future interface surfaces; not changed by ASTRA-001 |
| ASTRA-001 | Accepted and Frozen | Constitutional parent inherited by ASTRA-002 |
| ASTRA-002 | Accepted and Frozen | Intelligence-pipeline parent inherited by ASTRA-003 |
| ASTRA-003 | Accepted and Frozen | Conversation/context parent inherited by ASTRA-004 |
| ASTRA-004 | Accepted and Frozen | Capability/tool parent for future execution-planning architecture |
| ASTRA-005 | Accepted and Frozen | Execution-planning parent for future Tool Execution Architecture |
| ASTRA-006 | Accepted and Frozen | Tool-execution parent for future provider, memory, learning, and governance architecture |
| ASTRA-007 | Accepted and Frozen | Provider architecture parent for future memory, learning, and governance architecture |
| ASTRA-008 | Accepted and Frozen | Memory architecture parent for future learning and governance architecture |
| ASTRA-009 | Accepted and Frozen | Learning and adaptation architecture parent for future safety, audit, and governance architecture |
| External model providers | Not integrated by ASTRA-002 | Optional future capability, never the default path |

---

# Blocking Dependencies Before Implementation

- ASTRA-004 review, Product Owner approval, and freeze before implementing
  capability discovery or tool behavior;
- ASTRA-005 is frozen, but separate Product Owner authorization is still
  required before implementing execution-planning behavior;
- ASTRA-006 is frozen, but separate Product Owner authorization is still
  required before implementing Tool Executor handoff or execution monitoring
  behavior;
- ASTRA-007 is frozen, but separate Product Owner authorization is still
  required before implementing provider routing, prompts, model invocation, or
  provider integration;
- ASTRA-008 is frozen, but separate Product Owner authorization is still
  required before implementing runtime memory, memory storage, memory
  retrieval, vector databases, embeddings, deletion/export controls, or memory
  UI behavior;
- ASTRA-009 is frozen, but separate Product Owner authorization is still
  required before implementing runtime learning, model training, fine-tuning,
  embeddings, vector databases, adaptation storage, adaptation controls, or
  personalization behavior;
- separate Product Owner authorization before implementing conversation or
  context behavior from ASTRA-003;
- Product Owner authorization for a named implementation phase;
- source-level Astra review of the proposed implementation task;
- explicit non-goals and rollback boundaries;
- persistent audit decision before personal-data execution;
- user controls before memory or proactive behavior; and
- per-app contracts before app-specific tools or cross-app orchestration.
