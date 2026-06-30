from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.snippet_generator.db import get_snippet_generator_db

CurrentUser = Annotated[User, Depends(get_current_user)]
SnippetGeneratorDb = Annotated[Session, Depends(get_snippet_generator_db)]
