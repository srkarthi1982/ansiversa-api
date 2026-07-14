from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.digital_document_vault.db import get_digital_document_vault_db

DigitalDocumentVaultDB = Annotated[Session, Depends(get_digital_document_vault_db)]
CurrentDigitalDocumentVaultUser = Annotated[User, Depends(get_current_user)]
