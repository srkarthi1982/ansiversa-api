from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.meeting_scheduler.db import get_meeting_scheduler_db

MeetingSchedulerDB = Annotated[Session, Depends(get_meeting_scheduler_db)]
CurrentMeetingSchedulerUser = Annotated[User, Depends(get_current_user)]
