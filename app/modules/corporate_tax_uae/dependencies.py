from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.corporate_tax_uae.db import get_corporate_tax_uae_db

CorporateTaxDB = Annotated[Session, Depends(get_corporate_tax_uae_db)]
CurrentCorporateTaxUser = Annotated[User, Depends(get_current_user)]
