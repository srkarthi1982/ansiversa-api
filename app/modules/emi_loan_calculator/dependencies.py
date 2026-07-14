from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.emi_loan_calculator.db import get_emi_loan_calculator_db

EmiLoanCalculatorDB = Annotated[Session, Depends(get_emi_loan_calculator_db)]
CurrentEmiLoanCalculatorUser = Annotated[User, Depends(get_current_user)]
