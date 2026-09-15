from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin


async def get_by_email(db: AsyncSession, email: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.email == email.lower()))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, admin_id: int) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> list[Admin]:
    result = await db.execute(select(Admin).order_by(Admin.created_at.desc()))
    return list(result.scalars().all())
