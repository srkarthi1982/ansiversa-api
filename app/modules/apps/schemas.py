from datetime import datetime

from pydantic import BaseModel


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


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int


class AppCatalogItemResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    category_id: str
    status: str
    version: str
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


class AppCatalogListResponse(BaseModel):
    items: list[AppCatalogItemResponse]
    total: int
