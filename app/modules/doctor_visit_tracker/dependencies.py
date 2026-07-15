from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.doctor_visit_tracker.db import get_doctor_visit_db

DoctorVisitDB = Annotated[Session, Depends(get_doctor_visit_db)]
CurrentDoctorVisitUser = Annotated[User, Depends(get_current_user)]
