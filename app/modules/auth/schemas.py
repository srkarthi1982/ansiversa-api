from pydantic import BaseModel


class AuthStatusResponse(BaseModel):
    status: str
    service: str
    auth_ready: bool
    message: str
