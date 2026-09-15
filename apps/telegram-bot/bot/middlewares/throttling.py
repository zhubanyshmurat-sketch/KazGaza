import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

COOLDOWN_SECONDS = 0.6


class ThrottlingMiddleware(BaseMiddleware):
    """Simple per-user cooldown to absorb accidental double-taps / spam
    without needing external infra. Not a hard rate limit — the backend's
    slowapi limits protect the API itself."""

    def __init__(self) -> None:
        self._last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            now = time.monotonic()
            last = self._last_seen.get(user.id, 0.0)
            if now - last < COOLDOWN_SECONDS:
                return None
            self._last_seen[user.id] = now
        return await handler(event, data)
