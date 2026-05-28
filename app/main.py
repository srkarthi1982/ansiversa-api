from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.openapi import generate_operation_id
from app.modules.apps.routes import apps_router, categories_router
from app.modules.auth.routes import router as auth_router
from app.modules.health.routes import router as health_router


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routes(app: FastAPI) -> None:
    app.include_router(
        health_router,
        prefix=f"{settings.API_V1_PREFIX}/health",
        tags=["Health"],
    )
    app.include_router(
        auth_router,
        prefix=f"{settings.API_V1_PREFIX}/auth",
        tags=["Auth"],
    )
    app.include_router(
        apps_router,
        prefix=f"{settings.API_V1_PREFIX}/apps",
        tags=["Apps"],
    )
    app.include_router(
        categories_router,
        prefix=f"{settings.API_V1_PREFIX}/categories",
        tags=["Categories"],
    )

    @app.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "status": "running",
            "version": settings.APP_VERSION,
        }


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Single source of truth API for the Ansiversa ecosystem.",
        version=settings.APP_VERSION,
        generate_unique_id_function=generate_operation_id,
    )

    register_middleware(app)
    register_routes(app)

    return app


app = create_app()
