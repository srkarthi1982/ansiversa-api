# 📁 API Review Backlog

**File**

```text
ansiversa-api/docs/api-review-backlog/admin.md
```

Contents:

```md
# Admin Module API Review Backlog

Status: ⏳ Pending

Date: 18-Jun-2026

Purpose:

These are API consistency improvements discovered during manual API verification.

This is NOT a blocker.

Do NOT work on these during Milestone Review #1.

Execute after Milestone Review #1 is fully completed.

---

## Task 1

Title:

Add 404 for missing category update

File:

app/modules/admin/categories_service.py

Function:

update_admin_category()

Issue:

The service retrieves:

existing = db.get(Category, category_id)

but does not stop when the category does not exist.

Expected behavior:

Return:

HTTP 404

detail:

"Category not found."

---

## Task 2

Title:

Add 404 for missing category delete

File:

app/modules/admin/categories_service.py

Function:

delete_admin_category()

Issue:

Deletion can continue even if the category does not exist.

Expected behavior:

Return:

HTTP 404

detail:

"Category not found."

before performing delete logic.

---

## Task 3

Title:

Add 404 for missing app delete

File:

app/modules/admin/apps_service.py

Function:

delete_admin_app()

Issue:

Deletion currently executes even when app_id does not exist.

Expected behavior:

Return:

HTTP 404

detail:

"App not found."

before delete execution.

---

## Task 4

Title:

Review FAQ response naming consistency

File:

app/modules/admin/schemas.py

Issue:

Mixed naming:

is_published

vs

isPublished

Review generated OpenAPI and frontend contracts.

Goal:

Use one naming convention consistently.

No behavioral changes required.

---
