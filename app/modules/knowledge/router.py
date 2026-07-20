"""Public AI knowledge artifact routes."""

from __future__ import annotations

from fastapi import APIRouter
from starlette.responses import FileResponse

from app.modules.knowledge.publisher import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    PUBLIC_AI_JSONLD_PATH,
    PUBLIC_AI_KNOWLEDGE_PATH,
    PUBLIC_AI_METADATA_PATH,
    PUBLIC_AI_SITEMAP_PATH,
    ROBOTS_PATH,
)

router = APIRouter()

PUBLIC_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600",
    "X-Robots-Tag": "index, follow",
}


def _file(path, media_type: str) -> FileResponse:
    return FileResponse(path, media_type=media_type, headers=PUBLIC_CACHE_HEADERS)


@router.get("/llms.txt", include_in_schema=False)
def get_llms_txt() -> FileResponse:
    return _file(LLMS_PATH, "text/plain; charset=utf-8")


@router.get("/llms-full.txt", include_in_schema=False)
def get_llms_full_txt() -> FileResponse:
    return _file(LLMS_FULL_PATH, "text/plain; charset=utf-8")


@router.get("/ai-sitemap.xml", include_in_schema=False)
def get_ai_sitemap_xml() -> FileResponse:
    return _file(PUBLIC_AI_SITEMAP_PATH, "application/xml; charset=utf-8")


@router.get("/public-ai-knowledge.json", include_in_schema=False)
def get_public_ai_knowledge_json() -> FileResponse:
    return _file(PUBLIC_AI_KNOWLEDGE_PATH, "application/json; charset=utf-8")


@router.get("/public-ai-jsonld.json", include_in_schema=False)
def get_public_ai_jsonld_json() -> FileResponse:
    return _file(PUBLIC_AI_JSONLD_PATH, "application/ld+json; charset=utf-8")


@router.get("/public-ai-metadata.json", include_in_schema=False)
def get_public_ai_metadata_json() -> FileResponse:
    return _file(PUBLIC_AI_METADATA_PATH, "application/json; charset=utf-8")


@router.get("/robots.txt", include_in_schema=False)
def get_robots_txt() -> FileResponse:
    return _file(ROBOTS_PATH, "text/plain; charset=utf-8")


api_router = APIRouter()


@api_router.get("/public")
def get_public_knowledge() -> FileResponse:
    return _file(PUBLIC_AI_KNOWLEDGE_PATH, "application/json; charset=utf-8")


@api_router.get("/public/jsonld")
def get_public_jsonld() -> FileResponse:
    return _file(PUBLIC_AI_JSONLD_PATH, "application/ld+json; charset=utf-8")


@api_router.get("/public/metadata")
def get_public_metadata() -> FileResponse:
    return _file(PUBLIC_AI_METADATA_PATH, "application/json; charset=utf-8")
