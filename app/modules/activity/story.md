# Universal Activity Timeline

This parent module records safe, concise milestones in one authenticated user’s Ansiversa journey. It is not an audit log, analytics tracker, surveillance system, or replacement for app-owned record history.

The `ActivityTimeline` table stores bounded type, title, optional generic description, source, optional canonical app, optional internal action, bounded entity references, and timestamp. It never stores raw payloads, JSON snapshots, prompts, answers, financial or medical values, document contents, passwords, tokens, file names, IP addresses, user agents, or stack traces.

Future integrations call `record_activity(...)` or the failure-isolated `record_activity_safely(...)`; no unrestricted create endpoint exists. Navigation events use a dedicated endpoint and a 30-minute per-app cooldown. Client-originated platform events are limited to generic assistant usage and notification continuation. Retention is the newest 1,000 records per user, enforced at publish time without background cleanup.

Production migration was verified on 2026-07-20 at parent Alembic head `20260720_0002`. The `ActivityTimeline` table and both owner-scoped indexes are present in `ansiversaDb`.
