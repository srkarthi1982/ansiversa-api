from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.first_aid_guide.db import get_first_aid_guide_db

FirstAidGuideDB = Annotated[Session, Depends(get_first_aid_guide_db)]
CurrentFirstAidGuideUser = Annotated[User, Depends(get_current_user)]
