# I1-018 — Universal Recent Items

**Iteration:** 2026-07-next
**Priority:** Medium
**Status:** Frozen
**Depends On:** I1-016 — Global Search Enhancements
**Depends On:** I1-017 — Command Palette Enhancements
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Implement a platform-wide Recent Items service.

Recent Items should become the single source of truth for recently accessed applications, pages, records, and future Astra interactions.

Rather than every application implementing its own "Recent" feature, the platform should provide one consistent experience.

---

# Vision

Users should be able to continue where they left off regardless of which application they previously used.

Examples:

- Recently opened applications
- Recently viewed pages
- Recently opened records
- Recently viewed reports
- Recently used tools
- Future Astra conversations

---

# Core Principle

> Record once.

> Reuse everywhere.

Every application reports recent activity to one shared Recent Items service.

Applications never implement separate "recent" logic.

---

# Current Consumers

The shared Recent Items service should support:

- Dashboard
- Command Palette
- Global Search
- Astra AI
- Future Home widgets

All consumers use the same data source.

---

# Recent Item Types

Examples:

Applications

- Quiz
- Course Tracker
- Leave Planner

Pages

- Dashboard
- Settings
- Notifications

Records

- Quiz Attempt
- Course
- Expense
- Goal

Future

- Astra conversations
- Reports
- Saved searches

---

# Data Model

Each recent item should contain:

- owner
- application
- item type
- title
- subtitle
- canonical route
- icon
- timestamp
- metadata (optional)

Implementation may differ.

---

# Recording Rules

A recent item should be created when:

- a user opens an application
- a user opens a record
- a user views a supported page

Avoid recording:

- login
- logout
- loading pages
- background requests
- health checks
- repeated refreshes

---

# Deduplication

Opening the same item repeatedly should update its timestamp rather than creating duplicates.

Example:

```
Quiz

↓

Quiz

↓

Quiz
```

Result:

One recent entry with the latest timestamp.

---

# Ordering

Recent Items should be ordered by:

Most recently accessed first.

Ordering remains deterministic.

---

# Retention

Support a bounded history.

Suggested defaults:

- recent applications
- recent pages
- recent records

Old entries may be removed according to platform policy.

---

# Privacy

Recent Items belong only to the authenticated user.

Users must never see another user's history.

---

# Dashboard Integration

Dashboard may display:

- Continue where you left off
- Recently used apps
- Recent activity

using this shared service.

---

# Command Palette Integration

Display:

- recent applications
- recent records
- recent pages

before general search results where appropriate.

---

# Global Search Integration

Recent Items may be surfaced when:

- search is empty
- search has limited results

Do not replace search ranking.

---

# Astra Integration

Future Astra questions may include:

- Continue where I stopped.
- Open the last course I viewed.
- Show my recent activity.
- Open my most recent Quiz.

Astra retrieves these through the shared Recent Items service.

---

# Accessibility

Verify:

- keyboard
- screen readers
- focus order
- touch targets
- mobile scrolling

---

# Mobile

Requirements:

- responsive layout
- compact presentation
- smooth scrolling
- safe-area support

---

# Performance

Requirements:

- lightweight writes
- bounded history
- deterministic ordering
- indexed lookups
- minimal storage overhead

---

# Tests

Include:

- create recent item
- deduplication
- ordering
- retention
- owner isolation
- Dashboard integration
- Command Palette integration
- Global Search integration
- Astra integration
- mobile

---

# Browser Verification

Use the shared platform browser matrix in `04-validation-plan.md`.

Verify Recent Items-specific recording, ordering, deduplication, empty states,
and cross-surface behavior.

---

# Documentation

Create:

```
docs/architecture/recent-items.md
```

Document:

- architecture
- retention
- ordering
- deduplication
- ownership
- integrations

Update:

- backend AGENTS.md
- frontend AGENTS.md
- Dashboard story
- Command Palette story
- iteration documentation

---

# Acceptance Criteria

The task is complete when:

- Shared Recent Items service exists.
- Applications no longer duplicate recent-item logic.
- Dashboard, Search, Command Palette, and Astra consume the shared service.
- Deduplication works.
- Ordering is deterministic.
- Privacy is preserved.
- Browser verification passes.

---

# Success Criteria

Users always have a consistent "Continue where you left off" experience across the entire Ansiversa platform.

Recent Items become reusable infrastructure rather than an application-specific feature.

---

# Future Scope

Not included:

- pinned history
- shared history
- organization history
- AI-generated activity summaries
- cross-user recommendations

---

# Delivery

Report:

- architecture
- data model
- deduplication rules
- retention rules
- Dashboard integration
- Command Palette integration
- Astra integration
- browser verification
- documentation updates
- repository status

Confirm explicitly:

- Recent Items remain owner-scoped.
- Applications reuse the shared service.
- Dashboard, Search, Command Palette, and Astra consume the same source.
- Existing navigation remains unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
