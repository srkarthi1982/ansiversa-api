# School Administration Story

## Purpose

School Administration is App #070 in Ansiversa. It provides a private school-record management workspace for organizing students, classes, enrolments, attendance, and operational summaries.

V1 is intentionally not a complete student information system, learning management system, payment platform, admissions platform, government reporting system, biometric attendance tool, grading system, or parent/student portal.

## Workflow

The protected workflow is:

```text
Overview
→ Students
→ Classes
→ Attendance
→ Insights
```

The overview Explore CTA enters `/school-administration/students`.

## User Journey

A signed-in user creates student records with admission numbers, guardian contacts, admission status, emergency contact details, and support notes. They create classes by academic year, teacher, room, capacity, and status. Students are assigned to classes through explicit enrolment records. Attendance is recorded per class, student, and date. Insights summarize only stored records.

## Database Design

The module owns an isolated database configured by `SCHOOL_ADMINISTRATION_DATABASE_URL`.

Tables:

- `SchoolStudents`
- `SchoolClasses`
- `SchoolEnrollments`
- `SchoolAttendance`

`SchoolEnrollments` is the explicit class-student relationship. Student records expose current class context from active enrolments, not from free-text class storage alone.

Important constraints:

- Unique owner plus student admission number.
- Unique owner plus class plus student plus enrollment status, preventing duplicate active enrolments.
- Unique owner plus class plus student plus attendance date.
- Foreign keys from enrolments and attendance to student/class records.
- Cascade behavior is handled through SQLAlchemy relationships so deleting a student or class removes dependent enrolments and attendance records.

Indexes are based on owner-scoped list, filter, sorting, class lookup, student lookup, attendance date, and status query patterns.

## API Design

Routes live under `/api/v1/school-administration`.

The API provides:

- Dashboard summary endpoint.
- Student CRUD and duplicate endpoints.
- Class CRUD and duplicate endpoints.
- Enrollment create/delete endpoints.
- Attendance CRUD endpoints.

List and dashboard responses return lightweight summaries and previews. Detail endpoints return full editable note/support fields. Update payloads are separate from create payloads; attendance updates do not accept create-only `classId` or `studentId`.

All queries are owner-scoped through the authenticated user. The service verifies that class, student, enrolment, and attendance IDs belong to the current owner before linking or mutating records.

## Shared Components Used

The frontend uses established Ansiversa shared components:

- `AvAppOverviewPage`
- `AvAuthenticatedPageState`
- `AvPageHeader`
- `AvCardEmptyState`
- `AvInlineFeedback`
- `AvPagination`
- `AvRecordActions`
- `AvFormDrawer`
- `useAvConfirmDialog`

State is managed through a module-local Zustand store.

## Performance Considerations

The dashboard payload seeds the workflow with summaries needed by the current V1 UI. The backend keeps large text fields out of list responses by returning previews. Detail endpoints are used for editing full records. Attendance rate excludes `not_recorded` records and handles zero-record cases with a 0% rate and explicit calculation basis.

## Current Status

Workflow Ready. The app remains `active` / `comingSoon` with `version = null` and no approved destination metadata.

## Known Limitations

- No role-based staff access.
- No parent or student portal.
- No fee collection, invoices, or payments.
- No admissions workflow.
- No exams, grades, transcripts, or LMS functionality.
- No government/ministry reporting.
- No biometric attendance.
- No document attachments or imports.

## Future Enhancements

Potential future directions include fees and invoice tracking, teacher management, timetables, exams and grades, parent/student portals, document attachments, ID card generation, notifications, admissions workflow, multi-campus support, CSV import/export, audit trail, and role-based staff access.

## Current Implementation

School Administration V1 is implemented as an owner-scoped FastAPI module with isolated SQLAlchemy models, an Alembic migration, generated OpenAPI contracts, and a React workflow under `src/modules/school-administration`.
