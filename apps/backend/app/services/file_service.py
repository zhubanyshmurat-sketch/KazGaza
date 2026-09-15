import io
import uuid
from pathlib import Path

import httpx
from fastapi import HTTPException, status
from PIL import Image, UnidentifiedImageError

from app.config import get_settings
from kazgaza_shared import FileType

settings = get_settings()

_MIME_TO_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
_PIL_FORMAT_TO_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class TelegramFileError(Exception):
    pass


async def fetch_telegram_photo_bytes(telegram_file_id: str) -> bytes:
    """Downloads a photo from Telegram servers using the bot token.

    The bot only ever hands the backend a file_id; the backend is the
    sole owner of image storage/validation, matching the "storage of
    photographs" requirement being backend-side.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        meta_resp = await client.get(
            f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile",
            params={"file_id": telegram_file_id},
        )
        meta = meta_resp.json()
        if not meta.get("ok"):
            raise TelegramFileError("Telegram getFile failed")
        file_path = meta["result"]["file_path"]

        file_resp = await client.get(f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}")
        if file_resp.status_code != 200:
            raise TelegramFileError("Telegram file download failed")
        return file_resp.content


def validate_and_identify_image(raw: bytes) -> str:
    """Validates real image content/size (never trusts a filename or
    client-declared MIME type) and returns the sniffed MIME type."""
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"Файл тым үлкен (максимум {settings.MAX_UPLOAD_MB}MB).",
        )
    try:
        with Image.open(io.BytesIO(raw)) as img:
            img.verify()
            fmt = img.format
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Файл жарамды сурет емес.")

    mime = _PIL_FORMAT_TO_MIME.get(fmt or "")
    if mime not in settings.ALLOWED_IMAGE_MIME:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Суреттің форматы қолдау көрсетілмейді.")
    return mime


def store_image(raw: bytes, mime: str, application_number: str) -> str:
    ext = _MIME_TO_EXT.get(mime, ".jpg")
    directory = Path(settings.UPLOAD_DIR) / application_number
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    (directory / filename).write_bytes(raw)
    return f"{settings.PUBLIC_MEDIA_BASE_URL}/{application_number}/{filename}"


async def download_validate_store(telegram_file_id: str, application_number: str) -> str:
    raw = await fetch_telegram_photo_bytes(telegram_file_id)
    mime = validate_and_identify_image(raw)
    return store_image(raw, mime, application_number)


REQUIRED_PHOTOS = {
    "METER_NOT_WORKING": {FileType.METER_PHOTO},
    "GAS_LEAK": {FileType.METER_PHOTO, FileType.GAS_LEAK_PHOTO},
    "MPI_REMOVAL": set(),
}
