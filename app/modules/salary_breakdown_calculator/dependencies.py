from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.salary_breakdown_calculator.db import get_db
DB=Annotated[Session,Depends(get_db)];CurrentUser=Annotated[User,Depends(get_current_user)]
