from pydantic import BaseModel, ConfigDict, Field


class QuizTaxonomyItemResponse(BaseModel):
    id: int
    name: str
    is_active: bool = Field(serialization_alias="isActive")
    question_count: int = Field(serialization_alias="qCount")

    model_config = ConfigDict(from_attributes=True)


class QuizPlatformResponse(QuizTaxonomyItemResponse):
    description: str
    type: str | None


class QuizSubjectResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")


class QuizTopicResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")
    subject_id: int = Field(serialization_alias="subjectId")


class QuizRoadmapResponse(QuizTaxonomyItemResponse):
    platform_id: int = Field(serialization_alias="platformId")
    subject_id: int = Field(serialization_alias="subjectId")
    topic_id: int = Field(serialization_alias="topicId")


class QuizPlatformListResponse(BaseModel):
    items: list[QuizPlatformResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizSubjectListResponse(BaseModel):
    items: list[QuizSubjectResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizTopicListResponse(BaseModel):
    items: list[QuizTopicResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class QuizRoadmapListResponse(BaseModel):
    items: list[QuizRoadmapResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
