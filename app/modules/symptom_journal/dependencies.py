from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.symptom_journal.db import get_symptom_journal_db

SymptomJournalDB = Annotated[Session, Depends(get_symptom_journal_db)]
CurrentSymptomJournalUser = Annotated[User, Depends(get_current_user)]
