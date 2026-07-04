from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.project_tracker.db import get_project_tracker_db

CurrentUser = Annotated[User, Depends(get_current_user)]
ProjectTrackerDb = Annotated[Session, Depends(get_project_tracker_db)]
