# Medicine Reminder Destination

## App Name

Medicine Reminder

## Destination Status

Approved v1.0

## Final Product Vision

Medicine Reminder should become Ansiversa's calm medication routine workspace: a private place where users organize medicines, schedules, dose history, refill awareness, and review notes without receiving unapproved medical advice.

## Target Users

- People managing daily or weekly medicines.
- Caregivers supporting a family member's routine.
- Users with temporary prescriptions.
- Users with chronic routines who want a personal adherence record.
- Users preparing notes for pharmacy or doctor conversations.

## Core User Problems

- Users forget whether they took a dose.
- Medication instructions and schedules are scattered across bottles, paper, messages, and memory.
- Refills can be noticed too late.
- Users need a history of taken, missed, skipped, and late doses.
- Users want notes for side effects, questions, or medication changes.

## Final Capabilities

- Create, edit, archive, and delete medicines.
- Add one or more reminder schedules per medicine.
- Log taken, missed, skipped, and late doses.
- Review daily and weekly medication history.
- Track refill reminder dates and basic quantity awareness.
- Store medicine-specific notes.
- Filter and search medicines and dose history.
- Keep list responses lightweight and detail endpoints complete.
- Support accessible responsive workflows inside the Ansiversa shell.

## Advanced Capabilities

- Platform notifications after governance approval.
- Caregiver sharing and escalation after privacy review.
- Exportable medication summaries for doctor visits.
- Calendar integration.
- Refill quantity calculations.
- Medication cabinet print view.
- Optional family member profiles if Partner/Astra approve multi-person health tracking.

## AI Opportunities

- Convert user-entered prescription text into a draft schedule for user review.
- Summarize dose history and notes for appointments.
- Detect incomplete setup, such as an active medicine without a schedule.
- Suggest questions to ask a pharmacist or doctor based on user notes.
- Explain app records in plain language without diagnosing or prescribing.

## Ecosystem Connections

Medicine Reminder can later connect with Doctor Visit Tracker, Health Report Organizer, Emergency Contacts Organizer, Family Task Planner, Wellness and Goal Planner, and Dashboard summaries through approved APIs. It must not directly own or mutate records in those apps.

## Weekly Return Value

Users return weekly to confirm medication routines, review missed doses, update refill reminders, and add notes that reduce uncertainty before pharmacy or doctor conversations.

## Success Criteria

- Users can create medicines and schedules quickly.
- Dose logging is faster than relying on memory.
- Missed and late doses are visible without shame-based messaging.
- The API preserves privacy with owner-scoped minimal responses.
- The app remains practical and avoids medical advice claims.

## Journey Progress

Current Position: 32 / 100
Destination: 100 / 100
Remaining Journey: 68 / 100

This estimate describes product maturity, not feature completion. Workflow Ready V1 includes medicines, schedules, dose logs, notes, dashboard summaries, search/filter workflows, owner-scoped APIs, isolated database storage, and knowledge lifecycle documentation. The remaining journey includes real notification delivery, caregiver workflows, exports, advanced refill intelligence, and carefully governed AI assistance.

## Future Version Ideas

- V1.1: Reminder notification delivery and daily today view.
- V1.2: Refill quantity tracking and pharmacy notes.
- V1.3: Doctor visit summary export.
- V2: Opt-in caregiver sharing.
- V2+: AI-assisted setup and review under strict safety governance.

## Non Goals

- Do not provide medical diagnosis.
- Do not recommend dosage changes.
- Do not provide drug-interaction claims without approved clinical data.
- Do not replace emergency care or clinician advice.
- Do not create hidden caregiver sharing.

## Guiding Principles

- User control comes first.
- Medication data is sensitive.
- Reminders support routines; they do not guarantee adherence.
- Use clear language and avoid fear-based messaging.
- Keep the app useful even without AI or external integrations.

## Governance Notes

Astra: Approved on 2026-07-11.

Partner: Approved Medicine Reminder live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes, synced destination metadata, and prepared live promotion metadata.
