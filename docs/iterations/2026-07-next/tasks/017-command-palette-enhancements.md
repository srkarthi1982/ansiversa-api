# I1-017 — Command Palette Enhancements

**Iteration:** 2026-07-next
**Priority:** Medium
**Status:** Frozen
**Depends On:** I1-016 — Global Search Enhancements
**Primary Repository:** `ansiversa`
**Supporting Repository:** `ansiversa-api` only if additional search metadata is required

---

# Objective

Enhance the existing Command Palette into the fastest navigation experience within Ansiversa.

The Command Palette should become the primary keyboard-driven navigation surface while remaining fully usable on desktop, tablet, and mobile.

It should integrate naturally with Astra AI without duplicating search logic.

---

# Vision

Users should be able to press:

```
Ctrl + K
```

or

```
⌘ + K
```

and immediately:

- open applications
- navigate to pages
- find settings
- view recent items
- launch favorite apps
- continue recent work
- ask Astra AI

The Command Palette should become the fastest way to move around Ansiversa.

---

# Current Capabilities

Existing implementation already supports:

- keyboard shortcut
- grouped results
- applications
- platform pages
- responsive UI
- navigation

This task extends those capabilities.

---

# Enhancement Areas

## Search Integration

Reuse Global Search.

Do not implement separate search logic.

The Command Palette should consume the shared search service.

---

## Recent Items

Display:

- recently opened apps
- recent pages
- recent Astra conversations (future)
- recent searches

Recent items remain owner-scoped.

---

## Favorites

Show:

- favorite applications
- favorite pages

Pinned favorites should appear before standard search results when appropriate.

---

## Context Awareness

The Command Palette should understand the current application.

Examples:

Inside Quiz:

```
Open Results

Start Quiz

Quiz Settings
```

Inside Course Tracker:

```
Open Active Courses

Completed Courses

Learning Summary
```

---

## Astra Integration

Allow users to transition naturally into Astra.

Examples:

```
Ask Astra:
How many Quiz platforms have I completed?
```

or

```
Search Results

↓

Ask Astra instead
```

The Command Palette should not implement Assistant logic.

It only launches Astra where appropriate.

---

## Keyboard Navigation

Support:

- Arrow Up
- Arrow Down
- Enter
- Escape
- Tab where appropriate

Navigation should remain predictable.

---

## Ranking

Suggested order:

1. Exact match
2. Favorites
3. Recent items
4. Search results
5. Suggested actions

Ranking remains deterministic.

---

## Empty State

Example:

> No matching results.

Offer:

- Browse Apps
- Ask Astra AI

---

## Mobile

Provide an equivalent touch experience.

Requirements:

- full-screen palette
- large touch targets
- responsive scrolling
- safe-area support

---

## Accessibility

Verify:

- keyboard
- screen readers
- focus trap
- contrast
- reduced motion
- accessible labels

---

## Performance

Requirements:

- instant opening
- lightweight rendering
- no unnecessary backend requests
- cached search index
- bounded rendering

---

# Future Scope

Future enhancements may include:

- quick actions
- pinned commands
- developer commands
- plugin commands

These are outside this iteration.

---

# Tests

Include:

- keyboard navigation
- search integration
- favorites
- recent items
- context-aware entries
- Astra launch
- empty state
- accessibility
- mobile
- performance

---

# Browser Verification

Use the shared platform browser matrix in `04-validation-plan.md`.

Verify Command Palette-specific keyboard behavior, ranking, responsive layout,
and navigation actions.

---

# Documentation

Update:

- frontend AGENTS.md
- Command Palette story
- shared search documentation
- iteration documentation

---

# Acceptance Criteria

The task is complete when:

- Command Palette uses shared search.
- Favorites are supported.
- Recent items appear correctly.
- Context-aware suggestions work.
- Astra launch integration exists.
- Accessibility passes.
- Browser verification passes.

---

# Success Criteria

Users can navigate almost the entire Ansiversa platform without leaving the Command Palette.

---

# Delivery

Report:

- search integration
- favorites
- recent items
- context awareness
- Astra integration
- accessibility
- performance
- browser verification
- documentation updates
- repository status

Confirm explicitly:

- Shared search remains the single source of truth.
- No duplicate search implementation was introduced.
- Astra launch remains optional.
- Existing keyboard shortcuts remain unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
