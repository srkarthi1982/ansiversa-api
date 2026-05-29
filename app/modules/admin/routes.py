from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.admin.schemas import AdminStatusResponse, AdminUserResponse
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User

router = APIRouter()


@router.get("/status", response_model=AdminStatusResponse)
def admin_status(
    current_admin: Annotated[User, Depends(require_admin_user)],
) -> AdminStatusResponse:
    return AdminStatusResponse(
        status="ok",
        service="ansiversa-admin",
        admin=AdminUserResponse(
            id=current_admin.id,
            email=current_admin.email,
            role_id=current_admin.role_id,
        ),
    )
