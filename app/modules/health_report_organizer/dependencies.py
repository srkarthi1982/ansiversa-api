from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.health_report_organizer.db import get_health_report_organizer_db

HealthReportOrganizerDB = Annotated[Session, Depends(get_health_report_organizer_db)]
CurrentHealthReportOrganizerUser = Annotated[User, Depends(get_current_user)]
