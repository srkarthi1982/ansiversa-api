# I1-015 — Astra Recommendation Engine

**Iteration:** 2026-07-next
**Priority:** High
**Status:** Deferred
**Depends On:** I1-008 — Astra Dashboard Intelligence
**Depends On:** I1-013 — Astra Intent Engine
**Depends On:** I1-014 — Astra Response Builder
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Implement the Astra Recommendation Engine.

The Recommendation Engine becomes responsible for selecting the most valuable recommendation for the authenticated user using deterministic platform rules.

It ranks recommendations produced by applications but never replaces application business logic.

---

# Existing System Touchpoints

Future implementation should extend app-owned recommendations, Dashboard
signals, Activity, Notifications, the Intent Engine, and the Response Builder.
Do not centralize app-specific recommendation rules inside Astra.

---

# Vision

Applications produce recommendations.

The Recommendation Engine prioritizes them.

Example:

Quiz

- Revise Leadership

Course Tracker

- Finish Python Fundamentals (92%)

Notifications

- Two unread important notifications

Dashboard

- Continue recently used app

↓

Recommendation Engine

↓

Priority:

1. Finish Python Fundamentals
2. Review Leadership Quiz
3. Read Notifications

---

# Core Principle

> Applications recommend.

> Astra prioritizes.

Business rules remain inside the application.

Astra only compares approved recommendations.

---

# Responsibilities

The Recommendation Engine should:

- collect recommendations
- rank them
- resolve conflicts
- remove duplicates
- explain priorities
- produce one primary recommendation
- optionally produce secondary recommendations

---

# Recommendation Sources

Examples:

- Quiz
- Course Tracker
- Notifications
- Dashboard
- Future applications

Every recommendation must include metadata describing:

- source application
- recommendation type
- priority
- confidence
- supporting facts
- canonical action

---

# Recommendation Categories

Examples:

- COMPLETE_NEAREST_TASK
- CONTINUE_PROGRESS
- REVIEW_WEAK_TOPIC
- RESUME_ACTIVITY
- UNREAD_NOTIFICATION
- OVERDUE_ITEM
- FAVORITE_APP
- RECENT_ACTIVITY
- INFORMATION_ONLY

Applications may define additional categories.

---

# Priority Rules

Suggested order:

1. Critical overdue work
2. Nearest completion
3. Important notifications
4. Resume active work
5. Continue learning
6. Recently used apps
7. Informational suggestions

The exact order should be governed and documented.

---

# Conflict Resolution

Example:

Quiz recommends:

- Leadership Review

Course Tracker recommends:

- Python Fundamentals

The Recommendation Engine should apply deterministic priority rules.

Never rely on OpenAI to choose between recommendations.

---

# Duplicate Removal

Example:

Dashboard

↓

Continue Course Tracker

Course Tracker

↓

Continue Python Fundamentals

Only one recommendation should remain if they refer to the same underlying action.

---

# Recommendation Contract

Suggested structure:

```text
Recommendation
 ├── Source
 ├── Type
 ├── Priority
 ├── Confidence
 ├── Explanation
 ├── Supporting Facts
 ├── Canonical Action
```

Implementation may differ.

---

# Explainability

Every recommendation must answer:

- Why?
- Which application produced it?
- What facts support it?

Example:

> Continue Python Fundamentals because it is already 92% complete.

---

# Confidence

Support:

- High
- Medium
- Low
- Insufficient

Confidence should come from deterministic rules.

---

# OpenAI

OpenAI may improve wording.

OpenAI must never:

- change ranking
- invent recommendations
- remove recommendations
- modify supporting facts

---

# Performance

Requirements:

- lightweight
- deterministic
- bounded
- cache friendly
- stable ordering

---

# Tests

Include tests for:

- ranking
- duplicates
- conflicts
- priority
- confidence
- explanation
- no recommendations
- partial recommendations

---

# Browser Verification

Verify:

- primary recommendation
- secondary recommendations
- explanation
- canonical action
- mobile layout
- desktop layout

---

# Documentation

Create:

```
docs/architecture/astra-recommendation-engine.md
```

Document:

- ranking rules
- recommendation contract
- duplicate handling
- conflict resolution
- confidence
- explainability

Update:

- backend AGENTS
- Assistant documentation
- architecture documentation
- iteration documentation

---

# Acceptance Criteria

The task is complete when:

- Recommendation Engine exists.
- Ranking is deterministic.
- Duplicate recommendations are removed.
- Conflict resolution is documented.
- OpenAI cannot alter recommendation order.
- Tests pass.

---

# Success Criteria

Regardless of how many applications participate, Astra consistently presents one clear, explainable recommendation to the user.

---

# Future Scope

Not included:

- machine learning ranking
- user-behavior prediction
- adaptive recommendation models
- autonomous planning
- proactive scheduling

---

# Delivery

Report:

- architecture
- ranking rules
- conflict resolution
- duplicate handling
- confidence model
- tests
- documentation
- repository status

Confirm explicitly:

- Applications remain the source of recommendations.
- Astra ranks but does not invent recommendations.
- OpenAI cannot change recommendation order.
- Existing application business logic remains unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
