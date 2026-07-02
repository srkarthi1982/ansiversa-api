from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.grammar_and_paraphrasing_assistant.db import get_grammar_and_paraphrasing_assistant_db

CurrentUser = Annotated[User, Depends(get_current_user)]
GrammarAndParaphrasingAssistantDb = Annotated[Session, Depends(get_grammar_and_paraphrasing_assistant_db)]
