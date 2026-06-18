# Language Flashcards Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Prevent multiple active study sessions for the same deck

File:

app/modules/language_flashcards/service.py

Function:

start_session()

Issue:

Users can create unlimited active sessions for the same deck.

Expected behavior:

If an active session already exists, return it or block creation.

Priority:

P2

---

## Task 2

Title:

Add unique constraint for ReviewLog

File:

app/modules/language_flashcards/models.py

Table:

ReviewLogs

Issue:

(sessionId, cardId) uniqueness is enforced only in application code.

Expected behavior:

Add a database unique constraint.

Priority:

P2

---

## Task 3

Title:

Validate review count against session total

File:

app/modules/language_flashcards/service.py

Function:

submit_review()

Issue:

Validation relies on current deck cards instead of session.total_cards.

Expected behavior:

Also validate against session.total_cards.