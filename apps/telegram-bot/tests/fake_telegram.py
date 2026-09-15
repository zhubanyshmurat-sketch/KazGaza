import time
from typing import Any

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import Chat, Message, PhotoSize, Update, User

USER = User(id=555111222, is_bot=False, first_name="Aigerim", username="aigerim_kz")
CHAT = Chat(id=555111222, type="private")

_update_id = [1000]
_message_id = [1]


class RecordingSession(BaseSession):
    """A fake aiogram session: no network calls, records every outgoing
    Bot API method call and fabricates minimally valid responses so
    handlers under test run exactly as they would in production."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[TelegramMethod] = []

    async def make_request(self, bot: Bot, method: TelegramMethod[TelegramType], timeout=None) -> TelegramType:
        self.calls.append(method)
        returning = method.__returning__

        if returning is bool:
            return True  # type: ignore[return-value]

        if returning is Message or (hasattr(returning, "__args__") and Message in getattr(returning, "__args__", ())):
            _message_id[0] += 1
            return Message(
                message_id=_message_id[0],
                date=int(time.time()),
                chat=CHAT,
                text=getattr(method, "text", None) or "",
            )  # type: ignore[return-value]

        return True  # type: ignore[return-value]

    async def close(self) -> None:  # pragma: no cover - nothing to release
        return None

    async def stream_content(self, *args: Any, **kwargs: Any):  # pragma: no cover - unused
        yield b""


def make_bot() -> Bot:
    return Bot(token="123456:TEST-FAKE-TOKEN", session=RecordingSession())


def next_message_id() -> int:
    _message_id[0] += 1
    return _message_id[0]


def next_update_id() -> int:
    _update_id[0] += 1
    return _update_id[0]


def text_update(text: str) -> Update:
    message = Message(
        message_id=next_message_id(),
        date=int(time.time()),
        chat=CHAT,
        from_user=USER,
        text=text,
    )
    return Update(update_id=next_update_id(), message=message)


def photo_update(file_id: str = "fake-photo-file-id") -> Update:
    message = Message(
        message_id=next_message_id(),
        date=int(time.time()),
        chat=CHAT,
        from_user=USER,
        photo=[PhotoSize(file_id=file_id, file_unique_id=file_id, width=100, height=100)],
    )
    return Update(update_id=next_update_id(), message=message)


def location_update(lat: float = 51.169, lon: float = 71.449) -> Update:
    from aiogram.types import Location

    message = Message(
        message_id=next_message_id(),
        date=int(time.time()),
        chat=CHAT,
        from_user=USER,
        location=Location(latitude=lat, longitude=lon),
    )
    return Update(update_id=next_update_id(), message=message)


def callback_update(data: str, message_text: str = "prompt") -> Update:
    from aiogram.types import CallbackQuery

    message = Message(
        message_id=next_message_id(),
        date=int(time.time()),
        chat=CHAT,
        text=message_text,
    )
    callback = CallbackQuery(id=str(next_update_id()), from_user=USER, chat_instance="fake", data=data, message=message)
    return Update(update_id=next_update_id(), callback_query=callback)
