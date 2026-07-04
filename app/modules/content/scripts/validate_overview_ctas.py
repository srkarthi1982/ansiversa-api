"""Validate mini-app overview Explore CTA routing.

Run with:

    python3 -m app.modules.content.scripts.validate_overview_ctas
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


OVERVIEW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "overview"
REFERENCE_FILENAMES = {"apps.json"}
EXPLORE_LABEL = "Explore"
INVALID_PATH_PARTS = ("coming-soon", "comingsoon", "placeholder")


@dataclass(frozen=True)
class CtaValidationError:
    path: Path
    message: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _frontend_route_registry_path() -> Path:
    return _repo_root().parent / "ansiversa" / "src" / "app" / "router" / "appModulePages.ts"


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: overview metadata must be a JSON object.")
    return value


def _load_first_workflow_routes(registry_path: Path) -> dict[str, str]:
    if not registry_path.exists():
        return {}

    content = registry_path.read_text(encoding="utf-8")
    routes: dict[str, str] = {}
    app_blocks = re.finditer(
        r"'(?P<slug>[a-z0-9-]+)':\s*\[(?P<body>.*?)\]",
        content,
        flags=re.DOTALL,
    )
    for match in app_blocks:
        first_slug = re.search(r"slug:\s*'(?P<page>[a-z0-9-]+)'", match.group("body"))
        if first_slug is not None:
            app_slug = match.group("slug")
            routes[app_slug] = f"/{app_slug}/{first_slug.group('page')}"
    return routes


def _validate_action(
    *,
    metadata_path: Path,
    app_slug: str,
    name: str,
    action: object,
    first_workflow_route: str | None,
) -> list[CtaValidationError]:
    errors: list[CtaValidationError] = []
    if not isinstance(action, dict):
        return [CtaValidationError(metadata_path, f"{name} CTA is missing or is not an object.")]

    label = action.get("label")
    cta_path = action.get("path")
    if label != EXPLORE_LABEL:
        errors.append(CtaValidationError(metadata_path, f"{name} CTA label must be {EXPLORE_LABEL!r}; found {label!r}."))

    if not isinstance(cta_path, str) or not cta_path.strip():
        errors.append(CtaValidationError(metadata_path, f"{name} CTA path is missing or empty."))
        return errors

    cta_path = cta_path.strip()
    overview_route = f"/{app_slug}"
    if not cta_path.startswith("/"):
        errors.append(CtaValidationError(metadata_path, f"{name} CTA path must be an absolute app route; found {cta_path!r}."))
    if first_workflow_route is not None and cta_path == overview_route:
        errors.append(CtaValidationError(metadata_path, f"{name} CTA path must not route back to the overview route {overview_route!r}."))
    if any(part in cta_path.lower() for part in INVALID_PATH_PARTS):
        errors.append(CtaValidationError(metadata_path, f"{name} CTA path must not use a placeholder or coming-soon route; found {cta_path!r}."))
    if first_workflow_route is not None and cta_path != first_workflow_route:
        errors.append(
            CtaValidationError(
                metadata_path,
                f"{name} CTA path must enter the first workflow route {first_workflow_route!r}; found {cta_path!r}.",
            )
        )

    return errors


def validate_overview_ctas() -> list[CtaValidationError]:
    first_workflow_routes = _load_first_workflow_routes(_frontend_route_registry_path())
    errors: list[CtaValidationError] = []
    metadata_paths = sorted(
        path
        for path in OVERVIEW_DATA_DIR.glob("*.json")
        if path.name not in REFERENCE_FILENAMES
    )

    if not metadata_paths:
        return [CtaValidationError(OVERVIEW_DATA_DIR, "No overview metadata JSON files found.")]

    for metadata_path in metadata_paths:
        app_slug = metadata_path.stem
        metadata = _load_json(metadata_path)
        first_workflow_route = first_workflow_routes.get(app_slug)
        hero_action = metadata.get("hero", {}).get("primaryAction") if isinstance(metadata.get("hero"), dict) else None
        final_action = metadata.get("finalCta", {}).get("action") if isinstance(metadata.get("finalCta"), dict) else None

        errors.extend(
            _validate_action(
                metadata_path=metadata_path,
                app_slug=app_slug,
                name="Primary",
                action=hero_action,
                first_workflow_route=first_workflow_route,
            )
        )
        errors.extend(
            _validate_action(
                metadata_path=metadata_path,
                app_slug=app_slug,
                name="Final",
                action=final_action,
                first_workflow_route=first_workflow_route,
            )
        )

    return errors


def main() -> None:
    try:
        errors = validate_overview_ctas()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}")
        raise SystemExit(f"Overview CTA validation failed with {len(errors)} error(s).")

    print("Overview CTA validation passed.")


if __name__ == "__main__":
    main()
