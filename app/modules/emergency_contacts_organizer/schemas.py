from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ContactSort = Literal["priority", "name", "updated"]
FavouriteFilter = Literal["all", "favourites", "primary"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


def _normalize_phone(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _validate_phone(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    allowed = set("0123456789+()-. xX")
    digit_count = sum(1 for character in value if character.isdigit())
    if digit_count < 3 or any(character not in allowed for character in value):
        raise ValueError(f"{field_name} must be a valid phone value.")
    return value


class EmergencyContactCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=240)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EmergencyContactCategoryUpdateRequest(EmergencyContactCategoryCreateRequest):
    pass


class EmergencyContactCategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    contact_count: int = Field(serialization_alias="contactCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EmergencyContactCreateRequest(BaseModel):
    full_name: str = Field(alias="fullName", min_length=1, max_length=180)
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    relationship: str = Field(min_length=1, max_length=120)
    primary_phone: str = Field(alias="primaryPhone", min_length=3, max_length=60)
    alternate_phone: str | None = Field(default=None, alias="alternatePhone", max_length=60)
    email: EmailStr | None = Field(default=None, max_length=180)
    country_or_region: str | None = Field(default=None, alias="countryOrRegion", max_length=120)
    address: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=5000)
    priority: int = Field(default=50, ge=0, le=999)
    is_favourite: bool = Field(default=False, alias="isFavourite")
    is_primary: bool = Field(default=False, alias="isPrimary")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("full_name", "relationship", "country_or_region", "address", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("primary_phone", "alternate_phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        return _normalize_phone(value)

    @field_validator("primary_phone")
    @classmethod
    def validate_primary_phone(cls, value: str) -> str:
        return _validate_phone(value, "primaryPhone") or value

    @field_validator("alternate_phone")
    @classmethod
    def validate_alternate_phone(cls, value: str | None) -> str | None:
        return _validate_phone(value, "alternatePhone")


class EmergencyContactUpdateRequest(EmergencyContactCreateRequest):
    pass


class EmergencyContactSummaryResponse(BaseModel):
    id: str
    full_name: str = Field(serialization_alias="fullName")
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    relationship: str
    primary_phone: str = Field(serialization_alias="primaryPhone")
    alternate_phone: str | None = Field(serialization_alias="alternatePhone")
    email: str | None
    country_or_region: str | None = Field(serialization_alias="countryOrRegion")
    priority: int
    is_favourite: bool = Field(serialization_alias="isFavourite")
    is_primary: bool = Field(serialization_alias="isPrimary")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EmergencyContactDetailResponse(EmergencyContactSummaryResponse):
    address: str | None
    notes: str | None


class EmergencyContactCountItem(BaseModel):
    label: str
    count: int


class EmergencyContactDashboardResponse(BaseModel):
    total_contacts: int = Field(serialization_alias="totalContacts")
    favourite_contacts: int = Field(serialization_alias="favouriteContacts")
    primary_contacts: int = Field(serialization_alias="primaryContacts")
    missing_phone_contacts: int = Field(serialization_alias="missingPhoneContacts")
    missing_email_contacts: int = Field(serialization_alias="missingEmailContacts")


class EmergencyContactInsightsResponse(EmergencyContactDashboardResponse):
    categories: list[EmergencyContactCategoryResponse]
    category_distribution: list[EmergencyContactCountItem] = Field(serialization_alias="categoryDistribution")
    relationship_distribution: list[EmergencyContactCountItem] = Field(serialization_alias="relationshipDistribution")
    country_distribution: list[EmergencyContactCountItem] = Field(serialization_alias="countryDistribution")
    favourite_contacts_list: list[EmergencyContactSummaryResponse] = Field(serialization_alias="favouriteContactsList")
    recent_contacts: list[EmergencyContactSummaryResponse] = Field(serialization_alias="recentContacts")
