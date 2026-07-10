"""Sync approved destination metadata into catalog export data.

Run with:

    python3 -m app.modules.apps.scripts.sync_destination_metadata --apply
    python3 -m app.modules.apps.scripts.sync_destination_metadata --check
"""

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


APPROVED_STATUS = "approved"
EXPECTED_LIVE_DESTINATION_COUNT = 58
REVIEW_DATE_PATTERN = re.compile(r"Astra: Approved on (?P<date>\d{4}-\d{2}-\d{2})\.")
PROGRESS_PATTERN = re.compile(r"Current Position:\s*(?P<progress>\d+)\s*/\s*100")


@dataclass(frozen=True)
class DestinationMetadata:
    slug: str
    progress: int
    status: str
    reviewed_at: date


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def modules_dir() -> Path:
    return repo_root() / "app" / "modules"


def apps_json_path() -> Path:
    return modules_dir() / "content" / "data" / "overview" / "apps.json"


def _section_value(lines: list[str], heading: str) -> str:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            for value in lines[index + 1 :]:
                stripped = value.strip()
                if stripped:
                    return stripped

    return ""


def parse_destination(path: Path) -> DestinationMetadata | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    destination_status = _section_value(lines, "## Destination Status")
    if destination_status != "Approved v1.0":
        return None

    progress_match = PROGRESS_PATTERN.search(text)
    if progress_match is None:
        raise ValueError(f"{path}: approved destination is missing Journey Progress.")

    review_match = REVIEW_DATE_PATTERN.search(text)
    if review_match is None:
        raise ValueError(f"{path}: approved destination is missing Astra approval date.")

    progress = int(progress_match.group("progress"))
    if progress < 0 or progress > 100:
        raise ValueError(f"{path}: Journey Progress must be between 0 and 100.")

    return DestinationMetadata(
        slug=path.parent.name.replace("_", "-"),
        progress=progress,
        status=APPROVED_STATUS,
        reviewed_at=date.fromisoformat(review_match.group("date")),
    )


def load_destination_metadata() -> dict[str, DestinationMetadata]:
    metadata: dict[str, DestinationMetadata] = {}
    for path in sorted(modules_dir().glob("*/destination.md")):
        item = parse_destination(path)
        if item is None:
            continue
        if item.slug in metadata:
            raise ValueError(f"Duplicate destination metadata for slug: {item.slug}")
        metadata[item.slug] = item

    return metadata


def load_apps_json() -> dict[str, list[dict[str, object]]]:
    return json.loads(apps_json_path().read_text(encoding="utf-8"))


def sync_apps_json(apps_data: dict[str, list[dict[str, object]]], metadata: dict[str, DestinationMetadata]) -> int:
    live_slugs = {
        str(app["slug"])
        for apps in apps_data.values()
        for app in apps
        if app.get("launchStatus") == "live"
    }
    missing = sorted(live_slugs - set(metadata))
    extra = sorted(set(metadata) - live_slugs)
    if missing:
        raise ValueError(f"Live apps missing approved destination metadata: {missing}")
    if extra:
        raise ValueError(f"Destination metadata exists for non-live apps: {extra}")
    if len(metadata) != EXPECTED_LIVE_DESTINATION_COUNT:
        raise ValueError(
            "Expected "
            f"{EXPECTED_LIVE_DESTINATION_COUNT} approved live destinations, found {len(metadata)}."
        )

    changed = 0
    for apps in apps_data.values():
        for app in apps:
            item = metadata.get(str(app["slug"]))
            expected_progress = item.progress if item else None
            expected_status = item.status if item else None
            expected_reviewed_at = item.reviewed_at.isoformat() if item else None

            if app.get("destination_progress") != expected_progress:
                app["destination_progress"] = expected_progress
                changed += 1
            if app.get("destination_status") != expected_status:
                app["destination_status"] = expected_status
                changed += 1
            if app.get("destination_reviewed_at") != expected_reviewed_at:
                app["destination_reviewed_at"] = expected_reviewed_at
                changed += 1

    return changed


def write_apps_json(apps_data: dict[str, list[dict[str, object]]]) -> None:
    apps_json_path().write_text(
        json.dumps(apps_data, indent="\t") + "\n",
        encoding="utf-8",
    )


def run(apply: bool) -> int:
    metadata = load_destination_metadata()
    apps_data = load_apps_json()
    changed = sync_apps_json(apps_data, metadata)

    if apply:
        write_apps_json(apps_data)

    if changed and not apply:
        raise SystemExit(
            f"apps.json is not synced with destination metadata ({changed} field updates pending)."
        )

    print(
        "Destination metadata check passed. "
        f"Approved live apps: {len(metadata)}. "
        f"apps.json field updates: {changed}."
    )
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync approved destination metadata.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Write destination metadata into apps.json.")
    mode.add_argument("--check", action="store_true", help="Verify apps.json destination metadata.")
    args = parser.parse_args()

    run(apply=bool(args.apply))


if __name__ == "__main__":
    main()
