from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class LinkedInProfileCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    career_level: str | None = Field(default=None, alias="careerLevel", max_length=80)
    target_role: str | None = Field(default=None, alias="targetRole", max_length=180)
    current_headline: str | None = Field(default=None, alias="currentHeadline", max_length=220)
    current_bio: str | None = Field(default=None, alias="currentBio", max_length=6000)
    optimized_bio: str | None = Field(default=None, alias="optimizedBio", max_length=6000)
    keywords: str | None = Field(default=None, max_length=2000)
    tone: str | None = Field(default=None, max_length=80)
    language: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LinkedInProfileUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    career_level: str | None = Field(default=None, alias="careerLevel", max_length=80)
    target_role: str | None = Field(default=None, alias="targetRole", max_length=180)
    current_headline: str | None = Field(default=None, alias="currentHeadline", max_length=220)
    current_bio: str | None = Field(default=None, alias="currentBio", max_length=6000)
    optimized_bio: str | None = Field(default=None, alias="optimizedBio", max_length=6000)
    keywords: str | None = Field(default=None, max_length=2000)
    tone: str | None = Field(default=None, max_length=80)
    language: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BioTemplateCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    name: str = Field(min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    career_level: str | None = Field(default=None, alias="careerLevel", max_length=80)
    template: str = Field(min_length=1, max_length=6000)
    is_default: bool = Field(default=False, alias="isDefault")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "name", "industry", "career_level", "template", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BioTemplateUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    career_level: str | None = Field(default=None, alias="careerLevel", max_length=80)
    template: str | None = Field(default=None, min_length=1, max_length=6000)
    is_default: bool | None = Field(default=None, alias="isDefault")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "name", "industry", "career_level", "template", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class BioVersionCreateRequest(BaseModel):
    profile_id: int = Field(alias="profileId", gt=0)
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    version_number: int | None = Field(default=None, alias="versionNumber", gt=0)
    headline: str | None = Field(default=None, max_length=220)
    bio: str = Field(min_length=1, max_length=6000)
    change_summary: str | None = Field(default=None, alias="changeSummary", max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("platform_id", "headline", "bio", "change_summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LinkedInProfileSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    industry: str | None
    career_level: str | None = Field(serialization_alias="careerLevel")
    target_role: str | None = Field(serialization_alias="targetRole")
    current_headline: str | None = Field(serialization_alias="currentHeadline")
    optimized_bio_preview: str | None = Field(serialization_alias="optimizedBioPreview")
    keywords_preview: str | None = Field(serialization_alias="keywordsPreview")
    tone: str | None
    language: str | None
    version_count: int = Field(serialization_alias="versionCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class LinkedInProfileDetailResponse(LinkedInProfileSummaryResponse):
    current_bio: str | None = Field(serialization_alias="currentBio")
    optimized_bio: str | None = Field(serialization_alias="optimizedBio")
    keywords: str | None
    notes: str | None


class BioTemplateSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    name: str
    industry: str | None
    career_level: str | None = Field(serialization_alias="careerLevel")
    template_preview: str | None = Field(serialization_alias="templatePreview")
    is_default: bool = Field(serialization_alias="isDefault")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class BioTemplateDetailResponse(BioTemplateSummaryResponse):
    template: str


class BioVersionSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    profile_id: int = Field(serialization_alias="profileId")
    profile_title: str = Field(serialization_alias="profileTitle")
    version_number: int = Field(serialization_alias="versionNumber")
    headline: str | None
    bio_preview: str | None = Field(serialization_alias="bioPreview")
    change_summary_preview: str | None = Field(serialization_alias="changeSummaryPreview")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class BioVersionDetailResponse(BioVersionSummaryResponse):
    bio: str
    change_summary: str | None = Field(serialization_alias="changeSummary")


class LinkedInBioOptimizerDashboardResponse(BaseModel):
    profiles: list[LinkedInProfileSummaryResponse]
    templates: list[BioTemplateSummaryResponse]
    versions: list[BioVersionSummaryResponse]
    profile_count: int = Field(serialization_alias="profileCount")
    template_count: int = Field(serialization_alias="templateCount")
    version_count: int = Field(serialization_alias="versionCount")
    optimized_profile_count: int = Field(serialization_alias="optimizedProfileCount")

    model_config = ConfigDict(from_attributes=True)
