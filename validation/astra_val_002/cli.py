from __future__ import annotations

import argparse
import json
import sys

from validation.astra_val_002.runner import SCENARIO_NAMES, run_all, run_scenario


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="ASTRA-VAL-002 local projection integrity and privacy validation"
    )
    selection = value.add_mutually_exclusive_group(required=True)
    selection.add_argument("--list", action="store_true")
    selection.add_argument("--scenario")
    selection.add_argument("--all", action="store_true")
    value.add_argument("--format", choices=("text", "json"), default="text")
    return value


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if args.list:
        print("\n".join(SCENARIO_NAMES))
        return 0
    if args.scenario and args.scenario not in SCENARIO_NAMES:
        print(f"ASTRA-VAL-002 unknown scenario: {args.scenario}", file=sys.stderr)
        return 2
    try:
        results = run_all() if args.all else (run_scenario(args.scenario),)
    except Exception as exc:
        print(f"ASTRA-VAL-002 setup failure: {type(exc).__name__}", file=sys.stderr)
        return 3
    if args.format == "json":
        payload = [item.model_dump(mode="json") for item in results]
        print(
            json.dumps(
                payload[0] if len(payload) == 1 else payload,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    else:
        print("\n\n".join(item.text() for item in results))
    return 0 if all(item.passed for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
