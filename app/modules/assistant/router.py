from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.assistant.schemas import AssistantQueryRequest, AssistantQueryResponse
from app.modules.assistant.service import query_assistant
from app.modules.auth.models import User
from app.modules.auth.service import get_optional_current_user

router = APIRouter()


@router.post("/query", response_model=AssistantQueryResponse)
def query_ansiversa_assistant(
    payload: AssistantQueryRequest,
    db: Annotated[Session, Depends(get_parent_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> AssistantQueryResponse:
    return query_assistant(
        db,
        payload.message,
        payload.context,
        current_user=current_user,
    )
