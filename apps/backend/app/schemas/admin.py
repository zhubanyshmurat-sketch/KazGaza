from pydantic import BaseModel, EmailStr, Field

from kazgaza_shared import AdminRole


class AdminCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: AdminRole = AdminRole.OPERATOR


class AdminUpdate(BaseModel):
    name: str | None = None
    role: AdminRole | None = None
    active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class AdminOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: AdminRole
    active: bool

    model_config = {"from_attributes": True}
