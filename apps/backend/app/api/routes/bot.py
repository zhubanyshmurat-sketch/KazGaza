from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_bot_secret
from app.core.rate_limit import limiter
from app.repositories import application_repo, user_repo
from app.schemas.application import ApplicationCreateBot, BotApplicationSummary
from app.schemas.user import UserOut, UserRegister
from app.services.account_service import verify_personal_account
from app.services.application_service import create_application_from_bot
from app.services.settings_service import get_settings_row
from app.config import get_settings

router = APIRouter(prefix="/bot", tags=["bot"], dependencies=[Depends(verify_bot_secret)])
settings = get_settings()


@router.post("/users/register", response_model=UserOut)
@limiter.limit(settings.RATE_LIMIT_BOT)
async def register_user(request: Request, data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await user_repo.get_or_create(db, data)
    await db.commit()
    return user


@router.post("/accounts/verify")
@limiter.limit(settings.RATE_LIMIT_BOT)
async def verify_account(request: Request, account_number: str):
    ok, error = verify_personal_account(account_number)
    return {"valid": ok, "error": error}


@router.post("/applications")
@limiter.limit(settings.RATE_LIMIT_BOT)
async def create_application(request: Request, data: ApplicationCreateBot, db: AsyncSession = Depends(get_db)):
    application = await create_application_from_bot(db, data)
    return {"application_number": application.application_number, "id": application.id}


@router.get("/applications/mine", response_model=list[BotApplicationSummary])
@limiter.limit(settings.RATE_LIMIT_BOT)
async def my_applications(request: Request, telegram_user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_repo.get_by_telegram_id(db, telegram_user_id)
    if not user:
        return []
    return await application_repo.list_for_user(db, user.id, limit=10)


@router.get("/applications/{application_number}/status", response_model=BotApplicationSummary)
@limiter.limit(settings.RATE_LIMIT_BOT)
async def application_status(
    request: Request, application_number: str, telegram_user_id: int, db: AsyncSession = Depends(get_db)
):
    application = await application_repo.get_by_number(db, application_number)
    if not application or application.user.telegram_user_id != telegram_user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Өтінім табылмады.")
    return application


@router.get("/settings/public")
@limiter.limit(settings.RATE_LIMIT_BOT)
async def public_settings(request: Request, db: AsyncSession = Depends(get_db)):
    row = await get_settings_row(db)
    return {
        "organization_name": row.organization_name,
        "contact_phone": row.contact_phone,
        "emergency_phone": row.emergency_phone,
        "max_photo_size_mb": row.max_photo_size_mb,
        "welcome_text": row.welcome_text,
    }
