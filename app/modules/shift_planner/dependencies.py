from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.shift_planner.db import get_shift_planner_db
ShiftPlannerDB=Annotated[Session,Depends(get_shift_planner_db)]
CurrentShiftPlannerUser=Annotated[User,Depends(get_current_user)]
