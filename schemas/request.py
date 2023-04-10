from pydantic import BaseModel
from pydantic import EmailStr

from typing import Optional


class RequestData(BaseModel):
    accs: list[str | int]


class AuthDataLogin(BaseModel):
    login: str

class AuthData(AuthDataLogin):
    password: str
    code: Optional[str] = None
    email: Optional[EmailStr] = None
