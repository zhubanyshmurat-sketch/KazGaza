from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token
from app.config import get_settings
from app.database import get_db
from app.models.admin import Admin

settings = get_settings()

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def get_current_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
    csrf_token: str | None = Cookie(default=None),
) -> Admin:
    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Авторизация қажет.")

    payload = decode_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Токен жарамсыз немесе мерзімі өтті.")

    # CSRF: cookie-based auth requires a matching double-submit token on
    # any state-changing request (double-submit cookie pattern).
    if request.method in MUTATING_METHODS:
        if not csrf_token or not x_csrf_token or csrf_token != x_csrf_token:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF token жарамсыз.")

    admin_id = int(payload["sub"])
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin or not admin.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Аккаунт табылмады немесе өшірілген.")
    return admin


async def verify_bot_secret(x_bot_secret: str | None = Header(default=None)) -> None:
    """Guards the /bot/* endpoints so only the Telegram bot service can call them."""
    if not x_bot_secret or x_bot_secret != settings.BOT_INTERNAL_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid bot credentials.")
