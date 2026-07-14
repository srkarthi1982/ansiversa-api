from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.household_expense_splitter.db import get_household_expense_splitter_db

HouseholdExpenseSplitterDB = Annotated[Session, Depends(get_household_expense_splitter_db)]
CurrentHouseholdExpenseSplitterUser = Annotated[User, Depends(get_current_user)]
