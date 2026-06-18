```md
# Dashboard Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Protect DashboardAppResponse from nullable app relationship

File:

app/modules/dashboard/routes.py

Function:

_serialize_dashboard_item()

Issue:

Dashboard.app is assumed to always exist.

If an App record is deleted independently, Dashboard serialization can fail.

Expected behavior:

Skip orphaned dashboard records or return a safe fallback.

Priority:

P2

---

## Task 2

Title:

Remove duplicated dashboard app serialization

File:

app/modules/dashboard/routes.py

Issue:

recent_apps are built from already serialized dashboard_items.

Expected behavior:

Avoid double transformation.

Serialize directly from Dashboard objects.

Priority:

P3

---

## Task 3

Title:

Add database index for unread notifications query

File:

app/modules/notifications/models.py

Issue:

Dashboard frequently executes:

(user_id, is_read)

lookup.

Expected behavior:

Ensure a composite index exists.

```
