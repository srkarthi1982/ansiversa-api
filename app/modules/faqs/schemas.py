from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FaqResponse(BaseModel):
    id: str
    question: str
    answer: str
    answer_md: str | None = Field(default=None, serialization_alias="answerMd")
    app_key: str | None = Field(default=None, serialization_alias="appKey")
    audience: str
    category: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class PublicFaqListItemResponse(BaseModel):
    id: str
    question: str
    answer: str


class FaqListResponse(BaseModel):
    items: list[PublicFaqListItemResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total_pages: int = Field(serialization_alias="totalPages")
