Next, create:

```text
docs/iterations/2026-07-next/tasks/007-notifications-center-ui-refinement.md
```

Use this content:

````markdown
# I1-007 — Notifications Center UI Refinement

**Iteration:** 2026-07-next  
**Priority:** High  
**Status:** Discussing  
**Primary Repository:** `ansiversa`  
**Supporting Repository:** `ansiversa-api` only if a verified API defect or missing presentation field is discovered  
**Depends On:** Existing Notifications Center Phase 1

---

# Objective

Refine the Notifications Center into a lighter, more compact, and easier-to-scan experience while preserving the existing notification architecture and backend behavior.

The current Notifications Center works correctly, but each notification is presented as a visually heavy card.

The refined experience should use:

- thin and smooth notification rows
- subtle separators
- compact spacing
- a right-aligned read/check action
- clearer unread emphasis
- better information density
- consistent desktop and mobile behavior

This is a presentation and interaction refinement—not a notification-system redesign.

---

# Current State

The existing implementation already provides:

- authenticated global notification bell
- unread badge
- responsive notification drawer
- owner-scoped pagination
- unread and type filtering
- mark-one-as-read
- mark-all-as-read
- loading state
- empty state
- error state
- safe internal navigation
- notification preferences
- production database support

These capabilities must remain intact.

---

# Problem Statement

The current notification layout feels visually dense because:

- every notification uses a large bordered card
- borders and padding create excessive visual weight
- the “Mark as read” action consumes too much space
- scanning many notifications requires unnecessary scrolling
- read and unread notifications do not feel sufficiently distinct
- action controls compete visually with notification content

The drawer should feel like a modern notification inbox rather than a list of large forms or dashboard cards.

---

# Design Direction

Preferred visual model:

```text
[Icon]  Notification title                         [✓]
        Short message or supporting detail
        Source · Relative time
──────────────────────────────────────────────────────
```

The exact design should follow existing Ansiversa shared UI contracts.

---

# Core Design Principles

## 1. Compact

Show more useful notifications within the visible drawer area.

## 2. Lightweight

Prefer subtle surfaces and dividers over heavy bordered cards.

## 3. Scannable

The title, source, time, unread status, and action must be understandable immediately.

## 4. Accessible

Read state must not depend only on color.

## 5. Consistent

Desktop and mobile should share the same notification-row component and behavior.

---

# Scope

This task includes:

- compact notification row
- softer border/separator treatment
- right-aligned read action
- clearer unread state
- read-state styling
- source and time hierarchy
- click-target refinement
- mobile responsiveness
- keyboard behavior
- focus behavior
- loading skeleton refinement
- empty and error state review
- pagination presentation review
- filter presentation review
- shared component extraction where appropriate
- Playwright regression coverage
- documentation updates

---

# Non-Goals

Do not add:

- push notifications
- email notifications
- SMS
- scheduled notification generation
- notification grouping by AI
- notification deletion
- notification snoozing
- notification search
- infinite scrolling unless separately approved
- production test records
- new database tables
- App #101

Do not redesign the entire shell or header.

---

# Notification Row Contract

Introduce or refine a shared row component such as:

```text
AvNotificationRow
```

The exact name should follow repository conventions.

Suggested inputs:

```ts
type NotificationRowProps = {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  sourceApp?: string | null;
  createdAt: string;
  isRead: boolean;
  action?: {
    label: string;
    route: string;
  } | null;
  onMarkRead: () => void;
  onNavigate?: () => void;
};
```

Do not duplicate notification rendering between desktop and mobile.

---

# Visual Hierarchy

## Unread Notification

Unread notifications should have stronger emphasis through a combination of:

- semibold title
- subtle surface/background distinction
- unread indicator
- enabled read/check action
- accessible unread label

Do not rely on color alone.

## Read Notification

Read notifications should appear visually calmer:

- normal title weight
- no unread indicator
- read action disabled, hidden, or replaced with a completed state
- content remains readable

Do not reduce opacity so much that accessibility suffers.

---

# Read Action

Replace large text-heavy “Mark as read” controls with a compact right-side control.

Preferred direction:

```text
✓
```

Requirements:

- accessible label: `Mark notification as read`
- tooltip where appropriate
- minimum touch target
- keyboard accessible
- visible focus state
- loading/disabled state while request is running
- prevents duplicate requests
- does not trigger notification navigation accidentally

Once read:

- show completed state where useful
- or remove the action cleanly
- do not leave a confusing disabled button without context

---

# Navigation Behavior

Where a notification contains a valid action:

- clicking the content area may navigate to the validated target
- the read/check action must remain independent
- navigation should close the mobile drawer where appropriate
- existing safe-route validation remains authoritative
- invalid or stale actions remain omitted

Decide explicitly whether navigation also marks the notification as read.

If existing behavior already defines this, preserve it.

Do not silently introduce a new business rule.

---

# Notification Content

Display only approved fields:

- title
- short message
- source app or source type
- created time
- unread/read state
- validated action

Do not expose:

- raw metadata JSON
- database IDs
- internal routes
- invalid source slugs
- debug information

---

# Time Presentation

Preferred display:

```text
2 minutes ago
Yesterday
Jul 20
```

The exact timestamp may be available through:

- accessible label
- tooltip
- expanded detail where appropriate

Requirements:

- timezone-safe
- stable during hydration
- no misleading future timestamps
- deterministic tests should not become flaky

If relative-time updates add unnecessary complexity, retain a clear formatted date and time.

---

# Filters

Review the existing filters for:

- unread
- notification type
- all notifications

Requirements:

- compact layout
- clear active state
- mobile usability
- keyboard accessibility
- no excessive vertical space
- filter changes reset pagination appropriately
- filter behavior remains backend-driven

Do not introduce unsupported notification types.

---

# Header

The drawer header should retain:

- title
- unread summary
- mark-all-read action
- close control

Refine spacing and hierarchy.

Suggested layout:

```text
Notifications                    [Mark all read] [×]
3 unread
```

On mobile, actions may wrap or use icon controls if accessible.

---

# Mark All as Read

Preserve current backend behavior.

Requirements:

- disabled when unread count is zero
- clear loading state
- prevents duplicate submissions
- updates list and badge consistently
- error restores usable state
- accessible label
- no optimistic state corruption

---

# Pagination

Preserve owner-scoped backend pagination.

Review whether the current pagination UI fits the drawer.

Requirements:

- compact
- understandable
- keyboard accessible
- no horizontal overflow
- current page clearly identified
- filters and pagination remain synchronized

Do not switch to infinite scrolling without separate approval.

---

# Loading State

Replace large card-shaped loading placeholders with compact row skeletons matching the final design.

Requirements:

- stable drawer dimensions
- no layout jump
- no excessive animation
- respects reduced-motion settings
- mobile-safe

---

# Empty States

Support distinct empty states where possible:

## No Notifications

> You do not have any notifications yet.

## No Unread Notifications

> You’re all caught up.

## No Filter Results

> No notifications match the selected filter.

Keep actions minimal and relevant.

---

# Error State

Preserve Retry behavior.

Requirements:

- concise message
- retry button
- drawer remains closable
- no raw API error
- no stack trace
- retry does not duplicate requests

---

# Responsive Behavior

Verify at:

- desktop
- tablet
- mobile

Requirements:

- drawer width remains appropriate
- row content wraps cleanly
- title and action do not overlap
- right-side check remains reachable
- no horizontal scrolling
- touch targets remain large enough
- safe-area spacing preserved
- drawer closes correctly after navigation

---

# Accessibility

Verify:

- semantic notification list
- each notification has understandable accessible text
- unread state is announced
- read action has an accessible label
- focus order is logical
- drawer traps/restores focus correctly
- Escape closes the drawer
- screen-reader users can identify notification title, status, and time
- color is not the only indicator
- minimum contrast requirements
- reduced motion respected

---

# Performance

This refinement must not introduce:

- new initial API requests
- polling
- large dependencies
- app implementation imports
- significant bundle increase
- unnecessary rerenders
- duplicated notification state

Measure and report bundle impact.

---

# Backend Boundary

No backend change is expected.

A backend change may occur only if investigation proves that the frontend lacks a necessary, safe presentation field.

Do not change:

- notification persistence
- owner-scoping
- pagination contract
- unread logic
- action validation
- preference model
- publisher service

Any backend change must be narrow and separately documented.

---

# Tests

Add or update Playwright tests covering:

1. drawer opens
2. compact rows render
3. unread notification styling
4. read notification styling
5. mark-one-read control
6. mark-one-read loading state
7. mark-all-read
8. zero-unread state
9. notification navigation
10. invalid action omitted
11. filter behavior
12. pagination behavior
13. empty state
14. filtered empty state
15. error and Retry
16. keyboard navigation
17. focus restoration
18. mobile layout
19. mobile item selection closes drawer
20. no horizontal overflow

Run across:

- Chromium
- Chrome
- Tablet
- Mobile

---

# Manual Verification

Use the live system to verify:

- multiple unread notifications
- mixture of read and unread notifications
- long title
- long message
- missing source app
- notification with action
- notification without action
- mark-one-read
- mark-all-read
- filters
- pagination
- mobile drawer
- badge synchronization

---

# Documentation

Update:

- frontend `AGENTS.md`
- frontend `src/story.md`
- Notifications story
- shared UI documentation if a reusable row component is introduced
- iteration backlog
- validation plan
- release checklist where applicable

Document the UI rule:

> Notifications use compact, accessible rows with subtle separation. Large card-style notification blocks are not the default presentation.

---

# Acceptance Criteria

The task is complete when:

- notification rows are compact and lightweight
- unread and read states are clearly distinguishable
- read action appears on the right
- action remains accessible
- notification navigation remains safe
- filters and pagination continue working
- mark-all-read remains reliable
- loading, empty, and error states match the refined layout
- mobile and desktop share the same component contract
- no backend regression exists
- bundle impact is acceptable
- Playwright and manual verification pass
- documentation is updated

---

# Success Criteria

A user should be able to open Notifications and quickly understand:

- what is unread
- what requires attention
- where the notification came from
- when it happened
- where it leads
- how to mark it as read

The drawer should feel light, modern, and easy to scan even with many notifications.

---

# Delivery

After implementation, report:

- commit hash
- component architecture
- before/after screenshots
- unread/read visual treatment
- read-action behavior
- navigation behavior
- filter and pagination behavior
- desktop/tablet/mobile results
- accessibility verification
- bundle impact
- Playwright results
- documentation updates
- backend impact
- repository status

Confirm explicitly:

- Existing Notifications APIs remain authoritative.
- No notification data model was duplicated.
- No push, email, SMS, scheduler, or deletion feature was added.
- Safe route validation remains unchanged.
- Owner-scoped behavior remains unchanged.
- No App #101 was introduced.
- All changed repositories are clean and aligned with `origin/main`.
````

Update `01-priority-backlog.md`:

```text
I1-007 | Notifications Center UI Refinement | High | Discussing
```

This task directly captures the visual issue you observed earlier: the functionality is correct, but the cards should become thinner, smoother, and easier to scan.
