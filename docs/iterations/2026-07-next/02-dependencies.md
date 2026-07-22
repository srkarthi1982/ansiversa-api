# Ansiversa Iteration 1

# Dependencies

This document records the frozen task sequencing for Iteration 1.

Its purpose is to ensure implementation starts only after prerequisite planning,
architecture boundaries, validation requirements, and governance decisions are
clear.

---

# Dependency Status

| Status | Meaning |
|----------|---------|
| Ready | Ready for implementation after Planning Freeze |
| Completed | Implemented and available as a prerequisite |
| Deferred | Documented but not planned for this implementation window |
| Blocked | Waiting on an unresolved dependency or governance decision |

---

# Dependency Principles

- Dependencies are implementation-order constraints, not architectural ownership changes.
- Applications continue to own their business logic, services, database access, and app-specific Astra tools.
- Astra owns orchestration, routing, tool execution flow, and final response assembly.
- User identity remains backend-owned.
- OpenAI cannot generate SQL, select users, override identity, or change deterministic facts.
- Phase 1 personal-data tools remain authenticated, owner-scoped, bounded, and read-only.
- Platform-wide validation requirements live in `04-validation-plan.md`.

---

# Task Dependency Table

| Task | Title | Status | Prerequisites | Blocks / Enables | Parallel Opportunity | Wave |
|------|-------|--------|---------------|------------------|----------------------|------|
| I1-001 | Astra AI User Data Awareness – Phase 1 | Completed | I1-009 | I1-002, I1-003, app pilots | No | Wave 1 |
| I1-002 | Astra AI Tool Framework | Completed | I1-001 | I1-012, I1-003, tool-enabled app pilots | No | Wave 1 |
| I1-003 | Platform User Context Provider | Completed | I1-001, I1-002, I1-012 | I1-004, I1-010, context-aware platform work | No | Wave 1 |
| I1-004 | Quiz Astra AI Integration | Completed | I1-001, I1-002, I1-003, I1-012 | I1-005, I1-006, first authenticated tool pilot | No | Wave 2 |
| I1-005 | Course Tracker Astra AI Integration | Completed | I1-004 | I1-006, I1-008 | Complete; enables later learning and dashboard intelligence | Wave 4 |
| I1-006 | Astra Learning Intelligence | Completed | I1-004, I1-005 | I1-008, later learning expansion | Complete; deterministic composition implemented without I1-013/I1-014 redesign | Wave 4 |
| I1-007 | Notifications Center UI Refinement | Ready | Existing Notifications Center Phase 1 | Notification UX polish | Yes, after freeze | Wave 2 |
| I1-008 | Astra Dashboard Intelligence | Ready | I1-005, I1-010, Activity, Notifications, Dashboard sources | I1-013, I1-014 input signals | Can run after I1-005 | Wave 4 |
| I1-009 | Astra AI Integration Contract | Completed | Planning Freeze approval | I1-001 and all Astra-enabled app contracts | First task | Wave 1 |
| I1-010 | Astra Conversation Context | Ready | I1-003, I1-004 | Follow-up behavior for later Astra tasks | Can run after I1-004 | Wave 2 |
| I1-011 | Astra Memory Management | Deferred | I1-010 plus consent, retention, deletion, and audit decisions | Later persistent memory governance | No | Later Iteration |
| I1-012 | Astra Tool Registry | Completed | I1-002 | I1-003, registered tool discovery | No | Wave 1 |
| I1-013 | Astra Intent Engine | Ready | I1-008, I1-012 | I1-014 and future orchestration extraction | Can start design review after I1-012 | Wave 4 |
| I1-014 | Astra Response Builder | Ready | I1-013 | Future response assembly consistency | No | Wave 4 |
| I1-015 | Astra Recommendation Engine | Deferred | I1-008, I1-013, I1-014 plus recommendation governance | Later deterministic recommendation ranking | No | Later Iteration |
| I1-016 | Global Search Enhancements | Ready | Existing Search module, I1-009 for Astra boundary | I1-017, I1-018 | Yes, after Wave 1 contract | Wave 3 |
| I1-017 | Command Palette Enhancements | Ready | I1-016 | I1-018 | No | Wave 3 |
| I1-018 | Universal Recent Items | Ready | I1-016, I1-017, existing Activity/Recent Apps review | I1-021 and platform personalization | No | Wave 3 |
| I1-019 | Accessibility Improvements | Ready | Existing shell and shared components | Quality baseline for browser verification | Yes, after freeze | Wave 2 |
| I1-020 | Mobile Experience Improvements | Ready | I1-019, I1-021 | Mobile platform polish | Can run after performance baseline | Wave 3 |
| I1-021 | Performance Improvements | Ready | Existing build/test baseline, I1-018 if recent-item queries change | Mobile and release readiness | Yes, measurement-first | Wave 3 |
| I1-022 | Platform Insights Dashboard | Deferred | Approved metrics sources, admin access model, privacy review | Later platform observation dashboard | No | Later Iteration |

---

# Simple Dependency Graph

```text
Wave 0
Planning Freeze
    ↓
I1-009 Astra AI Integration Contract
    ↓
I1-001 Astra AI User Data Awareness
    ↓
I1-002 Astra AI Tool Framework
    ↓
I1-012 Astra Tool Registry
    ↓
I1-003 Platform User Context Provider
    ↓
I1-004 Quiz Astra AI Integration
    ↓
I1-010 Astra Conversation Context

Independent Wave 2 quality track:
I1-007 Notifications Center UI Refinement
I1-019 Accessibility Improvements

Platform experience track:
I1-016 Global Search Enhancements
    ↓
I1-017 Command Palette Enhancements
    ↓
I1-018 Universal Recent Items
    ↓
I1-021 Performance Improvements
    ↓
I1-020 Mobile Experience Improvements

Wave 4 Astra refinement:
I1-005 Course Tracker Astra AI Integration
    ↓
I1-006 Astra Learning Intelligence
    ↓
I1-008 Astra Dashboard Intelligence
    ↓
I1-013 Astra Intent Engine
    ↓
I1-014 Astra Response Builder

Later Iteration:
I1-011 Astra Memory Management
I1-015 Astra Recommendation Engine
I1-022 Platform Insights Dashboard
```

---

# Implementation Waves

## Wave 0 — Planning Freeze

- Documentation corrections
- Governance alignment
- Architecture freeze
- Validation centralization

## Wave 1 — Astra Foundation

```text
I1-009  Astra AI Integration Contract
    ↓
I1-001  Astra AI User Data Awareness
    ↓
I1-002  Astra AI Tool Framework
    ↓
I1-012  Astra Tool Registry
    ↓
I1-003  Platform User Context Provider
```

## Wave 2 — First Pilot and Quality Baseline

```text
I1-004  Quiz Astra AI Integration
    ↓
I1-010  Astra Conversation Context
    ↓
I1-007  Notifications Center UI Refinement
    ↓
I1-019  Accessibility Improvements
```

I1-007 and I1-019 may run in parallel with Astra validation when staffing and
review capacity allow.

## Wave 3 — Platform Experience

```text
I1-016  Global Search Enhancements
    ↓
I1-017  Command Palette Enhancements
    ↓
I1-018  Universal Recent Items
    ↓
I1-021  Performance Improvements
    ↓
I1-020  Mobile Experience Improvements
```

## Wave 4 — Astra Refinement

```text
I1-005  Course Tracker Astra AI Integration
    ↓
I1-006  Astra Learning Intelligence
    ↓
I1-008  Astra Dashboard Intelligence
    ↓
I1-013  Astra Intent Engine
    ↓
I1-014  Astra Response Builder
```

## Later Iteration

These tasks remain documented but are not planned for the 2026-07-26 through
2026-08-09 implementation window:

```text
I1-011  Astra Memory Management
I1-015  Astra Recommendation Engine
I1-022  Platform Insights Dashboard
```

---

# I1-002 and I1-012 Responsibility Boundary

I1-002 and I1-012 remain separate tasks.

I1-002 owns:

- Tool execution
- Authentication
- Authorization
- Execution lifecycle
- Read-only enforcement
- Execution pipeline

I1-012 owns:

- Tool registration
- Tool discovery
- Metadata
- Versioning
- Enable/disable state

This preserves the Single Responsibility Principle while keeping both tasks in
Wave 1.

---

# External Dependencies

Current external services:

- OpenAI API
- Turso / libSQL
- Vercel

No new external providers should be introduced during this iteration unless
formally approved.

---

# Notes

Changes to dependency order after Planning Freeze require Partner/Astra review.

Runtime behavior must not change from this document alone.
