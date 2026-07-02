# Voice Converter

## Purpose

Voice Converter provides a privacy-first browser-native text-to-speech workflow for Ansiversa. V1 keeps speech conversion local and avoids backend text storage, cloud TTS providers, generated audio files, and AI SDKs.

## Workflow

The frontend provides a public overview and protected Workspace, History, and Insights routes. Users enter text, choose a browser voice, preview speech through Speech Synthesis, and save local sessions.

## User Journey

Users start at `/voice-converter`, continue to `/voice-converter/workspace`, preview speech locally, then review sessions in History and Insights.

## Database Design

There is no Voice Converter database in V1. The backend does not store text, audio, speech sessions, playback settings, or user history for this app.

## API Design

There are no Voice Converter runtime APIs in V1. The backend only serves parent catalog and overview metadata through existing content endpoints.

## Shared Components Used

The frontend uses the shared Ansiversa shell, page header, authenticated page state, form drawer, empty state, feedback stack, and card patterns.

## Performance Considerations

V1 avoids audio libraries, backend uploads, cloud providers, generated audio blobs, and server-side processing. Local records are small JSON entries saved in browser storage.

## Current Status

Approved Live. App #046 is promoted to `active` / `live` with version `1.0.0` after Astra/Partner approval, production Apps row promotion, overview metadata sync, tracked catalog export update, validation, and production route verification.

## Known Limitations

Speech output depends on browser Speech Synthesis support and available local voices. V1 does not export audio, sync sessions, auto-read text, or integrate premium voice models.

## Future Enhancements

Future versions may add richer browser voice controls, safe export options, or backend/cloud speech processing after explicit privacy and architecture review.

## Current Implementation

The backend owns only catalog and overview metadata for Voice Converter. No backend runtime persistence or app-specific API module exists for text or audio content.
