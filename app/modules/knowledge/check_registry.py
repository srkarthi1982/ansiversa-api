"""Read-only drift check for the canonical knowledge registry."""

from __future__ import annotations

from app.modules.knowledge.builder import REGISTRY_PATH, build_registry, serialized_registry


def main() -> None:
    expected = serialized_registry(build_registry()[0])
    actual = REGISTRY_PATH.read_text(encoding="utf-8") if REGISTRY_PATH.exists() else ""
    if actual != expected:
        raise SystemExit("Knowledge registry is stale. Run python -m app.modules.knowledge.build_registry")
    print("knowledge registry: current")


if __name__ == "__main__": main()
