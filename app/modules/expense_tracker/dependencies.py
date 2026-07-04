from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.expense_tracker.db import get_expense_tracker_db

ExpenseTrackerDB = Annotated[Session, Depends(get_expense_tracker_db)]
CurrentExpenseTrackerUser = Annotated[User, Depends(get_current_user)]

