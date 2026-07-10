from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.language_learning_buddy.db import get_language_learning_buddy_db

LanguageLearningBuddyDB = Annotated[Session, Depends(get_language_learning_buddy_db)]
CurrentLanguageLearningBuddyUser = Annotated[User, Depends(get_current_user)]
