from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.packing_checklist.db import get_packing_checklist_db

PackingChecklistDB = Annotated[Session, Depends(get_packing_checklist_db)]
CurrentPackingChecklistUser = Annotated[User, Depends(get_current_user)]
