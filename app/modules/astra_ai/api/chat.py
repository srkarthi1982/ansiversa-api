from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, settings
from app.modules.astra_ai.chat_gateway import (
    AstraChatGateway,
    AstraChatGatewayError,
    AstraChatRequest,
    AstraChatResponse,
)
from app.modules.astra_ai.configuration import AstraConfigurationError, load_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    EnvironmentScope,
    ProductionAuthorizationState,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError, AstraRuntimeState
from app.modules.auth.service import AuthenticatedUserContext, get_authenticated_user_context
from app.modules.subscription_manager.dependencies import SubscriptionManagerDB


router = APIRouter()
ASTRA_CHAT_ROUTE_PREFIX = "/astra/chat"
ALLOWED_CHAT_ENVIRONMENTS = {"local", "development", "test", "qa", "preview", "staging"}
PRODUCTION_ENVIRONMENTS = {"production"}


class AstraChatRuntimeService:
    def __init__(self) -> None:
        self._runtime: AstraRuntime | None = None
        self._gateway: AstraChatGateway | None = None

    def startup(self) -> None:
        if (
            self._runtime is not None
            and self._runtime.state is AstraRuntimeState.READY
            and self._gateway is not None
        ):
            return
        runtime = AstraRuntime()
        runtime.startup()
        self._runtime = runtime
        self._gateway = AstraChatGateway(runtime=runtime)

    def shutdown(self) -> None:
        if self._runtime is not None and self._runtime.state in {AstraRuntimeState.READY, AstraRuntimeState.FAULTED}:
            self._runtime.shutdown()
        self._runtime = None
        self._gateway = None

    def require_gateway(self) -> AstraChatGateway:
        if self._runtime is None or self._runtime.state is not AstraRuntimeState.READY or self._gateway is None:
            raise AstraChatGatewayError("Astra chat Runtime is unavailable.")
        return self._gateway


chat_runtime_service = AstraChatRuntimeService()


def validate_astra_chat_access(app_settings: Settings = settings) -> None:
    environment = astra_chat_environment(app_settings)
    if environment not in ALLOWED_CHAT_ENVIRONMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "astra_chat_unavailable", "message": "Astra chat is unavailable in this environment."},
        )
    try:
        loaded = load_astra_configuration(app_settings=app_settings)
    except AstraConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "astra_chat_unavailable", "message": "Astra chat requires a valid environment boundary."},
        ) from exc
    if loaded.configuration.environment_scope is EnvironmentScope.PRODUCTION:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "astra_chat_unavailable", "message": "Astra chat is not available in production."},
        )
    if loaded.configuration.production_authorization_state is not ProductionAuthorizationState.NOT_APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "production_not_approved", "message": "Astra chat production authorization is not approved."},
        )
    try:
        chat_runtime_service.startup()
    except (AstraRuntimeError, AstraChatGatewayError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "runtime_unavailable", "message": "Astra chat Runtime failed closed."},
        ) from exc


def astra_chat_environment(app_settings: Settings = settings) -> str | None:
    app_env = app_settings.APP_ENV.strip().lower()
    vercel_env = (app_settings.VERCEL_ENV or "").strip().lower()
    if app_env in PRODUCTION_ENVIRONMENTS or vercel_env in PRODUCTION_ENVIRONMENTS:
        return "production"
    if vercel_env:
        return vercel_env if vercel_env in ALLOWED_CHAT_ENVIRONMENTS else None
    return app_env if app_env in ALLOWED_CHAT_ENVIRONMENTS else None


def should_register_astra_chat_routes(app_settings: Settings = settings) -> bool:
    return astra_chat_environment(app_settings) in ALLOWED_CHAT_ENVIRONMENTS


def require_astra_chat_gateway() -> AstraChatGateway:
    validate_astra_chat_access()
    return chat_runtime_service.require_gateway()


@router.post("", response_model=AstraChatResponse)
def create_astra_chat_turn(
    payload: AstraChatRequest,
    authenticated_context: Annotated[AuthenticatedUserContext, Depends(get_authenticated_user_context)],
    db: SubscriptionManagerDB,
    gateway: Annotated[AstraChatGateway, Depends(require_astra_chat_gateway)],
) -> AstraChatResponse:
    return gateway.handle(
        payload,
        authenticated_context=authenticated_context,
        subscription_manager_db=db,
    )
