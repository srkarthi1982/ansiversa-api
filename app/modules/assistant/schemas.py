from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings


AssistantActionType = Literal["app", "platform", "account", "legal"]
AssistantSourceType = Literal["app", "platform", "account", "legal", "faq"]
AssistantConfidence = Literal["high", "medium", "low"]
AssistantResponseMode = Literal["deterministic", "openai_grounded", "fallback"]


class AssistantContextApp(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    key: str | None = None
    slug: str | None = None
    name: str | None = None
    category: str | None = None
    route: str | None = None


class AssistantContextHistoryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_message: str = Field(alias="userMessage", max_length=500)
    assistant_answer: str = Field(alias="assistantAnswer", max_length=1000)
    selected_action_label: str | None = Field(
        default=None,
        alias="selectedActionLabel",
        max_length=120,
    )
    selected_action_route: str | None = Field(
        default=None,
        alias="selectedActionRoute",
        max_length=240,
    )


class AssistantClientContext(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    current_route: str | None = Field(default=None, alias="currentRoute", max_length=240)
    current_page: str | None = Field(default=None, alias="currentPage", max_length=120)
    current_app: AssistantContextApp | None = Field(default=None, alias="currentApp")
    current_category: str | None = Field(default=None, alias="currentCategory", max_length=120)
    last_opened_app: AssistantContextApp | None = Field(default=None, alias="lastOpenedApp")
    recent_app_keys: list[str] = Field(default_factory=list, alias="recentAppKeys", max_length=10)
    favorite_app_ids: list[str] = Field(default_factory=list, alias="favoriteAppIds", max_length=50)
    conversation_history: list[AssistantContextHistoryItem] = Field(
        default_factory=list,
        alias="conversationHistory",
        max_length=10,
    )


class AssistantQueryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.AI_MAX_USER_MESSAGE_LENGTH)
    context: AssistantClientContext | None = None

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
