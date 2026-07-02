# Price Checker

## Purpose

Price Checker supports a privacy-first browser-local workflow for manually comparing product prices. V1 helps users organize purchase decisions without backend shopping history, live shopping APIs, scraping, alerts, or cloud synchronization.

## Workflow

The frontend provides a public overview and protected Analyze, Analyses, and Insights routes. Users create manual price analyses, save them locally, manage saved comparisons, and review local insights.

## User Journey

Users start at `/price-checker`, continue to `/price-checker/analyze`, enter product, store, category, current price, optional previous price, and notes, then save the analysis locally. They can search, filter, edit, duplicate, delete, clear, and review insights from saved analyses.

## Database Design

There is no Price Checker database in V1. The backend does not store products, stores, prices, notes, shopping history, alerts, or background job state.

## API Design

There are no Price Checker runtime APIs in V1. The backend only serves parent catalog and overview metadata through existing content endpoints. No shopping API integration, scraping route, alert route, notification route, or cloud synchronization route exists for this app.

## Shared Components Used

The frontend uses the shared Ansiversa shell, authenticated page state, page header, form drawer, empty state, inline feedback, feedback stack, stat grid, record actions, and card patterns.

## Performance Considerations

V1 avoids shopping SDKs, scraping libraries, browser extensions, alert systems, background jobs, chart libraries, backend runtime persistence, and new dependencies. The backend footprint is limited to overview metadata and documentation.

## Current Status

Approved live at version `1.0.0`. App #050 remains browser-local and uses backend catalog/overview metadata only.

## Known Limitations

Prices are manually entered and are not verified against live stores. V1 does not normalize currencies, monitor price changes, send alerts, scrape pages, compare live listings, or sync data across devices.

## Future Enhancements

Future versions may add approved import/export, currency support, optional alerting, or trusted API integrations after privacy, legal, and architecture review.

## Current Implementation

The backend owns only catalog and overview metadata for Price Checker. No backend runtime persistence or app-specific API module exists for product price content.
