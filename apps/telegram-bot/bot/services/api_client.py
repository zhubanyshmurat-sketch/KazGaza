from datetime import date
from typing import Any

import httpx

from bot.config import get_settings

settings = get_settings()


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.BACKEND_API_URL,
        headers={"X-Bot-Secret": settings.BOT_INTERNAL_TOKEN},
        timeout=20,
    )


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", "Белгісіз қате.")
        except Exception:
            detail = "Белгісіз қате."
        raise ApiError(detail, resp.status_code)


async def register_user(
    telegram_user_id: int,
    telegram_username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> dict[str, Any]:
    async with _client() as client:
        resp = await client.post(
            "/bot/users/register",
            json={
                "telegram_user_id": telegram_user_id,
                "telegram_username": telegram_username,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        _raise_for_status(resp)
        return resp.json()


async def create_application(
    telegram_user_id: int,
    personal_account: str,
    application_type: str,
    requested_date: date | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    photos: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload = {
        "telegram_user_id": telegram_user_id,
        "personal_account": personal_account,
        "application_type": application_type,
        "requested_date": requested_date.isoformat() if requested_date else None,
        "latitude": latitude,
        "longitude": longitude,
        "photos": photos or [],
    }
    async with _client() as client:
        resp = await client.post("/bot/applications", json=payload)
        _raise_for_status(resp)
        return resp.json()


async def get_my_applications(telegram_user_id: int) -> list[dict[str, Any]]:
    async with _client() as client:
        resp = await client.get("/bot/applications/mine", params={"telegram_user_id": telegram_user_id})
        _raise_for_status(resp)
        return resp.json()


async def get_application_status(application_number: str, telegram_user_id: int) -> dict[str, Any]:
    async with _client() as client:
        resp = await client.get(
            f"/bot/applications/{application_number}/status",
            params={"telegram_user_id": telegram_user_id},
        )
        _raise_for_status(resp)
        return resp.json()


async def get_public_settings() -> dict[str, Any]:
    async with _client() as client:
        resp = await client.get("/bot/settings/public")
        _raise_for_status(resp)
        return resp.json()
