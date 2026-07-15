from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.home_maintenance_planner.db import get_home_maintenance_db

HomeMaintenanceDB = Annotated[Session, Depends(get_home_maintenance_db)]
CurrentHomeMaintenanceUser = Annotated[User, Depends(get_current_user)]

