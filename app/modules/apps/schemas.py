from datetime import datetime

from pydantic import BaseModel


class AppCatalogItemResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    category: str
    status: str
    launch_status: str
    visibility: str
    website_url: str | None
    admin_url: str | None
    logo_key: str | None
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppCatalogListResponse(BaseModel):
    items: list[AppCatalogItemResponse]
    total: int
