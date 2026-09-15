import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.auth.security import create_token, decode_token
from app.config import get_settings
from app.core.rate_limit import limiter
from app.models.admin import Admin
from app.schemas.auth import AdminOut, LoginRequest, LoginResponse
from app.services.auth_service import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, admin: Admin) -> str:
    access_token = create_token(admin.id, "access")
    refresh_token = create_token(admin.id, "refresh")
    csrf_token = secrets.token_urlsafe(32)

    cookie_kwargs = dict(
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        "access_token", access_token, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, **cookie_kwargs
    )
    response.set_cookie(
        "refresh_token", refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, **cookie_kwargs
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return csrf_token


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(request: Request, response: Response, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await authenticate(db, data.email, data.password)
    csrf_token = _set_auth_cookies(response, admin)
    return LoginResponse(admin=AdminOut.model_validate(admin), csrf_token=csrf_token)


@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token жоқ.")
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token жарамсыз.")

    from app.repositories import admin_repo

    admin = await admin_repo.get_by_id(db, int(payload["sub"]))
    if not admin or not admin.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Аккаунт табылмады.")
    csrf_token = _set_auth_cookies(response, admin)
    return LoginResponse(admin=AdminOut.model_validate(admin), csrf_token=csrf_token)


@router.post("/logout")
async def logout(response: Response):
    for cookie in ("access_token", "refresh_token", "csrf_token"):
        response.delete_cookie(cookie, path="/", domain=settings.COOKIE_DOMAIN)
    return {"detail": "ok"}


@router.get("/me", response_model=AdminOut)
async def me(admin: Admin = Depends(get_current_admin)):
    return AdminOut.model_validate(admin)
