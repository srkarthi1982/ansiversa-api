from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    id: str
    actor_user_id: str | None = Field(default=None, serialization_alias="actorUserId")
    actor_email: str | None = Field(default=None, serialization_alias="actorEmail")
    action: str
    entity_type: str = Field(serialization_alias="entityType")
    entity_id: str | None = Field(default=None, serialization_alias="entityId")
    entity_label: str | None = Field(default=None, serialization_alias="entityLabel")
    metadata_json: str | None = Field(default=None, serialization_alias="metadataJson")
    ip_address: str | None = Field(default=None, serialization_alias="ipAddress")
    user_agent: str | None = Field(default=None, serialization_alias="userAgent")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)
