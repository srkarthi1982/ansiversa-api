# Astra AI Architecture Dependencies

**Status:** ASTRA-001 frozen; ASTRA-002 frozen; ASTRA-003 frozen

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
| External model providers | Not integrated by ASTRA-002 | Optional future capability, never the default path |

---

# Blocking Dependencies Before Implementation

- ASTRA-004 review, Product Owner approval, and freeze before implementing
  capability discovery or tool behavior;
- separate Product Owner authorization before implementing conversation or
  context behavior from ASTRA-003;
- Product Owner authorization for a named implementation phase;
- source-level Astra review of the proposed implementation task;
- explicit non-goals and rollback boundaries;
- persistent audit decision before personal-data execution;
- user controls before memory or proactive behavior; and
- per-app contracts before app-specific tools or cross-app orchestration.
