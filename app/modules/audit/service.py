import json
from typing import Any

from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.auth.models import User


def _serialize_metadata(metadata: Any) -> str | None:
    if metadata is None:
        return None

    try:
        return json.dumps(metadata, default=str, sort_keys=True)
    except (TypeError, ValueError):
        return json.dumps({"value": str(metadata)}, sort_keys=True)


def _get_request_ip(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None

    return request.client.host


def _get_request_user_agent(request: Request | None) -> str | None:
    if request is None:
        return None

    return request.headers.get("user-agent")


def write_audit_log(
    db: Session,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    entity_label: str | None = None,
    metadata: Any = None,
    request: Request | None = None,
    required: bool = False,
) -> AuditLog | None:
    audit_log = AuditLog(
        actor_user_id=actor.id if actor else None,
        actor_email=actor.email if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_label=entity_label,
        metadata_json=_serialize_metadata(metadata),
        ip_address=_get_request_ip(request),
        user_agent=_get_request_user_agent(request),
    )
    db.add(audit_log)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        if required:
            raise
        return None

    db.refresh(audit_log)

    return audit_log
