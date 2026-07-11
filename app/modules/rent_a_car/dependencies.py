from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.rent_a_car.db import get_rent_a_car_db

RentACarDB = Annotated[Session, Depends(get_rent_a_car_db)]
CurrentRentACarUser = Annotated[User, Depends(get_current_user)]
