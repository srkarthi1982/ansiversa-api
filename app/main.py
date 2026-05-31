from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.openapi import generate_operation_id
from app.modules.admin.apps_routes import router as admin_apps_router
from app.modules.admin.categories_routes import router as admin_categories_router
from app.modules.admin.faqs_routes import router as admin_faqs_router
from app.modules.admin.routes import router as admin_router
from app.modules.admin.users_routes import router as admin_users_router
from app.modules.apps.routes import apps_router, categories_router
from app.modules.auth.routes import router as auth_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.faqs.routes import router as faqs_router
from app.modules.favorites.routes import router as favorites_router
from app.modules.health.routes import router as health_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.profile.routes import router as profile_router


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
    app.include_router(
        faqs_router,
        prefix=f"{settings.API_V1_PREFIX}/faqs",
        tags=["FAQs"],
    )
    app.include_router(
        admin_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin"],
    )
    app.include_router(
        admin_categories_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Categories"],
    )
    app.include_router(
        admin_apps_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Apps"],
    )
    app.include_router(
        admin_users_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Users"],
    )
    app.include_router(
        admin_faqs_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin FAQs"],
    )
    app.include_router(
        profile_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Profile"],
    )
    app.include_router(
        favorites_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Favorites"],
    )
    app.include_router(
        notifications_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Notifications"],
    )
    app.include_router(
        dashboard_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Dashboard"],
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
