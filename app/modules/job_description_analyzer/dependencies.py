from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.job_description_analyzer.db import get_job_description_analyzer_db

CurrentUser = Annotated[User, Depends(get_current_user)]
JobDescriptionAnalyzerDb = Annotated[Session, Depends(get_job_description_analyzer_db)]
