from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthStatusResponse(BaseModel):
    status: str
    service: str
    auth_ready: bool
    message: str


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=2, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Enter a valid email address.")

        return normalized

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("Name is required.")

        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    ok: bool


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role_id: int = Field(serialization_alias="roleId")
    status: str
    plan: str | None = None
    plan_status: str | None = Field(default=None, serialization_alias="planStatus")
    country_code: str | None = Field(default=None, serialization_alias="countryCode")
    region_code: str | None = Field(default=None, serialization_alias="regionCode")
    city: str | None = None
    timezone: str | None = None
    avatar_url: str | None = Field(default=None, serialization_alias="avatarUrl")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(UserResponse):
    pass


# Backward-compatible import name for early API code paths.
UserCreate = RegisterRequest
