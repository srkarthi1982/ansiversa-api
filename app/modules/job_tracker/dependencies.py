from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.job_tracker.db import get_job_tracker_db

CurrentUser = Annotated[User, Depends(get_current_user)]
JobTrackerDb = Annotated[Session, Depends(get_job_tracker_db)]
