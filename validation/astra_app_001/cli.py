from __future__ import annotations

import argparse
import json

from validation.astra_app_001.runner import run_all, run_scenario, scenario_names


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local ASTRA-APP-001 Subscription Manager validation scenarios.")
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
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return 0
    if isinstance(payload, dict):
        print(f"{payload.get('scenario', 'scenario')}: {payload.get('status', 'ok')}")
        if "message" in payload:
            print(payload["message"])
        return 0
    for item in payload:
        if isinstance(item, dict):
            print(f"{item.get('scenario', 'scenario')}: {item.get('status', 'available')}")
        else:
            print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
