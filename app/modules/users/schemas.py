from typing import Literal

from pydantic import BaseModel


Theme = Literal["system", "light", "dark"]
Language = Literal["en", "ta", "ar"]


class UserSettingsResponse(BaseModel):
    theme: Theme = "system"
    language: Language = "en"
    marketing_emails: bool = False


class UserSettingsUpdateRequest(BaseModel):
    theme: Theme | None = None
    language: Language | None = None
    marketing_emails: bool | None = None
