from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import verify_password
from app.models.admin import Admin
from app.repositories import admin_repo


async def authenticate(db: AsyncSession, email: str, password: str) -> Admin:
    admin = await admin_repo.get_by_email(db, email.lower())
    if not admin or not admin.active or not verify_password(password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email немесе құпия сөз қате.")
    return admin
