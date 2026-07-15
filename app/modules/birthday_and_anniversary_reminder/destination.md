# Birthday & Anniversary Reminder Destination

## Document Status

Approved for Live promotion on 2026-07-15 after Astra review, Partner approval, production migration verification, production catalog verification, and manual browser verification.

## Destination Status

Approved v1.0

## Product Destination

Birthday & Anniversary Reminder should become a private memory aid for meaningful annual occasions. It helps users prepare for birthdays, anniversaries, graduations, and other dates without sending automatic messages.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## V1 Scope

- Protected reminder CRUD.
- Archive, restore, favourite, acknowledge, and delete actions.
- Seeded and custom occasion types.
- Annual next-occurrence and days-remaining calculations.
- Today, week, month, next 30 days, missed, and acknowledged filters.
- Dashboard and insights based on stored data.

## Non-Goals

- No automatic SMS, WhatsApp, email, or external notifications.
- No AI-generated gift suggestions.

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the private annual occasion reminder foundation with owner-scoped reminders, occasion types, acknowledgements, favourite/archive/restore/delete actions, annual next-occurrence calculations, search, filters, sorting, dashboard metrics, insights, production migration, and verified production workflow behavior. Remaining maturity includes shared drawer-based create/edit flows, shared confirmation dialogs, reminder notifications, calendar export, printable lists, and governed optional gift ideas.

## Review Status

Approved live at version `1.0.0`.

## Approved CTA

Explore → `/birthday-and-anniversary-reminder/reminders`

## Future Direction

- Move create/edit flows from inline panels to shared `AvDrawer`.
- Replace native browser delete confirmations with shared `AvConfirmDialog`.
- Add notification reminders through the approved platform notification layer.
- Add calendar export and printable lists after review.
- Consider optional gift ideas only after explicit governance approval.

## Governance Notes

Astra: Approved on 2026-07-15.

Partner: Approved Birthday & Anniversary Reminder live promotion after owner-review browser verification, with V2 UI polish notes for shared drawer forms and shared confirmation dialogs.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, synced overview metadata, promoted the production Apps row, synced destination metadata, and verified production catalog counts.
