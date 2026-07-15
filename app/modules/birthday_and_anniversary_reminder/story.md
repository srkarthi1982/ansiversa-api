# Birthday & Anniversary Reminder Story

## Purpose

Birthday & Anniversary Reminder gives authenticated users a private workspace for important annual occasions and preparation notes.

## Workflow

Users create reminder records, assign occasion types, save event dates, add relationship/contact details, gift ideas, and notes, then review upcoming or missed reminders. Acknowledging a reminder marks the current year handled while preserving the next annual occurrence.

## Database Design

The module owns an isolated database configured by `BIRTHDAY_AND_ANNIVERSARY_REMINDER_DATABASE_URL`.

- `ReminderTypes`: owner-scoped seeded/custom occasion types.
- `ReminderContacts`: owner-scoped reminder records with person, date, contact, gift, favourite, and archive fields.
- `ReminderAcknowledgements`: owner-scoped per-year acknowledgement records.

The Alembic version table is `birthday_and_anniversary_reminder_alembic_version`.

## API Design

The API is mounted at `/api/v1/birthday-and-anniversary-reminder` and provides dashboard, insights, type CRUD, reminder CRUD, archive/restore, favourite/unfavourite, acknowledge, search, filters, and annual recurrence calculations.

## Performance Considerations

Indexes support owner lists, type filters, archived/favourite filters, event-date ordering, relationship filters, updated review, and acknowledgement-year checks.

## Current Status

Approved live at version `1.0.0` after Astra review, Partner approval, production-configured isolated database migration verification, production Apps row promotion, overview metadata sync, and manual browser workflow verification. Destination metadata is synced at `20 / 100`, status `approved`, reviewed on `2026-07-15`.

## Known Limitations

No automatic messages, notifications, contact import, calendar sync, sharing, exports, or AI features are implemented. V2 UI polish should replace native browser delete confirmations with shared `AvConfirmDialog` and move create/edit flows into shared drawers for platform consistency.

## Future Enhancements

Notification reminders, calendar export, printable lists, optional gift suggestions, and message drafts can be considered after V1 approval.

## Current Implementation

The production catalog row is `active` / `live` / `1.0.0`.
