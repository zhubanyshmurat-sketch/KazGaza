from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.auth.rbac import require_any_admin, require_super_admin
from app.schemas.dashboard import SettingsOut, SettingsUpdate
from app.services.settings_service import get_settings_row, update_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsOut, dependencies=[Depends(require_any_admin)])
async def read_settings(db: AsyncSession = Depends(get_db)):
    return await get_settings_row(db)


@router.patch("", response_model=SettingsOut, dependencies=[Depends(require_super_admin)])
async def patch_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    return await update_settings(db, data)
