# Exam Module API Review Backlog

Status: 🟡 Pending

Date: 18-Jun-2026

Purpose:

Manual API verification completed.

Minor consistency improvements discovered.

No blocker issues found.

---

## Task 1

Title:

Prevent multiple active attempts for the same paper

File:

app/modules/exam/service.py

Function:

start_attempt()

Issue:

Users can create unlimited active attempts for the same paper.

Expected behavior:

If an active attempt already exists, return it or block creation.

Priority:

P2

---

## Task 2

Title:

Expire attempts during submit flow

File:

app/modules/exam/service.py

Function:

submit_attempt()

Issue:

Expired attempts are checked in save_answers() but not in submit_attempt().

Expected behavior:

Apply the same expiration validation before submission.

Priority:

P2

---

## Task 3

Title:

Add unique constraint for ExamAnswer

File:

app/modules/exam/models.py

Table:

ExamAnswers

Issue:

(attemptId, questionId) uniqueness is enforced only in application code.

Expected behavior:

Add a database unique constraint.

Priority:

P2

---

## Task 4

Title:

Optimize review response calculations

File:

app/modules/exam/service.py

Function:

_review_response()

Issue:

wrong_answers and unanswered repeatedly iterate over questions.

Expected behavior:

Calculate counters in a single loop.