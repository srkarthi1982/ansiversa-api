from copy import deepcopy

from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.content.models import Metadata


def _copy_content(content: dict | None) -> dict | None:
  return deepcopy(content) if content is not None else None


def get_metadata(db: Session, key: str) -> Metadata | None:
  return db.get(Metadata, key)


def get_metadata_content(db: Session, key: str) -> dict | None:
  metadata = db.get(Metadata, key)
  if metadata is None:
    return None

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

    return existing

  metadata = Metadata(key=key, content=content)
  db.add(metadata)
  try:
    db.commit()
  except Exception:
    db.rollback()
    raise

  db.refresh(metadata)
  return metadata


def delete_metadata(db: Session, key: str) -> None:
  existing = db.get(Metadata, key)
  if not existing:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

  db.delete(existing)
  db.commit()
