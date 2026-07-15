from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.birthday_and_anniversary_reminder.db import get_birthday_reminder_db

BirthdayReminderDB = Annotated[Session, Depends(get_birthday_reminder_db)]
CurrentBirthdayReminderUser = Annotated[User, Depends(get_current_user)]
