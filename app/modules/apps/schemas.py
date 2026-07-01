from datetime import datetime

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    id: str
    key: str | None
    slug: str
    name: str
    description: str | None
    sort_order: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryCatalogListItemResponse(BaseModel):
    id: str
    name: str
    description: str | None


class CategoryListResponse(BaseModel):
    items: list[CategoryCatalogListItemResponse]
    total: int


class AppCatalogItemResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    category_id: str
    status: str
    version: str | None
    is_featured: bool
    website_url: str | None
    admin_url: str | None
    created_at: datetime
    updated_at: datetime
    capabilities: str | None
    launch_status: str
    visibility: str
    pricing_gate: str
    logo_key: str | None

    model_config = {"from_attributes": True}


class AppCatalogListItemResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    category_id: str
    status: str
    launch_status: str


class AppCatalogListResponse(BaseModel):
    items: list[AppCatalogListItemResponse]
    total: int


class AppCatalogCountsResponse(BaseModel):
    total: int
    live: int
    coming_soon: int = Field(serialization_alias="comingSoon")


class AppCatalogResponse(BaseModel):
    apps: list[AppCatalogListItemResponse]
    categories: list[CategoryCatalogListItemResponse]
    counts: AppCatalogCountsResponse
