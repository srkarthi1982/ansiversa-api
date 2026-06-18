# Contact Module API Review Backlog

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

app/modules/contact/service.py

Function:

create_contact_message()

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

Use Pydantic EmailStr validation

File:

app/modules/contact/schemas.py

Issue:

Custom email validation logic is implemented manually.

Expected behavior:

Replace with:

EmailStr

and keep normalization.