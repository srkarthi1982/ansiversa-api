```md
# Faqs Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Support global + app-specific FAQs together

File:

app/modules/faqs/service.py

Function:

list_public_faqs()

Issue:

When appKey is provided, only app-specific FAQs are returned.

Global FAQs (appKey = null) are excluded.

Expected behavior:

When appKey is supplied, return:

- global FAQs (appKey = null)
- app-specific FAQs

Priority:

P2

---

## Task 2

Title:

Include answerMd in FAQ search

File:

app/modules/faqs/service.py

Function:

list_public_faqs()

Issue:

Search currently checks:

- question
- answer

answerMd is ignored.

Expected behavior:

Include:

Faq.answer_md.ilike(search)

Priority:

P3

---

## Task 3

Title:

Normalize audience values

File:

app/modules/faqs/service.py

Function:

list_public_faqs()

Issue:

Audience comparison is case-sensitive.

Expected behavior:

Normalize values to lowercase before filtering.
