"""Verify parent Apps catalog data against approved-apps.md.

Run with:

    python -m app.modules.apps.scripts.verify_approved_catalog
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.modules.apps.scripts.sync_approved_catalog import (
    default_approved_path,
    print_report,
    verify_approved_catalog,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify approved Ansiversa Apps catalog data.")
    parser.add_argument(
        "--source",
        type=Path,
        default=default_approved_path(),
        help="Path to approved-apps.md.",
    )
    args = parser.parse_args()

    report = verify_approved_catalog(args.source)
    print_report(report, applied=True)

    failed = (
        report.categories_synced != 14
        or report.apps_synced != 100
        or bool(report.duplicate_keys)
        or bool(report.duplicate_slugs)
        or bool(report.invalid_category_apps)
        or bool(report.missing_apps)
    )
    if failed:
        raise SystemExit("Catalog verification failed.")


if __name__ == "__main__":
    main()
