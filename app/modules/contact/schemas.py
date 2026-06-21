from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactMessageCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr = Field(max_length=255)
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)

    @field_validator("name", "subject", mode="before")
    @classmethod
    def normalize_single_line_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        return " ".join(value.strip().split())

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        return value.strip().lower()


class ContactMessageResponse(BaseModel):
    id: str
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)
