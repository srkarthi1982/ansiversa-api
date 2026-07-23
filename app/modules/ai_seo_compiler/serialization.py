"""Deterministic serialization helpers for isolated compiler tests."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()
