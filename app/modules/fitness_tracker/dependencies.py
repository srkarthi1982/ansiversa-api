from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.fitness_tracker.db import get_fitness_tracker_db

FitnessTrackerDB = Annotated[Session, Depends(get_fitness_tracker_db)]
CurrentFitnessTrackerUser = Annotated[User, Depends(get_current_user)]
