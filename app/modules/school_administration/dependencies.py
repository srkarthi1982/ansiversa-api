from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.school_administration.db import get_school_administration_db

SchoolAdministrationDB = Annotated[Session, Depends(get_school_administration_db)]
CurrentSchoolAdministrationUser = Annotated[User, Depends(get_current_user)]
