from __future__ import annotations

import argparse
import json

from validation.astra_app_val_001.runner import run_all, run_scenario, scenario_names


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ASTRA-APP-VAL-001 Subscription Manager governed read execution validation."
    )
    parser.add_argument("--list", action="store_true", help="List available scenarios.")
    parser.add_argument("--scenario", help="Run one scenario by name.")
    parser.add_argument("--all", action="store_true", help="Run all scenarios.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    if args.list:
        return _emit(tuple({"scenario": name} for name in scenario_names()), args.format)
    if args.scenario:
        return _emit(run_scenario(args.scenario), args.format)
    if args.all:
        return _emit(run_all(), args.format)
    parser.error("Use --list, --scenario, or --all.")
    return 2


def _emit(payload, output_format: str) -> int:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, default=lambda value: value.model_dump(mode="json")))
        return 0
    if hasattr(payload, "text"):
        print(payload.text())
        return 0
    for item in payload:
        if hasattr(item, "text"):
            print(item.text())
            print()
        else:
            print(f"{item.get('scenario', 'scenario')}: available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
