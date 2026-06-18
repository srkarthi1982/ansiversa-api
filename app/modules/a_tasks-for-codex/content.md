```md
# Content Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Replace broad exception handling

File:

app/modules/content/service.py

Function:

upsert_metadata()

Issue:

Uses:

except Exception:

Expected behavior:

Catch specific SQLAlchemy exceptions only.

Priority:

P3

---

## Task 2

Title:

Protect metadata write/delete endpoints with admin authorization

File:

app/modules/content/routes.py

Issue:

PUT and DELETE currently require authenticated users only.

Expected behavior:

Replace:

get_current_user

with:

require_admin_user

Priority:

P2

---

## Task 3

Title:

Centralize repeated 404 metadata handling

File:

app/modules/content/routes.py

Issue:

Repeated code exists in:

- get_home_metadata()
- get_about_metadata()
- get_terms_metadata()
- get_privacy_metadata()
- get_pricing_metadata()
- get_overview_metadata()

Expected behavior:

Move metadata-not-found logic into a shared helper.

Priority:

P3

---

## Task 4

Title:

Standardize code formatting

File:

app/modules/content/service.py

Issue:

Function bodies use 2-space indentation.

Expected behavior:

Use repository standard 4-space indentation.