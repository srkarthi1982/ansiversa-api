from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.medicine_reminder.db import get_medicine_reminder_db

MedicineReminderDB = Annotated[Session, Depends(get_medicine_reminder_db)]
CurrentMedicineReminderUser = Annotated[User, Depends(get_current_user)]
