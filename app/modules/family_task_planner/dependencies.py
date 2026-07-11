from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.family_task_planner.db import get_family_task_planner_db

FamilyTaskPlannerDB = Annotated[Session, Depends(get_family_task_planner_db)]
CurrentFamilyTaskPlannerUser = Annotated[User, Depends(get_current_user)]
