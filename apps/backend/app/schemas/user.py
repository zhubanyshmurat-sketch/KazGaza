from datetime import datetime

from pydantic import BaseModel


class UserRegister(BaseModel):
    telegram_user_id: int
    telegram_username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None


class UserOut(BaseModel):
    id: int
    telegram_user_id: int
    telegram_username: str | None
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
