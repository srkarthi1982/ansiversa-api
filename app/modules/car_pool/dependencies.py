from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.car_pool.db import get_car_pool_db

CarPoolDB = Annotated[Session, Depends(get_car_pool_db)]
CurrentCarPoolUser = Annotated[User, Depends(get_current_user)]
