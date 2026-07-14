# Document Expiry Tracker Market Study

## Document Status

Research note for App #073 initial development.

## Market Version

1

## Created

2026-07-14

## Last Reviewed

2026-07-14

## Next Review

2026-10-14

## Purpose

Understand the public market around document and expiry reminder tools before building the Ansiversa V1 workflow.

## Problem Statement

Users miss important renewal dates because passports, IDs, licences, permits, insurance policies, and certificates are not reviewed every day. Existing alternatives often split the date from the underlying document context, add notification complexity, or target business compliance teams instead of individual personal planning.

## Target Users

- Individuals tracking passports, IDs, licences, residence documents, and insurance.
- Households managing multiple family document dates.
- Frequent travelers who need early visibility into travel document renewal dates.
- Small personal planners who do not need enterprise compliance automation.

## Competitor Landscape

- Mobile-first personal reminders: Document Expiry Reminder, DocuAlert, Expiry Reminder, EverPass.
- Document vaults with reminder features: NeuVault, DocStow, Filvy.
- Business expiration systems: Remindax, Expiration Reminder, Contracko, Microsoft Marketplace integrations.
- Generic alternatives: Apple Calendar, reminders apps, spreadsheets, Notion, Google Sheets, and scanner apps.

## Common Market Features

- Document name, type, expiry date, and notes.
- Custom reminder windows.
- Expired and upcoming lists.
- Mobile alerts.
- Document upload or scan in richer products.
- OCR or AI extraction in newer products.
- Team assignment and multi-channel alerts in business tools.

## User Love Signals

- Users value avoiding penalties, travel disruption, and last-minute renewal stress.
- Mobile products emphasize simple entry and reminders for passports, visas, licences, IDs, permits, insurance, and certificates.
- Business tools show demand for centralized expiration visibility and automatic alerting when many documents are involved.

## Complaints / Friction

- Manual entry can be tedious.
- Generic reminders disconnect the expiry date from the document context.
- OCR and AI extraction create trust and privacy questions.
- Enterprise tools can be too heavy for personal use.
- Notification-heavy products can overpromise reliability if delivery infrastructure is not mature.

## Pricing / Paywall Observations

The market spans free mobile utilities, freemium personal apps, and business subscription tools. Business products commonly charge for automation, team workflows, multi-channel reminders, and integrations. Personal products compete more on privacy, simplicity, and offline or mobile convenience.

## AI Trends

Some products now advertise OCR, MRZ scanning, AI extraction, or automatic date capture. These features reduce manual entry but increase privacy and accuracy risk. Ansiversa V1 should avoid AI extraction until there is explicit governance approval and clear user review.

## UX Patterns

- First screen often centers on the item list and upcoming expirations.
- Status colors usually separate expired, due soon, and active records.
- Reminder windows are simple numeric settings.
- Document type filters are common.
- Business tools highlight dashboards and team notification routing.

## Opportunities

- Build a private manual metadata workflow first.
- Keep status computation transparent and deterministic.
- Separate normal active totals from archived records.
- Keep the first workflow route on Documents so users can act immediately.
- Use insights to make upcoming renewal load visible without becoming a notification platform.

## Avoid List

- Do not copy competitor wording, screens, or reminder schedules.
- Do not implement file uploads, OCR, AI extraction, SMS, email, push, or calendar integration in V1.
- Do not imply official renewal handling.
- Do not position the app as enterprise compliance automation.

## Product Questions

- Should future household sharing exist, or should each user's records remain individual?
- Which notification channels should be approved first if reminder delivery is added?
- Should file attachments belong in this app or in a future document vault app?
- Should OCR extraction be tied to explicit confidence scores and user review?

## Sources

- Apple App Store, Document Expiry Reminder: https://apps.apple.com/us/app/document-expiry-reminder/id6756968613
- Google Play, DocuAlert: https://play.google.com/store/apps/details?id=com.docualert.documents_expiry_reminder
- Remindax: https://www.remindax.com/
- Expiration Reminder: https://www.expirationreminder.com/
- NeuVault document expiry reminder page: https://neuvault.app/document-expiry-reminder-app
- Filvy alternatives article: https://filvy.app/blog/en/expiration-reminder-alternatives/
- Microsoft Marketplace, Expiration Reminder: https://marketplace.microsoft.com/en-cy/product/office/WA200006920
- Contracko guide: https://contracko.com/blog/expiration-reminder-software

## Review Notes

Initial market review supports a bounded V1 focused on manual metadata, computed expiry states, and owner-scoped records. Notification and OCR capabilities should remain future governance decisions.

## Revision History

- 2026-07-14: Market Version 1 created during App #073 initial development.
