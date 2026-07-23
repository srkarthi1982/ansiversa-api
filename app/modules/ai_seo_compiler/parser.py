"""Parser boundaries for approved AI SEO source inventory entries."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.modules.ai_seo_compiler.inventory import SourceInventoryItem, SourceKind, SourceVisibility
from app.modules.ai_seo_compiler.normalization import normalize_text

MAX_SOURCE_BYTES = 300_000
MAX_PARSED_TEXT = 2_000

MARKDOWN_SECTION_ALIASES = {
    "purpose": {"purpose", "product purpose"},
    "capabilities": {"current capabilities", "features", "current implementation"},
    "limitations": {"limitations", "non goals", "boundaries", "boundary"},
    "safety": {"safety", "safety notes"},
    "future": {"future direction", "future version ideas"},
}


@dataclass(frozen=True)
class SourceProvenance:
    repository: str
    path: str
    section: str
    field_name: str
    visibility: str
    kind: str

    @classmethod
    def from_item(cls, item: SourceInventoryItem) -> "SourceProvenance":
        return cls(
            repository=item.repository.value,
            path=item.path,
            section=item.section,
            field_name=item.field_name,
            visibility=item.visibility.value,
            kind=item.kind.value if item.kind else "",
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "path": self.path,
            "section": self.section,
            "fieldName": self.field_name,
            "visibility": self.visibility,
            "kind": self.kind,
        }


@dataclass(frozen=True)
class ParsedClaim:
    field_name: str
    value: str
    provenance: SourceProvenance

    def as_dict(self) -> dict[str, object]:
        return {
            "fieldName": self.field_name,
            "value": self.value,
            "provenance": self.provenance.as_dict(),
        }


def _assert_source_safe(content: str) -> None:
    if len(content.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds parser byte bound")


def _extract_json_path(data: dict[str, Any], section: str) -> Any:
    current: Any = data
    for part in section.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"Required JSON section missing: {section}")
        current = current[part]
    return current


def _stringify_json_value(value: Any) -> str:
    if isinstance(value, str):
        return normalize_text(value, max_length=MAX_PARSED_TEXT)
    if isinstance(value, list):
        values = []
        for item in value:
            if isinstance(item, str):
                values.append(item)
            elif isinstance(item, dict):
                values.extend(str(item[key]) for key in ("title", "description", "label") if key in item)
            else:
                values.append(str(item))
        return normalize_text(" | ".join(values), max_length=MAX_PARSED_TEXT)
    if isinstance(value, (int, float, bool)) or value is None:
        return normalize_text(str(value), max_length=MAX_PARSED_TEXT)
    raise ValueError("Unsupported JSON value for public claim parsing")


def parse_json_source(item: SourceInventoryItem, content: str) -> ParsedClaim:
    _assert_source_safe(content)
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON source: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON source root must be an object")
    value = _stringify_json_value(_extract_json_path(data, item.section))
    if not value:
        raise ValueError("Parsed JSON value is empty")
    return ParsedClaim(item.field_name, value, SourceProvenance.from_item(item))


def parse_markdown_sections(content: str) -> dict[str, str]:
    _assert_source_safe(content)
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in content.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^#{1,4}\s+(.+?)\s*$", line)
        if heading:
            normalized = normalize_text(heading.group(1)).lower()
            current = next((key for key, aliases in MARKDOWN_SECTION_ALIASES.items() if normalized in aliases), None)
            if current:
                sections.setdefault(current, [])
            continue
        if current and not line.lstrip().startswith("<!--"):
            sections[current].append(line)
    return {
        key: normalized
        for key, lines in sections.items()
        if (normalized := normalize_text("\n".join(lines), max_length=MAX_PARSED_TEXT))
    }


def parse_markdown_source(item: SourceInventoryItem, content: str) -> ParsedClaim:
    sections = parse_markdown_sections(content)
    section_key = item.section.strip().lower().replace(" ", "_")
    section_key = {
        "current_capabilities": "capabilities",
        "future_version_ideas": "future",
        "non_goals": "limitations",
    }.get(section_key, section_key)
    if section_key not in sections:
        raise ValueError(f"Required Markdown section missing: {item.section}")
    return ParsedClaim(item.field_name, sections[section_key], SourceProvenance.from_item(item))


def parse_registry_source(item: SourceInventoryItem, content: str) -> ParsedClaim:
    _assert_source_safe(content)
    if item.field_name == "slug":
        pattern = r'"slug"\s*:\s*"([^"]+)"'
    elif item.field_name == "name":
        pattern = r'"name"\s*:\s*"([^"]+)"'
    else:
        pattern = rf'"{re.escape(item.field_name)}"\s*:\s*"([^"]+)"'
    match = re.search(pattern, content)
    if not match:
        raise ValueError(f"Required registry field missing: {item.field_name}")
    return ParsedClaim(item.field_name, normalize_text(match.group(1), max_length=MAX_PARSED_TEXT), SourceProvenance.from_item(item))


def parse_source(item: SourceInventoryItem, content: str) -> ParsedClaim:
    if item.visibility is SourceVisibility.PROHIBITED:
        raise ValueError("Prohibited sources cannot be parsed")
    if item.kind in {SourceKind.BACKEND_OVERVIEW_JSON}:
        return parse_json_source(item, content)
    if item.kind in {
        SourceKind.STORY_MD,
        SourceKind.DESTINATION_MD,
        SourceKind.MARKET_STUDY_MD,
        SourceKind.MARKETING_MD,
        SourceKind.SEO_ARCHITECTURE_DOC,
    }:
        return parse_markdown_source(item, content)
    if item.kind in {SourceKind.FRONTEND_APP_REGISTRY, SourceKind.FRONTEND_ROUTE_REGISTRY}:
        return parse_registry_source(item, content)
    raise ValueError(f"Unsupported source type: {item.kind}")
