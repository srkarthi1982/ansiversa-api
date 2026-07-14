from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.document_expiry_tracker.db import get_document_expiry_tracker_db

DocumentExpiryDB = Annotated[Session, Depends(get_document_expiry_tracker_db)]
CurrentDocumentExpiryUser = Annotated[User, Depends(get_current_user)]
