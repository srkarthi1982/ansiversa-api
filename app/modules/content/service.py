from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from time import monotonic

from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.content.models import Metadata

METADATA_CACHE_TTL_SECONDS = 300


@dataclass
class CachedMetadata:
  exists: bool
  content: dict | None
  expires_at: float


_metadata_cache: dict[str, CachedMetadata] = {}
_metadata_cache_lock = RLock()


def _copy_content(content: dict | None) -> dict | None:
  return deepcopy(content) if content is not None else None


def _read_cached_metadata(key: str) -> tuple[bool, dict | None] | None:
  now = monotonic()

  with _metadata_cache_lock:
    cached = _metadata_cache.get(key)
    if cached is None:
      return None
    if cached.expires_at <= now:
      _metadata_cache.pop(key, None)
      return None

    return cached.exists, _copy_content(cached.content)


def _write_cached_metadata(key: str, exists: bool, content: dict | None) -> None:
  with _metadata_cache_lock:
    _metadata_cache[key] = CachedMetadata(
      exists=exists,
      content=_copy_content(content),
      expires_at=monotonic() + METADATA_CACHE_TTL_SECONDS,
    )


def invalidate_metadata_cache(key: str | None = None) -> None:
  with _metadata_cache_lock:
    if key is None:
      _metadata_cache.clear()
      return

    _metadata_cache.pop(key, None)


def get_metadata(db: Session, key: str) -> Metadata | None:
  return db.get(Metadata, key)


def get_metadata_content(db: Session, key: str) -> dict | None:
  cached = _read_cached_metadata(key)
  if cached is not None:
    exists, content = cached
    return content if exists else None

  metadata = db.get(Metadata, key)
  if metadata is None:
    _write_cached_metadata(key, False, None)
    return None

  _write_cached_metadata(key, True, metadata.content)
  return _copy_content(metadata.content)


def list_metadata(db: Session) -> list[Metadata]:
  statement = select(Metadata).order_by(Metadata.key)

  return list(db.execute(statement).scalars().all())


def upsert_metadata(db: Session, key: str, content: dict | None) -> Metadata:
  existing = db.get(Metadata, key)
  if existing:
    existing.content = content
    db.add(existing)
    db.commit()
    db.refresh(existing)
    _write_cached_metadata(key, True, existing.content)

    return existing

  metadata = Metadata(key=key, content=content)
  db.add(metadata)
  try:
    db.commit()
  except Exception:
    db.rollback()
    raise

  db.refresh(metadata)
  _write_cached_metadata(key, True, metadata.content)
  return metadata


def delete_metadata(db: Session, key: str) -> None:
  existing = db.get(Metadata, key)
  if not existing:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

  db.delete(existing)
  db.commit()
  invalidate_metadata_cache(key)
