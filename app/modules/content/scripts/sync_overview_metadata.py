"""Validate and sync overview JSON files into parent metadata.

Run with:

    python3 -m app.modules.content.scripts.sync_overview_metadata
"""

import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select

from app.core.database import ParentSessionLocal
from app.modules.content.models import Metadata
from app.modules.content.schemas import OverviewResponse
from app.modules.content.service import delete_metadata, get_metadata, upsert_metadata
from app.modules.content.scripts.validate_overview_ctas import validate_overview_ctas


OVERVIEW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "overview"
REFERENCE_FILENAMES = {"apps.json"}
LEGACY_OVERVIEW_KEYS = {"quiz", "resume-builder"}


def load_overview(path: Path) -> dict:
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    try:
        return OverviewResponse.model_validate(content).model_dump(
            mode="json",
            exclude_none=True,
        )
    except ValidationError as exc:
        raise ValueError(f"{path}: overview schema validation failed:\n{exc}") from exc


def sync_overview_metadata() -> int:
    cta_errors = validate_overview_ctas()
    if cta_errors:
        details = "\n".join(f"{error.path}: {error.message}" for error in cta_errors)
        raise ValueError(f"Overview CTA validation failed:\n{details}")

    paths = sorted(
        path
        for path in OVERVIEW_DATA_DIR.rglob("*.json")
        if path.name not in REFERENCE_FILENAMES
    )
    if not paths:
        raise ValueError(f"No overview JSON files found under {OVERVIEW_DATA_DIR}.")

    seen_keys: set[str] = set()
    validated: list[tuple[str, dict]] = []

    for path in paths:
        key = f"overview:{path.stem}"
        if key in seen_keys:
            raise ValueError(f"Duplicate overview metadata key: {key}")

        seen_keys.add(key)
        validated.append((key, load_overview(path)))

    with ParentSessionLocal() as db:
        for key, content in validated:
            upsert_metadata(db, key, content)
            print(f"Synced {key}")

        stored_overview_keys = set(
            db.execute(
                select(Metadata.key).where(Metadata.key.like("overview:%"))
            )
            .scalars()
            .all()
        )
        stale_overview_keys = stored_overview_keys - seen_keys

        for key in sorted(stale_overview_keys):
            delete_metadata(db, key)
            print(f"Removed stale overview key {key}")

        for key in sorted(LEGACY_OVERVIEW_KEYS):
            if get_metadata(db, key) is not None:
                delete_metadata(db, key)
                print(f"Removed legacy overview key {key}")

    print(
        "Done. "
        f"Synced {len(validated)} overview metadata records; "
        f"removed {len(stale_overview_keys)} stale overview records."
    )
    return len(validated)


def main() -> None:
    try:
        sync_overview_metadata()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
