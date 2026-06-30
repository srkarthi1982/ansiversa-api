from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.book_summary_generator.db import get_book_summary_generator_db

CurrentUser = Annotated[User, Depends(get_current_user)]
BookSummaryGeneratorDb = Annotated[Session, Depends(get_book_summary_generator_db)]
