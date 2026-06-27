from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PortfolioProfileStatus = Literal["draft", "published", "archived"]
PortfolioProjectStatus = Literal["draft", "featured", "hidden"]
PortfolioSkillCategory = Literal["technical", "tool", "language", "soft", "domain"]
PortfolioSkillProficiency = Literal["beginner", "intermediate", "advanced", "expert"]
PortfolioVisibility = Literal["private", "unlisted", "public"]
PortfolioTheme = Literal["classic", "compact", "modern"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class PortfolioProfileCreateRequest(BaseModel):
    display_name: str = Field(alias="displayName", min_length=1, max_length=140)
    headline: str = Field(min_length=1, max_length=180)
    summary: str | None = Field(default=None, max_length=3000)
    location: str | None = Field(default=None, max_length=140)
    website_url: str | None = Field(default=None, alias="websiteUrl", max_length=240)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("display_name", "headline", "summary", "location", "website_url", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, alias="displayName", min_length=1, max_length=140)
    headline: str | None = Field(default=None, min_length=1, max_length=180)
    summary: str | None = Field(default=None, max_length=3000)
    location: str | None = Field(default=None, max_length=140)
    website_url: str | None = Field(default=None, alias="websiteUrl", max_length=240)
    status: PortfolioProfileStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("display_name", "headline", "summary", "location", "website_url", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioProjectCreateRequest(BaseModel):
    profile_id: int = Field(alias="profileId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=4000)
    project_url: str | None = Field(default=None, alias="projectUrl", max_length=240)
    role: str | None = Field(default=None, max_length=140)
    position: int = Field(default=1, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "project_url", "role", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioProjectUpdateRequest(BaseModel):
    profile_id: int | None = Field(default=None, alias="profileId", gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=4000)
    project_url: str | None = Field(default=None, alias="projectUrl", max_length=240)
    role: str | None = Field(default=None, max_length=140)
    position: int | None = Field(default=None, gt=0, le=200)
    status: PortfolioProjectStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "description", "project_url", "role", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioSkillCreateRequest(BaseModel):
    profile_id: int = Field(alias="profileId", gt=0)
    name: str = Field(min_length=1, max_length=120)
    category: PortfolioSkillCategory = "technical"
    proficiency: PortfolioSkillProficiency = "intermediate"
    position: int = Field(default=1, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioSkillUpdateRequest(BaseModel):
    profile_id: int | None = Field(default=None, alias="profileId", gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: PortfolioSkillCategory | None = None
    proficiency: PortfolioSkillProficiency | None = None
    position: int | None = Field(default=None, gt=0, le=200)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioPublishSettingCreateRequest(BaseModel):
    profile_id: int = Field(alias="profileId", gt=0)
    visibility: PortfolioVisibility = "private"
    slug: str = Field(min_length=1, max_length=120)
    theme: PortfolioTheme = "classic"
    is_published: bool = Field(default=False, alias="isPublished")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioPublishSettingUpdateRequest(BaseModel):
    profile_id: int | None = Field(default=None, alias="profileId", gt=0)
    visibility: PortfolioVisibility | None = None
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    theme: PortfolioTheme | None = None
    is_published: bool | None = Field(default=None, alias="isPublished")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PortfolioProfileResponse(BaseModel):
    id: int
    display_name: str = Field(serialization_alias="displayName")
    headline: str
    summary: str | None
    location: str | None
    website_url: str | None = Field(serialization_alias="websiteUrl")
    status: PortfolioProfileStatus
    project_count: int = Field(serialization_alias="projectCount")
    skill_count: int = Field(serialization_alias="skillCount")
    publish_count: int = Field(serialization_alias="publishCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PortfolioProfileListResponse(BaseModel):
    items: list[PortfolioProfileResponse]


class PortfolioProjectResponse(BaseModel):
    id: int
    profile_id: int = Field(serialization_alias="profileId")
    profile_name: str = Field(serialization_alias="profileName")
    title: str
    description: str | None
    project_url: str | None = Field(serialization_alias="projectUrl")
    role: str | None
    position: int
    status: PortfolioProjectStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PortfolioProjectListResponse(BaseModel):
    items: list[PortfolioProjectResponse]


class PortfolioSkillResponse(BaseModel):
    id: int
    profile_id: int = Field(serialization_alias="profileId")
    profile_name: str = Field(serialization_alias="profileName")
    name: str
    category: PortfolioSkillCategory
    proficiency: PortfolioSkillProficiency
    position: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PortfolioSkillListResponse(BaseModel):
    items: list[PortfolioSkillResponse]


class PortfolioPublishSettingResponse(BaseModel):
    id: int
    profile_id: int = Field(serialization_alias="profileId")
    profile_name: str = Field(serialization_alias="profileName")
    visibility: PortfolioVisibility
    slug: str
    theme: PortfolioTheme
    is_published: bool = Field(serialization_alias="isPublished")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PortfolioPublishSettingListResponse(BaseModel):
    items: list[PortfolioPublishSettingResponse]


class PortfolioCreatorDashboardResponse(BaseModel):
    profiles: list[PortfolioProfileResponse]
    projects: list[PortfolioProjectResponse]
    skills: list[PortfolioSkillResponse]
    publish_settings: list[PortfolioPublishSettingResponse] = Field(
        serialization_alias="publishSettings"
    )
    draft_profile_count: int = Field(serialization_alias="draftProfileCount")
    published_profile_count: int = Field(serialization_alias="publishedProfileCount")
    featured_project_count: int = Field(serialization_alias="featuredProjectCount")
    published_portfolio_count: int = Field(serialization_alias="publishedPortfolioCount")
