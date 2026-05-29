from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AdminUserResponse(BaseModel):
    id: str
    email: str
    role_id: int = Field(serialization_alias="roleId")


class AdminStatusResponse(BaseModel):
    status: str
    service: str
    admin: AdminUserResponse


AdminCategoryStatus = Literal["active", "disabled"]


class AdminCategoryResponse(BaseModel):
    id: str
    key: str | None
    slug: str
    name: str
    description: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    status: AdminCategoryStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    apps_count: int = Field(serialization_alias="appsCount")

    model_config = ConfigDict(from_attributes=True)


class AdminCategoryListResponse(BaseModel):
    items: list[AdminCategoryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total_pages: int = Field(serialization_alias="totalPages")
    sort: str
    dir: Literal["asc", "desc"]
    q: str
    status: str


class CreateCategoryRequest(BaseModel):
    id: str = Field(min_length=3)
    key: str | None = None
    name: str = Field(min_length=2)
    description: str | None = None
    sort_order: int | None = Field(default=None, validation_alias="sortOrder")
    status: str | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", "key", "name", "description", "status", mode="before")
    @classmethod
    def strip_string(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()

        return value


class UpdateCategoryRequest(BaseModel):
    key: str | None = None
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    sort_order: int | None = Field(default=None, validation_alias="sortOrder")
    status: str | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("key", "name", "description", "status", mode="before")
    @classmethod
    def strip_string(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()

        return value


class CategoryMutationResponse(BaseModel):
    ok: bool
    id: str


class DeleteCategoryResponse(BaseModel):
    ok: bool
