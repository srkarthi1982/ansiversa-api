# Iteration 1 Planning Readiness Audit

**Date:** 2026-07-22
**Repository:** `ansiversa-api`
**Path Reviewed:** `docs/iterations/2026-07-next/`
**Audit Scope:** Documentation and architecture planning only. No production code implementation was started.

---

# Executive Summary

The Iteration 1 planning package is directionally strong and preserves the major Ansiversa platform boundaries: fixed 100-app ecosystem, no App #101, app-owned business logic, backend-owned identity, read-only personal-data tools in Phase 1, deterministic safety/identity priority, and the existing Assistant response modes.

The package required freeze corrections for backlog/status consistency,
dependency documentation, implementation sequencing, Astra orchestration
boundaries, validation centralization, and capacity planning.

**Overall readiness result:** PASS WITH CHANGES

Freeze should proceed only with the corrected planning package and the remaining
architectural decisions explicitly tracked.

---

# Backlog Integrity Findings

- All task files from `tasks/001` through `tasks/022` exist exactly once.
- Programmatic read check passed for the original 29 Markdown files in the iteration package.
- Task file IDs and top-level task headings are internally consistent.
- No duplicate task files or missing numeric IDs were found.
- I1-022 uses the canonical name `Platform Insights Dashboard`.
- Planning status terminology is normalized to the backlog legend.
- Implementation-window tasks use `Frozen`.
- Later-iteration tasks use `Deferred`.
- I1-001 priority is normalized to `Critical`.

---

# Dependency Findings

No circular dependency was detected from explicit `Depends On` references.

`02-dependencies.md` now defines dependencies, blockers, parallel
opportunities, a simple graph, and implementation waves for I1-001 through
I1-022.

Broad dependency ranges were replaced with explicit prerequisite relationships.
I1-009 now leads Wave 1 as the contract/specification gate.

Parallel candidates:

- I1-007 Notifications Center UI Refinement can run independently after confirming the existing Notifications API contract.
- I1-019 Accessibility Improvements can run as a focused audit/fix track.
- I1-020 Mobile Experience Improvements can run independently if scoped to shell/platform layout defects.
- I1-021 Performance Improvements can run as measurement-first work, then focused fixes.
- I1-022 Platform Insights Dashboard should be deferred or run only after metrics sources are defined.

---

# Architecture Findings

The package consistently preserves these required architecture rules:

- Exactly 100 solution apps.
- No App #101.
- Applications own business logic and Astra capabilities.
- Astra owns orchestration.
- User identity is backend-owned.
- OpenAI cannot generate SQL.
- OpenAI cannot choose or override user identity.
- Personal-data tools are authenticated, owner-scoped, bounded, and read-only in Phase 1.
- Deterministic identity and safety routing remain higher priority than tool or model routing.
- Existing response modes remain `deterministic`, `openai_grounded`, and `fallback`.

Architecture risks to resolve before freeze:

- I1-002 includes an Assistant Tool Registry, while I1-012 separately defines Astra Tool Registry. The boundary must be clarified before either task is assigned.
- I1-013 Intent Engine and I1-014 Response Builder appear to extract pieces from the existing Assistant service. They must be framed as refactoring/extension of the existing behavior, not replacement architecture.
- I1-015 Recommendation Engine must not centralize app-specific recommendation rules. It should rank and present app-owned recommendations only.
- I1-018 Universal Recent Items could overlap with the existing Activity Timeline and frontend `useRecentAppsStore`; the source of truth must be approved before implementation.

---

# Duplication Findings

Potential overlap requiring refinement:

- I1-002 Astra AI Tool Framework: should own tool definition, execution context, read-only enforcement, executor contract, and integration with the Assistant endpoint.
- I1-012 Astra Tool Registry: owns registration, discovery, metadata, versioning, and enable/disable state.
- I1-013 Astra Intent Engine: should own intent classification and routing priority only.
- I1-014 Astra Response Builder: should own final response assembly only.
- I1-015 Astra Recommendation Engine: should own ranking of already-approved recommendations only.

Second overlap group:

- I1-003 Platform User Context Provider: backend-owned current user/app/favorite/recent/activity context snapshot.
- I1-010 Astra Conversation Context: per-session follow-up context, already partially represented by current Assistant client context.
- I1-011 Astra Memory Management: persistent or semi-persistent memory governance; this has higher privacy risk and should likely move later.
- I1-018 Universal Recent Items: owner-scoped recent records; may be better derived from Activity Timeline than introduced as a second persistence model.

Responsibility recommendation:

- Keep I1-002 and I1-012 separate under the Single Responsibility Principle.
- I1-002 owns execution, authentication, authorization, lifecycle, read-only enforcement, and the execution pipeline.
- I1-012 owns registration, discovery, metadata, versioning, and enable/disable state.
- Keep I1-010 as bounded session context.
- Defer I1-011 persistent memory until consent, deletion, retention, and audit requirements are approved.

---

# Existing-System Alignment Findings

Current backend capabilities already partially exist:

- `app/modules/assistant` already has deterministic retrieval, OpenAI grounded fallback, response modes, validated actions, public registry-backed knowledge, client context, identity/safety routing, and tests.
- `app/modules/knowledge` already has registry build/check/public validation modules.
- `app/modules/activity` already provides an owner-scoped Activity Timeline, bounded retention, route validation, and summary/list APIs.
- `app/modules/notifications` already provides owner-scoped notifications, unread state, preferences, route validation, and safe serialization.
- `app/modules/auth` already provides backend-owned current-user resolution and admin dependency support.
- Knowledge artifacts currently contain 100 apps and 14 categories.

Current frontend capabilities already partially exist:

- `AvAiAssistant`, `assistantContext`, `assistantRouter`, `assistantService`, and `useAiAssistant`.
- `AvCommandPalette`, command palette search index, and command palette store.
- Dashboard page with favorites, recent apps, activity preview, Astra entry point, and command palette entry point.
- Notifications Center and Notification store.
- Activity page/store/shared list.
- Favorites store and local recent apps store.
- Search page/module.

Planning implication:

- Most tasks should be written as extension or extraction work from existing modules, not greenfield builds.
- Any proposed new module names should be checked against existing conventions under `app/modules/*`, `src/shared/*`, and `src/modules/*` before implementation.
- I1-018 must explicitly decide whether to replace local recent apps, extend Activity Timeline, or create a separate universal recent table.

---

# Security And Privacy Findings

The documents identify the major security boundaries, but the package needs stronger implementation-level governance before freeze:

- Cross-user access: every tool must prove backend-injected owner identity and reject caller/model-supplied owner IDs.
- Sensitive-data minimization: tool outputs must define exact bounded fields per tool before implementation.
- Logging: no raw prompts, full context payloads, SQL, tokens, emails, user IDs sent to OpenAI, stack traces, or tool raw payloads should be logged.
- OpenAI boundary: model input should include only approved summaries and deterministic facts, never schema, SQL, internal IDs, or raw personal records.
- Tool-output leakage: response builder must prevent one tool's private output from being reused in another user's session or public/fallback answer.
- Memory/privacy: I1-011 needs consent, preference, retention, deletion, export, and audit requirements before implementation.
- External model context: personal context forwarding should require explicit field allowlists and should be disabled for identity, safety, and public-catalog questions.
- Audit: tool execution should record bounded audit metadata, but the current package does not define whether this uses Activity Timeline, AuditLogs, or a new assistant audit table.

Required pre-freeze decision:

- Choose the audit sink for personal-data tool execution and define retention/deletion behavior.

---

# Validation Findings

Executable checks confirmed:

- All 30 Markdown files under `docs/iterations/2026-07-next/`, including this audit report, are readable.
- `git diff --check` passed in `ansiversa-api`.
- Frontend scripts exist for `npm run typecheck`, `npm run lint`, `npm run build`, `npm run api:types`, and Playwright platform tests.
- Backend knowledge validation modules exist for registry/public checks.

Validation gaps:

- Several task files reference tests that do not exist yet:
  - `tests/test_assistant_tools.py`
  - `tests/test_quiz_astra_tools.py`
  - `tests/test_course_tracker_astra_tools.py`
- `ansiversa-api` does not have `pyproject.toml`, `Makefile`, or `package.json`; backend validation commands should use the existing `.venv`/`pytest`/`compileall` style.
- Browser matrices are repeated inside large tasks and should be centralized in `04-validation-plan.md`.
- Production verification steps require authenticated test accounts and seeded user data for Quiz, Course Tracker, Notifications, Activity, and Astra. The package should identify who owns seed data and which environment is used.
- Security validation is present at a checklist level but missing concrete test cases for cross-user access, prompt injection with tool access, OpenAI personal-context minimization, and memory deletion/retention.
- Migration verification should be required only for tasks that add or alter persistent storage.

---

# Capacity Assessment

The full 22-task backlog is not realistic for 2026-07-26 through 2026-08-09 if implementation, validation, documentation, deployment, manual browser verification, Astra review, and Partner approval are all included.

| Task | Classification | Feasibility Notes |
|---|---|---|
| I1-001 | Must complete | Architecture foundation, but should be narrowed to Phase 1 contract and approved boundaries before coding. |
| I1-002 | Must complete | Core execution framework; separate from I1-012 registry metadata. |
| I1-003 | Must complete | Needed for authenticated context; must extend existing backend/frontend Assistant context safely. |
| I1-004 | Should complete | First app pilot; feasible after I1-002/I1-003 and test seed plan. |
| I1-005 | Stretch | Second app pilot; depends on I1-004 learnings and may exceed window. |
| I1-006 | Defer | Cross-app learning intelligence is too broad for the same iteration as two app pilots. |
| I1-007 | Should complete | Independent UI refinement if scoped to current Notifications Center. |
| I1-008 | Stretch | Needs sharper distinction from I1-015 and dashboard data sources. |
| I1-009 | Must complete | Should move before pilots as the contract/specification gate. |
| I1-010 | Should complete | Current context exists; implement as bounded follow-up enhancement. |
| I1-011 | Defer | Persistent memory needs consent, retention, deletion, and audit decisions. |
| I1-012 | Must complete | Registry metadata/discovery task; separate from I1-002 execution. |
| I1-013 | Stretch | Useful extraction, but should wait until tool framework and first pilot expose real routing needs. |
| I1-014 | Stretch | Useful extraction, but should follow I1-013 or remain inside service for now. |
| I1-015 | Defer | Recommendation ranking over personal data and multiple apps is too broad for this window. |
| I1-016 | Should complete | Can improve existing Search independently if Astra adapter is scoped later. |
| I1-017 | Stretch | Best after I1-016; avoid duplicate search logic. |
| I1-018 | Defer | Needs source-of-truth decision versus Activity Timeline/local recent apps. |
| I1-019 | Should complete | Good independent quality track if scoped to shell/high-traffic surfaces. |
| I1-020 | Stretch | Broad platform UX task; should be defect-list driven. |
| I1-021 | Should complete | Measurement-first performance pass is feasible; broad optimization is not. |
| I1-022 | Defer | Low priority and admin/metrics scope needs approval. |

---

# Recommended Implementation Waves

Wave 0: Freeze corrections and contracts

- Fix backlog naming/status terminology.
- Maintain `02-dependencies.md` as the authoritative dependency and wave document.
- Approve audit sink, retention/deletion policy, and personal-context OpenAI allowlist.
- Keep I1-002 and I1-012 separate with documented responsibilities.

Wave 1: Astra safety foundation

- I1-009 Astra AI Integration Contract.
- I1-001 Astra AI User Data Awareness Phase 1.
- I1-002 Astra AI Tool Framework.
- I1-012 Astra Tool Registry.
- I1-003 Platform User Context Provider.

Wave 2: First proof and user-visible refinement

- I1-004 Quiz Astra AI Integration.
- I1-010 bounded conversation context.
- I1-007 Notifications Center UI Refinement.
- I1-019 focused accessibility pass.

Wave 3: Platform discovery and performance

- I1-016 Global Search Enhancements.
- I1-017 Command Palette Enhancements.
- I1-018 Universal Recent Items.
- I1-021 Performance Improvements.
- I1-020 Mobile Experience Improvements.

Wave 4: Astra refinement

- I1-005 Course Tracker Astra AI Integration.
- I1-008 Dashboard Intelligence.
- I1-013 Intent Engine.
- I1-014 Response Builder.

Later iteration

- I1-006 Learning Intelligence.
- I1-011 Memory Management.
- I1-015 Recommendation Engine.
- I1-022 Platform Insights Dashboard.

---

# Required Changes Before Planning Freeze

1. Keep I1-022 named `Platform Insights Dashboard` across the package.
2. Keep task statuses aligned to the official legend.
3. Keep backlog progress counts aligned with actual task statuses.
4. Keep I1-001 priority on the shared `Critical` scale.
5. Maintain `02-dependencies.md` as the full dependency and wave source of truth.
6. Keep dependency ranges explicit in `02-dependencies.md` and task headers.
7. Keep I1-002 and I1-012 separate under the approved responsibility split.
8. Keep I1-009 before app pilots as the Astra integration contract.
9. Define audit sink, retention, deletion, consent, and OpenAI personal-context allowlist for authenticated tools.
10. Replace missing validation file references with planned test names or create those tests as part of the relevant implementation task.
11. Centralize repeated browser matrix requirements in `04-validation-plan.md`.
12. Identify seeded authenticated test data requirements before browser/production verification.

---

# Optional Improvements

- Add a compact dependency graph table with `Task`, `Required Before`, `Can Run In Parallel`, and `Blocks`.
- Add a per-task scope-size field: `single assignment`, `split required`, or `defer`.
- Add a shared Assistant validation matrix for identity, safety, public discovery, authenticated context, tools, OpenAI grounded mode, and fallback.
- Add a privacy checklist specifically for personal-data tool outputs and memory.
- Add a short "existing system touchpoints" section to each task so Codex extends known modules instead of inventing new ones.

---

# Final Recommendation

Proceed to planning freeze only after required changes are made.

Recommended first implementation task after freeze:

**I1-009 — Astra AI Integration Contract**, followed by **I1-001**, **I1-002**, **I1-012**, and **I1-003**.

Do not begin I1-004 or I1-005 until the tool framework, context provider, audit policy, and validation fixtures are approved.
