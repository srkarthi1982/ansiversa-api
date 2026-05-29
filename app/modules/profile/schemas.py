from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.auth.schemas import CurrentUserResponse


class ProfileResponse(CurrentUserResponse):
    pass


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    country_code: str | None = Field(default=None, max_length=20, validation_alias="countryCode")
    region_code: str | None = Field(default=None, max_length=120, validation_alias="regionCode")
    city: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=120)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if value is None:
            return value
        if not isinstance(value, str):
            return value

        return " ".join(value.strip().split())

    @field_validator("country_code", "region_code", "city", "timezone", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        trimmed = value.strip()
        return trimmed or None

    model_config = ConfigDict(populate_by_name=True)


class PreferencesResponse(BaseModel):
    user_id: str = Field(serialization_alias="userId")
    product_updates: bool = Field(serialization_alias="productUpdates")
    security_alerts: bool = Field(serialization_alias="securityAlerts")
    theme: Literal["system", "light", "dark"] | None
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PreferencesUpdateRequest(BaseModel):
    product_updates: bool = Field(validation_alias="productUpdates")
    security_alerts: bool = Field(validation_alias="securityAlerts")
    theme: Literal["system", "light", "dark"] | None = None

    model_config = ConfigDict(populate_by_name=True)
