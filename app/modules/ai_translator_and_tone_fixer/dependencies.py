from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.ai_translator_and_tone_fixer.db import get_ai_translator_and_tone_fixer_db

CurrentUser = Annotated[User, Depends(get_current_user)]
AiTranslatorAndToneFixerDb = Annotated[Session, Depends(get_ai_translator_and_tone_fixer_db)]
