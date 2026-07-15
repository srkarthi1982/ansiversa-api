from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.fuel_expense_tracker.db import get_fuel_expense_db

FuelExpenseDB = Annotated[Session, Depends(get_fuel_expense_db)]
CurrentFuelExpenseUser = Annotated[User, Depends(get_current_user)]
