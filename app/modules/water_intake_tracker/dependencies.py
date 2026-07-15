from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.water_intake_tracker.db import get_water_intake_db

WaterIntakeDB = Annotated[Session, Depends(get_water_intake_db)]
CurrentWaterIntakeUser = Annotated[User, Depends(get_current_user)]
