from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.meal_planner.db import get_meal_planner_db

MealPlannerDB = Annotated[Session, Depends(get_meal_planner_db)]
CurrentMealPlannerUser = Annotated[User, Depends(get_current_user)]
