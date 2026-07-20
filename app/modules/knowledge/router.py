"""Public AI knowledge artifact routes."""

from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter
from starlette.responses import Response

from app.modules.knowledge.publisher import (
    _serialized_json,
    build_public_artifacts,
)

router = APIRouter()

PUBLIC_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600",
    "Access-Control-Allow-Origin": "*",
    "X-Robots-Tag": "index, follow",
}


@lru_cache(maxsize=1)
def _artifact_payloads() -> dict[str, str]:
    artifacts = build_public_artifacts()
    return {
        "llms": artifacts.llms,
        "llms-full": artifacts.llms_full,
        "sitemap": artifacts.sitemap,
        "knowledge": _serialized_json(artifacts.knowledge),
        "jsonld": _serialized_json(artifacts.jsonld),
        "metadata": _serialized_json(artifacts.metadata),
        "robots": artifacts.robots,
    }


def _artifact(name: str, media_type: str) -> Response:
    return Response(
        content=_artifact_payloads()[name],
        media_type=media_type,
        headers=PUBLIC_CACHE_HEADERS,
    )


@router.get("/llms.txt", include_in_schema=False)
def get_llms_txt() -> Response:
    return _artifact("llms", "text/plain; charset=utf-8")


@router.get("/llms-full.txt", include_in_schema=False)
def get_llms_full_txt() -> Response:
    return _artifact("llms-full", "text/plain; charset=utf-8")


@router.get("/ai-sitemap.xml", include_in_schema=False)
def get_ai_sitemap_xml() -> Response:
    return _artifact("sitemap", "application/xml; charset=utf-8")


@router.get("/public-ai-knowledge.json", include_in_schema=False)
def get_public_ai_knowledge_json() -> Response:
    return _artifact("knowledge", "application/json; charset=utf-8")


@router.get("/public-ai-jsonld.json", include_in_schema=False)
def get_public_ai_jsonld_json() -> Response:
    return _artifact("jsonld", "application/ld+json; charset=utf-8")


@router.get("/public-ai-metadata.json", include_in_schema=False)
def get_public_ai_metadata_json() -> Response:
    return _artifact("metadata", "application/json; charset=utf-8")


@router.get("/robots.txt", include_in_schema=False)
def get_robots_txt() -> Response:
    return _artifact("robots", "text/plain; charset=utf-8")


api_router = APIRouter()


@api_router.get("/public")
def get_public_knowledge() -> Response:
    return _artifact("knowledge", "application/json; charset=utf-8")


@api_router.get("/public/jsonld")
def get_public_jsonld() -> Response:
    return _artifact("jsonld", "application/ld+json; charset=utf-8")


@api_router.get("/public/metadata")
def get_public_metadata() -> Response:
    return _artifact("metadata", "application/json; charset=utf-8")
