# I1-008 — Astra Dashboard Intelligence

### Objective

Transform the Dashboard from a collection of summary widgets into a source of actionable intelligence.

Instead of only displaying statistics, Astra should interpret dashboard information and guide the user toward the most valuable next action.

---

### Typical Questions

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

### Data Sources

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

### Recommendation Categories

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

### Priority Rules

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

### Example

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

### Non-goals

Not yet:

* predictive AI
* automatic scheduling
* reminders
* autonomous actions
* external integrations

---

### Future

This task becomes the bridge between:

```text
Dashboard

↓

Assistant

↓

Daily Briefing

↓

Personal Intelligence
```

---

Update the backlog:

```text
I1-008 | Astra Dashboard Intelligence | High | Discussing
```

---

## I also want to propose one new engineering rule

I think we've naturally discovered another governance principle for Ansiversa:

> **Every new feature should answer two questions:**
>
> 1. **How does the user use this feature directly?**
> 2. **How will Astra help the user with this feature?**

That doesn't mean every feature needs Astra integration immediately. It means every feature should be designed with an extension point for Astra from the beginning. Just like you've been doing with `market-study.md`, `destination.md`, and `story.md`, this mindset will prevent future rework and keep Astra evolving alongside the platform rather than chasing it afterward. I think that philosophy fits perfectly with the engineering discipline you've built around Ansiversa.
