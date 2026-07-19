from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings


AssistantActionType = Literal["app", "platform", "account", "legal"]
AssistantSourceType = Literal["app", "platform", "account", "legal", "faq"]
AssistantConfidence = Literal["high", "medium", "low"]
AssistantResponseMode = Literal["deterministic", "openai_grounded", "fallback"]


class AssistantQueryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.AI_MAX_USER_MESSAGE_LENGTH)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("Message is required.")
        return message


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
    response_mode: AssistantResponseMode = Field(serialization_alias="responseMode")
