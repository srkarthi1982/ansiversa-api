from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.wellness_and_goal_planner.db import get_wellness_and_goal_planner_db

WellnessAndGoalPlannerDB = Annotated[Session, Depends(get_wellness_and_goal_planner_db)]
CurrentWellnessAndGoalPlannerUser = Annotated[User, Depends(get_current_user)]
