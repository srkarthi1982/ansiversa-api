from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.parking_expense_tracker.db import get_parking_expense_tracker_db

ParkingExpenseDB = Annotated[Session, Depends(get_parking_expense_tracker_db)]
CurrentParkingExpenseUser = Annotated[User, Depends(get_current_user)]
