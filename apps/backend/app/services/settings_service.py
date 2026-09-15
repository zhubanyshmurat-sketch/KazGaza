from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_settings import SystemSettings
from app.schemas.dashboard import SettingsUpdate


async def get_settings_row(db: AsyncSession) -> SystemSettings:
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    row = result.scalar_one_or_none()
    if not row:
        row = SystemSettings(id=1)
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


async def update_settings(db: AsyncSession, data: SettingsUpdate) -> SystemSettings:
    row = await get_settings_row(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    await db.commit()
    await db.refresh(row)
    return row
