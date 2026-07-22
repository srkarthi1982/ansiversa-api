# I1-022 — Platform Insights Dashboard

**Iteration:** 2026-07-next
**Priority:** Low
**Status:** Deferred
**Depends On:** Approved metrics sources, admin access model, and privacy review
**Primary Repository:** `ansiversa`
**Supporting Repository:** `ansiversa-api`

---

# Objective

Create a unified Platform Insights Dashboard for administrators.

The dashboard should provide operational visibility into the overall health, usage, quality, and growth of the Ansiversa ecosystem.

The purpose is observation—not application management.

No application business logic should move into this dashboard.

---

# Vision

Provide one place where platform administrators can understand:

- platform health
- application adoption
- Astra AI usage
- feature engagement
- platform quality
- operational trends

without opening multiple systems.

---

# Engineering Principle

> Observe.

> Measure.

> Improve.

The dashboard reports platform metrics but never becomes the operational source of truth for individual applications.

---

# Initial Sections

## Platform Overview

Display:

- total applications
- live applications
- registered users
- active users
- platform version
- deployment status

---

## Application Health

Examples:

- application availability
- response status
- latest deployment
- version
- certification state

---

## Astra AI

Examples:

- conversations
- supported applications
- tool usage
- deterministic responses
- grounded responses
- fallback responses

Future metrics only where supported.

---

## Platform Usage

Examples:

- popular applications
- recent activity
- search usage
- command palette usage
- notification usage

---

## Quality

Display:

- Lighthouse summaries
- Accessibility
- SEO
- Best Practices
- Performance

Historical tracking may be added later.

---

## System

Examples:

- API health
- database status
- background jobs
- cache status

Only high-level operational visibility.

---

# Dashboard Design

The dashboard should remain:

- lightweight
- responsive
- informative
- uncluttered

Avoid becoming an administration console.

---

# Visualization

Simple visualizations are acceptable.

Examples:

- cards
- progress indicators
- trend charts
- status badges

Avoid excessive dashboards with unnecessary charts.

---

# Astra Integration

Future Astra questions may include:

- How many applications are live?
- Which apps are most used?
- How many Astra conversations happened today?
- Is the platform healthy?

Astra retrieves platform insights through approved platform services.

---

# Permissions

Only authorized administrators should access this dashboard.

Normal users must never see platform-wide administrative metrics.

---

# Accessibility

Verify:

- keyboard
- screen readers
- contrast
- responsive layout

---

# Mobile

Support:

- tablet
- mobile
- desktop

The dashboard should remain readable at all supported sizes.

---

# Performance

Requirements:

- efficient queries
- cached summaries where appropriate
- bounded payloads
- responsive rendering

---

# Documentation

Create:

```
docs/architecture/platform-insights-dashboard.md
```

Document:

- architecture
- supported metrics
- permissions
- data sources
- refresh strategy

Update:

- frontend AGENTS.md
- backend AGENTS.md
- iteration documentation

---

# Tests

Include:

- administrator access
- unauthorized access
- empty state
- data rendering
- responsive layout
- accessibility
- Astra integration
- performance

---

# Browser Verification

Use the shared platform browser matrix in `04-validation-plan.md`.

Verify Insights Dashboard-specific admin access, responsive summaries, filters,
empty states, and privacy-safe display.

---

# Acceptance Criteria

The task is complete when:

- Platform Insights Dashboard exists.
- Metrics are sourced from approved platform services.
- Administrative permissions are enforced.
- Responsive layout is verified.
- Documentation is updated.

---

# Success Criteria

Platform administrators gain a single, reliable overview of the Ansiversa ecosystem without replacing application-specific dashboards.

---

# Future Scope

Not included:

- business intelligence
- predictive analytics
- AI forecasting
- automatic optimization
- infrastructure management
- external monitoring platforms

---

# Delivery

Report:

- dashboard architecture
- metrics implemented
- permissions
- browser verification
- accessibility
- performance
- documentation
- repository status

Confirm explicitly:

- Platform Insights remains an observation dashboard.
- Application ownership is preserved.
- Administrative permissions are enforced.
- Existing applications remain unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories remain clean and aligned with `origin/main`.
