from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.leave_planner.db import get_leave_planner_db

LeavePlannerDB = Annotated[Session, Depends(get_leave_planner_db)]
CurrentLeavePlannerUser = Annotated[User, Depends(get_current_user)]
