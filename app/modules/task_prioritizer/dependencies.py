from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.task_prioritizer.db import get_task_prioritizer_db

CurrentUser = Annotated[User, Depends(get_current_user)]
TaskPrioritizerDb = Annotated[Session, Depends(get_task_prioritizer_db)]
