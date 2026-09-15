import logging

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("kazgaza.telegram")


async def send_telegram_message(telegram_user_id: int, text: str) -> None:
    """Best-effort notification to a resident. Failures (e.g. the user
    blocked the bot) must never break the admin action that triggered them."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage",
                json={"chat_id": telegram_user_id, "text": text, "parse_mode": "HTML"},
            )
            if resp.status_code != 200:
                logger.warning("Telegram notify failed for %s: %s", telegram_user_id, resp.text)
    except httpx.HTTPError:
        logger.exception("Telegram notify error for %s", telegram_user_id)
