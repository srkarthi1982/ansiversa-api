from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.contact.schemas import (
    ContactMessageCreateRequest,
    ContactMessageResponse,
)
from app.modules.contact.service import create_contact_message

router = APIRouter()


@router.post(
    "",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_contact_message(
    payload: ContactMessageCreateRequest,
    db: Annotated[Session, Depends(get_parent_db)],
) -> ContactMessageResponse:
    contact_message = create_contact_message(db, payload)

    return ContactMessageResponse.model_validate(contact_message)
