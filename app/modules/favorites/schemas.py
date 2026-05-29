from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FavoriteAppResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    status: str
    launch_status: str = Field(serialization_alias="launchStatus")
    visibility: str
    pricing_gate: str = Field(serialization_alias="pricingGate")
    website_url: str | None = Field(default=None, serialization_alias="websiteUrl")
    logo_key: str | None = Field(default=None, serialization_alias="logoKey")

    model_config = ConfigDict(from_attributes=True)


class FavoriteResponse(BaseModel):
    favorite_id: str = Field(serialization_alias="favoriteId")
    created_at: datetime = Field(serialization_alias="createdAt")
    app: FavoriteAppResponse


class FavoriteListResponse(BaseModel):
    items: list[FavoriteResponse]
    total: int


class AddFavoriteRequest(BaseModel):
    app_id: str = Field(min_length=1, validation_alias="appId")

    model_config = ConfigDict(populate_by_name=True)


class AddFavoriteResponse(FavoriteResponse):
    pass


class RemoveFavoriteResponse(BaseModel):
    ok: bool
    app_id: str = Field(serialization_alias="appId")
