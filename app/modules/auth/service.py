from app.modules.auth.schemas import AuthStatusResponse


def get_auth_status() -> AuthStatusResponse:
    return AuthStatusResponse(
        status="ok",
        service="ansiversa-auth",
        auth_ready=False,
        message="Auth module skeleton is ready. Real authentication is not enabled yet.",
    )
