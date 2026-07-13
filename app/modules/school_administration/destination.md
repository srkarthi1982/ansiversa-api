# School Administration Destination

## Document Status

Approved for Live promotion on 2026-07-13 after Astra review, Partner approval, production migration verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

School Administration should mature into a calm, private administration workspace for smaller education operators that need dependable records before they need a full enterprise SIS.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Product Identity

School Administration is for:

- Small private schools.
- Tutors and learning centres.
- Training centres.
- Early-stage institutions.
- Administrators who need practical records without SIS complexity.

It is not positioned as a replacement for a complete SIS, LMS, payment gateway, admissions platform, government reporting tool, biometric attendance platform, or parent communication suite.

## Mature Workflow

The mature product may expand from:

```text
Students
→ Classes
→ Attendance
→ Insights
```

Toward:

```text
Students
→ Classes
→ Enrolments
→ Attendance
→ Fees
→ Timetables
→ Exams
→ Documents
→ Communications
→ Insights
```

Only approved future scope should be implemented.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 establishes the core record foundation across Students, Classes, Attendance, and Insights while intentionally deferring larger SIS capabilities such as admissions, grading, parent portals, LMS, payments, biometrics, government integrations, imports, attachments, and staff roles.

## Destination Capabilities

Potential future capabilities:

- Fees and invoice tracking.
- Teacher management.
- Timetables.
- Exams and grades.
- Parent/student portals.
- Document attachments.
- ID card generation.
- Notifications.
- Admissions workflow.
- Multi-campus support.
- CSV import/export.
- Audit trail.
- Role-based staff access.

## Current V1 Boundary

V1 includes:

- Student CRUD.
- Class CRUD.
- Explicit enrolment assignment/removal.
- Attendance CRUD.
- Operational insights.

V1 excludes:

- Government or ministry integration.
- Online admission processing.
- Fee collection and payment processing.
- Live parent/student portal.
- Biometric attendance.
- Academic grading and LMS functionality.

## Governance Notes

Astra: Approved on 2026-07-13.

Partner: Approved School Administration live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/foreign keys, synced overview metadata, and prepared live promotion metadata.
