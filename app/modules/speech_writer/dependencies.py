from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.speech_writer.db import get_speech_writer_db

CurrentUser = Annotated[User, Depends(get_current_user)]
SpeechWriterDb = Annotated[Session, Depends(get_speech_writer_db)]
