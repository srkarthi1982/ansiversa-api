from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.prompt_builder.db import get_prompt_builder_db

CurrentUser = Annotated[User, Depends(get_current_user)]
PromptBuilderDb = Annotated[Session, Depends(get_prompt_builder_db)]
