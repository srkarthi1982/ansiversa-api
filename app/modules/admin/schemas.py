from pydantic import BaseModel, Field


class AdminUserResponse(BaseModel):
    id: str
    email: str
    role_id: int = Field(serialization_alias="roleId")


class AdminStatusResponse(BaseModel):
    status: str
    service: str
    admin: AdminUserResponse
