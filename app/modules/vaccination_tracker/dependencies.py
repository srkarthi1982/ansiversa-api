from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.vaccination_tracker.db import get_vaccination_db

VaccinationDB = Annotated[Session, Depends(get_vaccination_db)]
CurrentVaccinationUser = Annotated[User, Depends(get_current_user)]
