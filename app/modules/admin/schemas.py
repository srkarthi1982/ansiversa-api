from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AdminStatusUserResponse(BaseModel):
    id: str
    email: str
    role_id: int = Field(serialization_alias="roleId")


class AdminStatusResponse(BaseModel):
    status: str
    service: str
    admin: AdminStatusUserResponse


AdminUserStatus = Literal["active", "disabled"]


class AdminUserRoleResponse(BaseModel):
    id: int
    name: str | None
    key: str | None

    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    id: str
    email: str
    name: str
    role_id: int = Field(serialization_alias="roleId")
    role: AdminUserRoleResponse | None
    role_name: str | None = Field(default=None, serialization_alias="roleName")
    status: AdminUserStatus
    plan: str | None
    plan_status: str | None = Field(serialization_alias="planStatus")
    country_code: str | None = Field(serialization_alias="countryCode")
    region_code: str | None = Field(serialization_alias="regionCode")
    city: str | None
    timezone: str | None
    location_source: str = Field(serialization_alias="locationSource")
    location_captured_at: datetime | None = Field(serialization_alias="locationCapturedAt")
    avatar_url: str | None = Field(serialization_alias="avatarUrl")
    avatar_updated_at: datetime | None = Field(serialization_alias="avatarUpdatedAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total_pages: int = Field(serialization_alias="totalPages")
    sort: str
    dir: Literal["asc", "desc"]
    q: str
    status: str
    role_id: int | str = Field(serialization_alias="roleId")
    plan: str
    plan_status: str = Field(serialization_alias="planStatus")
    country_code: str = Field(serialization_alias="countryCode")


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


AdminAppStatus = Literal["alpha", "beta", "live", "archived", "coming-soon"]
AdminAppLaunchStatus = Literal["live", "beta", "comingSoon", "disabled"]
AdminAppVisibility = Literal["public", "private", "internal"]
AdminAppPricingGate = Literal["free", "pro"]


class AdminAppResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str | None
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str | None = Field(default=None, serialization_alias="categoryName")
    status: AdminAppStatus
    launch_status: AdminAppLaunchStatus = Field(serialization_alias="launchStatus")
    visibility: AdminAppVisibility
    pricing_gate: AdminAppPricingGate = Field(serialization_alias="pricingGate")
    is_featured: bool = Field(serialization_alias="isFeatured")
    website_url: str | None = Field(serialization_alias="websiteUrl")
    admin_url: str | None = Field(serialization_alias="adminUrl")
    logo_key: str | None = Field(serialization_alias="logoKey")
    capabilities: list[str]
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class AdminAppListResponse(BaseModel):
    items: list[AdminAppResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total_pages: int = Field(serialization_alias="totalPages")
    sort: str
    dir: Literal["asc", "desc"]
    q: str
    category_id: str = Field(serialization_alias="categoryId")
    status: str
    launch_status: str = Field(serialization_alias="launchStatus")
    visibility: str
    pricing_gate: str = Field(serialization_alias="pricingGate")
    featured_only: bool = Field(serialization_alias="featuredOnly")


class AdminAppsMetaCategoryResponse(BaseModel):
    id: str
    name: str


class AdminAppsMetaCapabilityResponse(BaseModel):
    key: str
    label: str
    icon: str
    order: int


class AdminAppsMetaResponse(BaseModel):
    categories: list[AdminAppsMetaCategoryResponse]
    allowed_statuses: list[str] = Field(serialization_alias="allowedStatuses")
    allowed_launch_statuses: list[str] = Field(serialization_alias="allowedLaunchStatuses")
    allowed_visibility_values: list[str] = Field(serialization_alias="allowedVisibilityValues")
    allowed_pricing_gates: list[str] = Field(serialization_alias="allowedPricingGates")
    capability_options: list[AdminAppsMetaCapabilityResponse] = Field(serialization_alias="capabilityOptions")


class CreateAppRequest(BaseModel):
    name: str = Field(min_length=2)
    key: str = Field(min_length=2)
    slug: str = Field(min_length=2)
    category_id: str = Field(validation_alias="categoryId", min_length=1)
    description: str | None = None
    status: str | None = None
    is_featured: bool | None = Field(default=None, validation_alias="isFeatured")
    website_url: str | None = Field(default=None, validation_alias="websiteUrl")
    admin_url: str | None = Field(default=None, validation_alias="adminUrl")
    capabilities: list[str] | None = None
    launch_status: str | None = Field(default=None, validation_alias="launchStatus")
    visibility: str | None = None
    pricing_gate: str | None = Field(default=None, validation_alias="pricingGate")
    logo_key: str | None = Field(default=None, validation_alias="logoKey")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "name",
        "key",
        "slug",
        "category_id",
        "description",
        "status",
        "website_url",
        "admin_url",
        "launch_status",
        "visibility",
        "pricing_gate",
        "logo_key",
        mode="before",
    )
    @classmethod
    def strip_app_string(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()

        return value


class UpdateAppRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    key: str | None = Field(default=None, min_length=2)
    slug: str | None = Field(default=None, min_length=2)
    category_id: str | None = Field(default=None, validation_alias="categoryId")
    description: str | None = None
    status: str | None = None
    is_featured: bool | None = Field(default=None, validation_alias="isFeatured")
    website_url: str | None = Field(default=None, validation_alias="websiteUrl")
    admin_url: str | None = Field(default=None, validation_alias="adminUrl")
    capabilities: list[str] | None = None
    launch_status: str | None = Field(default=None, validation_alias="launchStatus")
    visibility: str | None = None
    pricing_gate: str | None = Field(default=None, validation_alias="pricingGate")
    logo_key: str | None = Field(default=None, validation_alias="logoKey")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "name",
        "key",
        "slug",
        "category_id",
        "description",
        "status",
        "website_url",
        "admin_url",
        "launch_status",
        "visibility",
        "pricing_gate",
        "logo_key",
        mode="before",
    )
    @classmethod
    def strip_app_string(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()

        return value


class AppMutationResponse(BaseModel):
    ok: bool
    id: str


class DeleteAppResponse(BaseModel):
    ok: bool
