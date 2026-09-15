from pydantic import BaseModel, EmailStr

from kazgaza_shared import AdminRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: AdminRole
    active: bool

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    admin: AdminOut
    csrf_token: str
