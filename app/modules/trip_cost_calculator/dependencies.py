from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.trip_cost_calculator.db import get_trip_cost_calculator_db

TripCostDB = Annotated[Session, Depends(get_trip_cost_calculator_db)]
CurrentTripCostUser = Annotated[User, Depends(get_current_user)]
