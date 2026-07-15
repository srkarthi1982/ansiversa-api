from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.emergency_contacts_organizer.db import get_emergency_contacts_organizer_db

EmergencyContactsOrganizerDB = Annotated[Session, Depends(get_emergency_contacts_organizer_db)]
CurrentEmergencyContactsOrganizerUser = Annotated[User, Depends(get_current_user)]
