from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.home_inventory_manager.db import get_home_inventory_manager_db

HomeInventoryManagerDB = Annotated[Session, Depends(get_home_inventory_manager_db)]
CurrentHomeInventoryManagerUser = Annotated[User, Depends(get_current_user)]
