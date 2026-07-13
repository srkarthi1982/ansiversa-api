from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.subscription_manager.db import get_subscription_manager_db

SubscriptionManagerDB = Annotated[Session, Depends(get_subscription_manager_db)]
CurrentSubscriptionManagerUser = Annotated[User, Depends(get_current_user)]
