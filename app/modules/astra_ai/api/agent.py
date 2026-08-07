from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, settings
from app.modules.astra_ai.api.chat import (
    ALLOWED_CHAT_ENVIRONMENT_SCOPES,
    astra_chat_environment,
    require_astra_chat_gateway,
)
from app.modules.astra_ai.chat_gateway import AstraChatGateway
from app.modules.astra_ai.intent_provider import OpenAIIntentProvider
from app.modules.astra_ai.natural_language_intent import (
    AstraAgentQueryRequest,
    AstraAgentQueryResponse,
    AstraIntentProvider,
    AstraNaturalLanguageIntentInterpreter,
)
from app.modules.auth.service import AuthenticatedUserContext, get_authenticated_user_context
from app.modules.subscription_manager.dependencies import SubscriptionManagerDB


router = APIRouter()


def should_register_astra_agent_routes(app_settings: Settings = settings) -> bool:
    return astra_chat_environment(app_settings) in ALLOWED_CHAT_ENVIRONMENT_SCOPES


def validate_astra_agent_access(app_settings: Settings = settings) -> None:
    environment = astra_chat_environment(app_settings)
    if environment not in ALLOWED_CHAT_ENVIRONMENT_SCOPES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "astra_agent_unavailable",
                "message": "Astra agent is not available in this environment.",
            },
        )
    if not app_settings.ASTRA_AI_INTENT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "feature_unavailable", "message": "Astra natural-language intent is disabled."},
        )


def get_astra_intent_provider() -> AstraIntentProvider | None:
    provider = OpenAIIntentProvider()
    return provider if provider.is_configured else None


def require_astra_agent_gateway() -> AstraChatGateway:
    validate_astra_agent_access()
    return require_astra_chat_gateway()


@router.post("", response_model=AstraAgentQueryResponse, response_model_by_alias=True)
def create_astra_agent_query(
    payload: AstraAgentQueryRequest,
    authenticated_context: Annotated[AuthenticatedUserContext, Depends(get_authenticated_user_context)],
    db: SubscriptionManagerDB,
    gateway: Annotated[AstraChatGateway, Depends(require_astra_agent_gateway)],
    provider: Annotated[AstraIntentProvider | None, Depends(get_astra_intent_provider)],
) -> AstraAgentQueryResponse:
    return AstraNaturalLanguageIntentInterpreter(gateway=gateway, provider=provider).handle(
        payload,
        authenticated_context=authenticated_context,
        subscription_manager_db=db,
    )
