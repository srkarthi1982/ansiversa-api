from fastapi import APIRouter

from app.modules.auth.schemas import AuthStatusResponse
from app.modules.auth.service import get_auth_status

router = APIRouter()


@router.get("/status/", response_model=AuthStatusResponse)
def auth_status() -> AuthStatusResponse:
    return get_auth_status()
