```md id="pr27sj"
# Auth Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Prevent setting the same password during password change

File:

app/modules/auth/service.py

Function:

change_password()

Issue:

Users can set their new password to the same value as the current password.

Expected behavior:

Return:

HTTP 400

detail:

"New password must be different from the current password."

Priority:

P3

---

## Task 2

Title:

Prevent setting the same password during password reset

File:

app/modules/auth/service.py

Function:

reset_password()

Issue:

Users can reset their password to the same existing password.

Expected behavior:

Return:

HTTP 400

detail:

"New password must be different from the current password."

Priority:

P3

---

## Task 3

Title:

Replace hardcoded ADMIN_ROLE_ID

File:

app/modules/auth/dependencies.py

Issue:

ADMIN_ROLE_ID = 1 is hardcoded.

Expected behavior:

Move this value to a shared constant/configuration location.

Priority:

P3

---

## Execution Rule

Do NOT execute now.

Execute after current milestone work is completed.
```
