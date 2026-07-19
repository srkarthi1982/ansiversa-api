from typing import Literal

from pydantic import BaseModel, Field


AssistantActionType = Literal["app", "platform", "account", "legal"]
AssistantSourceType = Literal["app", "platform", "account", "legal", "faq"]
AssistantConfidence = Literal["high", "medium", "low"]


class AssistantQueryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AssistantAction(BaseModel):
    type: AssistantActionType
    label: str
    route: str


class AssistantSource(BaseModel):
    id: str
    title: str
    type: AssistantSourceType


class AssistantQueryResponse(BaseModel):
    answer: str
    actions: list[AssistantAction]
    sources: list[AssistantSource]
    confidence: AssistantConfidence
