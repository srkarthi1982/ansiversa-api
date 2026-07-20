"""CLI for generating the canonical knowledge registry."""

from __future__ import annotations

import json
import time

from app.modules.knowledge.builder import GAP_REPORT_PATH, REGISTRY_PATH, build_registry, serialized_registry, source_files


def main() -> None:
    started = time.perf_counter()
    registry, gaps = build_registry()
    content = serialized_registry(registry)
    gap_content = json.dumps({"schemaVersion": 1, "gaps": gaps}, indent=2, sort_keys=True) + "\n"
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    changed = not REGISTRY_PATH.exists() or REGISTRY_PATH.read_text(encoding="utf-8") != content
    if changed: REGISTRY_PATH.write_text(content, encoding="utf-8", newline="\n")
    if not GAP_REPORT_PATH.exists() or GAP_REPORT_PATH.read_text(encoding="utf-8") != gap_content:
        GAP_REPORT_PATH.write_text(gap_content, encoding="utf-8", newline="\n")
    backend, frontend = source_files()
    print(f"knowledge registry: apps={len(registry['apps'])} categories={len(registry['categories'])} sources={len(backend)+len(frontend)} warnings={len(gaps)} errors=0 bytes={len(content.encode('utf-8'))} changed={str(changed).lower()} elapsed_ms={(time.perf_counter()-started)*1000:.1f}")


if __name__ == "__main__": main()
