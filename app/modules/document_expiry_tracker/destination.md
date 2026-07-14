# Document Expiry Tracker Destination

## Document Status

Approved for Live promotion on 2026-07-14 after Astra review, Partner approval, production migration verification, and manual browser verification.

## Destination Status

Approved v1.0

## Destination

Document Expiry Tracker should mature into Ansiversa's private renewal planning workspace for personal documents. Its destination is a calm, reliable place to understand which documents need attention, what dates matter, and what the next renewal step is, without pretending to file official renewals or send regulated notifications before those capabilities are approved.

The destination is always `100 / 100`. The current approved Journey Progress is `20 / 100`.

## Purpose

The app exists because many important personal documents matter only when they are close to expiring. Users need an owner-scoped place to keep document date metadata visible without maintaining scattered calendar reminders or spreadsheets.

## Mature Product Direction

A mature version should support:

- personal and household document renewal planning
- richer reminder preferences after notification governance
- optional attachment support after privacy review
- safer import or OCR helpers only after explicit approval
- clear expiry windows and renewal readiness indicators
- cross-platform consistency inside the Ansiversa shell

## Non-Goals

The app must not become:

- a government renewal service
- an identity verification provider
- a document scanning vault without privacy approval
- a compliance team automation system
- a notification delivery product before notification infrastructure is approved
- an AI extraction product before AI governance approval

## Journey Progress

Current Position: 20 / 100

Current Journey Progress: 20 / 100

V1 creates the manual recordkeeping foundation with CRUD, computed statuses, archive/restore, simple renewal updates, dashboard windows, insights, isolated storage, and clear product boundaries. Remaining maturity includes possible reminder delivery, document attachments, export, richer household support, and governed OCR or AI extraction.

## Current Implementation

The current implementation stores personal document metadata in the isolated `Documents` table. It computes status dynamically from expiry date, reminder days, and archive state. The first workflow route is `/document-expiry-tracker/documents`. Catalog status is approved for live release at version `1.0.0`.

## Governance Notes

Astra: Approved on 2026-07-14.

Partner: Approved Document Expiry Tracker live promotion after manual workflow verification.

Codex: Ran production-configured isolated database migration, verified schema/indexes/version table, synced overview metadata, and prepared live promotion metadata.
