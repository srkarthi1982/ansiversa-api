from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CardTemplateKey = Literal["professional", "minimal", "modern"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        return value.strip()

    return value


class CardProfileBaseRequest(BaseModel):
    full_name: str = Field(alias="fullName", min_length=1, max_length=120)
    job_title: str = Field(default="", alias="jobTitle", max_length=120)
    company_name: str = Field(default="", alias="companyName", max_length=140)
    phone_number: str = Field(default="", alias="phoneNumber", max_length=60)
    email: str = Field(default="", max_length=180)
    website: str = Field(default="", max_length=180)
    address: str = Field(default="", max_length=500)
    tagline: str = Field(default="", max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "full_name",
        "job_title",
        "company_name",
        "phone_number",
        "email",
        "website",
        "address",
        "tagline",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CardCreateRequest(CardProfileBaseRequest):
    template_key: CardTemplateKey = Field(default="professional", alias="templateKey")


class CardUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, alias="fullName", min_length=1, max_length=120)
    job_title: str | None = Field(default=None, alias="jobTitle", max_length=120)
    company_name: str | None = Field(default=None, alias="companyName", max_length=140)
    phone_number: str | None = Field(default=None, alias="phoneNumber", max_length=60)
    email: str | None = Field(default=None, max_length=180)
    website: str | None = Field(default=None, max_length=180)
    address: str | None = Field(default=None, max_length=500)
    tagline: str | None = Field(default=None, max_length=180)
    template_key: CardTemplateKey | None = Field(default=None, alias="templateKey")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator(
        "full_name",
        "job_title",
        "company_name",
        "phone_number",
        "email",
        "website",
        "address",
        "tagline",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CardProfileResponse(BaseModel):
    id: str
    full_name: str = Field(serialization_alias="fullName")
    job_title: str = Field(serialization_alias="jobTitle")
    company_name: str = Field(serialization_alias="companyName")
    phone_number: str = Field(serialization_alias="phoneNumber")
    email: str
    website: str
    address: str
    tagline: str
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CardDesignResponse(BaseModel):
    id: str
    profile_id: str = Field(serialization_alias="profileId")
    template_key: CardTemplateKey = Field(serialization_alias="templateKey")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class VisitingCardResponse(BaseModel):
    id: str
    profile: CardProfileResponse
    design: CardDesignResponse
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")


class VisitingCardListResponse(BaseModel):
    items: list[VisitingCardResponse]


class VisitingCardMakerDashboardResponse(BaseModel):
    cards: list[VisitingCardResponse]
    selected_card: VisitingCardResponse | None = Field(serialization_alias="selectedCard")
