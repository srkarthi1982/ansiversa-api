import re

from fastapi.routing import APIRoute


def _normalize_operation_part(value: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z_]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")

    if not normalized:
        return "operation"

    if normalized[0].isdigit():
        return f"op_{normalized}"

    return normalized


def generate_operation_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    name = route.name or "operation"
    methods = sorted(
        method.lower()
        for method in route.methods
        if method not in {"HEAD", "OPTIONS"}
    )
    method = methods[0] if methods else "request"

    parts = [
        _normalize_operation_part(tag),
        _normalize_operation_part(name),
        _normalize_operation_part(method),
    ]

    return "_".join(parts)
