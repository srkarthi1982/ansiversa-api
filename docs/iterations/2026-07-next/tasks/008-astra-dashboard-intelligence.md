# I1-008 — Astra Dashboard Intelligence

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Frozen
**Depends On:** I1-005 — Course Tracker Astra AI Integration
**Depends On:** I1-010 — Astra Conversation Context
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Transform the Dashboard from a collection of summary widgets into a source of actionable intelligence.

Instead of only displaying statistics, Astra should interpret dashboard information and guide the user toward the most valuable next action.

---

# Existing System Touchpoints

Extend the existing Dashboard, Assistant, Activity, Notifications, Favorites,
Recent Apps, Quiz, and Course Tracker integration points. Do not move
application business logic into the Dashboard or central Assistant.

---

# Typical Questions

A user should be able to ask:

* What should I focus on today?
* Is there anything important waiting for me?
* What needs my attention?
* Which app should I open first?
* What changed since yesterday?
* Give me today's summary.
* Am I falling behind anywhere?
* What's the most important thing right now?
* Show me today's highlights.
* Is there anything overdue?

---

# Data Sources

Initially:

* Notifications
* Activity Timeline
* Favorites
* Recent Apps
* Quiz Learning Intelligence
* Course Tracker Learning Intelligence

Future phases can extend this to:

* Bills
* Expenses
* Goals
* Documents
* Health
* etc.

---

# Recommendation Categories

The dashboard intelligence should classify items such as:

```text
ATTENTION_REQUIRED

CONTINUE_PROGRESS

NEAREST_COMPLETION

OVERDUE

UNREAD_NOTIFICATION

LEARNING_RECOMMENDATION

RECENT_ACTIVITY

NO_ACTION_REQUIRED
```

---

# Priority Rules

Instead of listing everything, Astra should rank items.

Example:

```text
1.
Unread notification requiring attention

2.
Course at 92%

3.
Weak Quiz topic

4.
Recently abandoned course

5.
Recent activity suggestion
```

---

# Example

Instead of the dashboard saying:

```text
Notifications: 3

Quiz Progress: 82%

Courses: 4
```

Astra says:

> Today you have three things worth your attention.

> • Finish Python Fundamentals (92%)
> • Review Leadership Quiz
> • You have 2 unread notifications

That's much more valuable than three numbers.

---

# Non-goals

Not yet:

* predictive AI
* automatic scheduling
* reminders
* autonomous actions
* external integrations

---

# Future

This task becomes the bridge between:

```text
Dashboard

↓

Assistant

↓

Daily Briefing

↓

Personal Intelligence
