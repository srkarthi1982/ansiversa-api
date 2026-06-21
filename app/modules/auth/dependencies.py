from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.modules.auth.constants import ADMIN_ROLE_ID
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user


def require_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role_id != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user
