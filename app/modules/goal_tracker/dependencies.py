from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.goal_tracker.db import get_goal_tracker_db

GoalTrackerDB = Annotated[Session, Depends(get_goal_tracker_db)]
CurrentGoalTrackerUser = Annotated[User, Depends(get_current_user)]
