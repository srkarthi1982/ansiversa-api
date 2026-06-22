from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TemplateKey = Literal["classic", "modern", "minimal", "timeline"]
SectionKey = Literal[
    "profile",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class ResumeProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    template_key: TemplateKey = Field(default="classic", alias="templateKey")
    is_default: bool = Field(default=False, alias="isDefault")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResumeProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    template_key: TemplateKey | None = Field(default=None, alias="templateKey")
    is_default: bool | None = Field(default=None, alias="isDefault")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ResumeSectionCreateRequest(BaseModel):
    project_id: str = Field(alias="projectId", min_length=1, max_length=80)
    key: SectionKey
    order: int = Field(gt=0, le=1000)
    is_enabled: bool = Field(default=True, alias="isEnabled")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResumeSectionUpdateRequest(BaseModel):
    key: SectionKey | None = None
    order: int | None = Field(default=None, gt=0, le=1000)
    is_enabled: bool | None = Field(default=None, alias="isEnabled")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResumeItemCreateRequest(BaseModel):
    section_id: str = Field(alias="sectionId", min_length=1, max_length=80)
    order: int = Field(gt=0, le=1000)
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResumeItemUpdateRequest(BaseModel):
    section_id: str | None = Field(default=None, alias="sectionId", min_length=1, max_length=80)
    order: int | None = Field(default=None, gt=0, le=1000)
    data: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResumeProjectResponse(BaseModel):
    id: str
    title: str
    template_key: str = Field(serialization_alias="templateKey")
    is_default: bool = Field(serialization_alias="isDefault")
    section_count: int = Field(serialization_alias="sectionCount")
    item_count: int = Field(serialization_alias="itemCount")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResumeProjectListResponse(BaseModel):
    items: list[ResumeProjectResponse]


class ResumeSectionResponse(BaseModel):
    id: str
    project_id: str = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    key: str
    order: int
    is_enabled: bool = Field(serialization_alias="isEnabled")
    item_count: int = Field(serialization_alias="itemCount")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResumeSectionListResponse(BaseModel):
    items: list[ResumeSectionResponse]


class ResumeItemResponse(BaseModel):
    id: str
    project_id: str = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    section_id: str = Field(serialization_alias="sectionId")
    section_key: str = Field(serialization_alias="sectionKey")
    order: int
    data: dict[str, Any]
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ResumeItemListResponse(BaseModel):
    items: list[ResumeItemResponse]


class ResumeBuilderReviewResponse(BaseModel):
    project_count: int = Field(serialization_alias="projectCount")
    default_project_count: int = Field(serialization_alias="defaultProjectCount")
    enabled_section_count: int = Field(serialization_alias="enabledSectionCount")
    item_count: int = Field(serialization_alias="itemCount")
    completion_rate: int = Field(serialization_alias="completionRate")
    ready_project_count: int = Field(serialization_alias="readyProjectCount")
    recent_items: list[ResumeItemResponse] = Field(serialization_alias="recentItems")


class ResumePreviewSectionResponse(BaseModel):
    section: ResumeSectionResponse
    items: list[ResumeItemResponse]


class ResumePreviewResponse(BaseModel):
    project: ResumeProjectResponse | None
    sections: list[ResumePreviewSectionResponse]


class ResumeBuilderDashboardResponse(BaseModel):
    projects: list[ResumeProjectResponse]
    sections: list[ResumeSectionResponse]
    items: list[ResumeItemResponse]
    preview: ResumePreviewResponse
    review: ResumeBuilderReviewResponse
