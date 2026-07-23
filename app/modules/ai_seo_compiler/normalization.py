"""Deterministic normalization helpers for isolated compiler output."""

from __future__ import annotations

import re
from enum import StrEnum
from urllib.parse import urlparse

MAX_TEXT = 2_000
ANSIVERSA_URL = "https://ansiversa.com"


def normalize_text(value: str, *, max_length: int = MAX_TEXT) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"<!--.*?-->", " ", normalized, flags=re.S)
    normalized = re.sub(r"```.*?```", " ", normalized, flags=re.S)
    normalized = re.sub(r"`([^`]+)`", r"\1", normalized)
    normalized = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"^[\s>*#-]+", "", normalized, flags=re.M)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:max_length]


def normalize_slug(value: str) -> str:
    normalized = value.strip().lower().replace("&", " and ").replace("+", " plus ")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized or len(normalized) > 100:
        raise ValueError("Invalid slug")
    return normalized


def normalize_route(value: str) -> str:
    route = value.strip()
    if route == "/":
        return route
    if not route.startswith("/") or route.startswith("//") or "?" in route or "#" in route:
        raise ValueError(f"Invalid public route: {value}")
    parts = [normalize_slug(part) for part in route.split("/") if part]
    return "/" + "/".join(parts)


def canonical_url(route: str) -> str:
    normalized = normalize_route(route)
    return ANSIVERSA_URL if normalized == "/" else f"{ANSIVERSA_URL}{normalized}"


def validate_canonical_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc != "ansiversa.com":
        raise ValueError(f"Invalid canonical URL: {value}")
    if parsed.params or parsed.query or parsed.fragment:
        raise ValueError(f"Canonical URL must not contain params, query, or fragment: {value}")
    return value.rstrip("/") if parsed.path == "/" else value


def normalize_enum(value: str, allowed: set[str]) -> str:
    normalized = normalize_slug(value).replace("-", "_")
    if normalized not in allowed:
        raise ValueError(f"Unsupported enum value: {value}")
    return normalized


def stable_list(values: list[str] | tuple[str, ...], *, lowercase: bool = False, max_items: int = 20) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        normalized = normalize_text(value)
        if lowercase:
            normalized = normalized.lower()
        if normalized and normalized not in result:
            result.append(normalized)
    return tuple(sorted(result)[:max_items])


def stable_id_fragment(value: str) -> str:
    return normalize_slug(value)[:80]


def enum_value(value: StrEnum | str) -> str:
    return value.value if isinstance(value, StrEnum) else str(value)
