"""Validate and sync overview JSON files into parent metadata.

Run with:

    python3 -m app.modules.content.scripts.sync_overview_metadata
"""

import json
from pathlib import Path

from pydantic import ValidationError

from app.core.database import ParentSessionLocal
from app.modules.content.schemas import OverviewResponse
from app.modules.content.service import upsert_metadata


OVERVIEW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "overview"


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
    paths = sorted(OVERVIEW_DATA_DIR.rglob("*.json"))
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

    print(f"Done. Synced {len(validated)} overview metadata records.")
    return len(validated)


def main() -> None:
    try:
        sync_overview_metadata()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
