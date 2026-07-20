"""Read-only drift check for public AI knowledge artifacts."""

from __future__ import annotations

import json
from xml.etree import ElementTree

from app.modules.knowledge.publisher import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    PUBLIC_AI_JSONLD_PATH,
    PUBLIC_AI_KNOWLEDGE_PATH,
    PUBLIC_AI_METADATA_PATH,
    PUBLIC_AI_SITEMAP_PATH,
    ROBOTS_PATH,
    _serialized_json,
    build_public_artifacts,
    validate_public_artifacts,
)


def _read(path):
    return path.read_text(encoding="utf-8")


def main() -> None:
    artifacts = build_public_artifacts()
    validate_public_artifacts(artifacts)
    expected = {
        PUBLIC_AI_KNOWLEDGE_PATH: _serialized_json(artifacts.knowledge),
        PUBLIC_AI_JSONLD_PATH: _serialized_json(artifacts.jsonld),
        PUBLIC_AI_METADATA_PATH: _serialized_json(artifacts.metadata),
        PUBLIC_AI_SITEMAP_PATH: artifacts.sitemap,
        LLMS_PATH: artifacts.llms,
        LLMS_FULL_PATH: artifacts.llms_full,
        ROBOTS_PATH: artifacts.robots,
    }
    stale = [path for path, content in expected.items() if not path.exists() or _read(path) != content]
    if stale:
        raise SystemExit(
            "public knowledge artifacts stale: "
            + ", ".join(path.relative_to(PUBLIC_AI_KNOWLEDGE_PATH.parents[1]).as_posix() for path in stale)
        )

    json.loads(_read(PUBLIC_AI_KNOWLEDGE_PATH))
    json.loads(_read(PUBLIC_AI_JSONLD_PATH))
    json.loads(_read(PUBLIC_AI_METADATA_PATH))
    ElementTree.fromstring(_read(PUBLIC_AI_SITEMAP_PATH))
    print("public knowledge artifacts: current")


if __name__ == "__main__":
    main()
