from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister


async def get_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    return result.scalar_one_or_none()


async def get_or_create(db: AsyncSession, data: UserRegister) -> User:
    user = await get_by_telegram_id(db, data.telegram_user_id)
    if user:
        user.telegram_username = data.telegram_username
        user.first_name = data.first_name
        user.last_name = data.last_name
        if data.phone_number:
            user.phone_number = data.phone_number
        await db.flush()
        return user

    user = User(
        telegram_user_id=data.telegram_user_id,
        telegram_username=data.telegram_username,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
    )
    db.add(user)
    await db.flush()
    return user
