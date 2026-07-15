from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.driver_logbook.db import get_driver_logbook_db

DriverLogbookDB = Annotated[Session, Depends(get_driver_logbook_db)]
CurrentDriverLogbookUser = Annotated[User, Depends(get_current_user)]
