from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.vat_assistant_uae.db import get_vat_assistant_uae_db

VatAssistantDB = Annotated[Session, Depends(get_vat_assistant_uae_db)]
CurrentVatAssistantUser = Annotated[User, Depends(get_current_user)]
