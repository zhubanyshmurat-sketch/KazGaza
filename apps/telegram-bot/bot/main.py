import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from bot.config import get_settings
from bot.handlers import (
    application_type,
    contact,
    gas_leak_flow,
    main_menu,
    meter_flow,
    mpi_flow,
    my_applications,
    start,
)
from bot.middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("kazgaza.bot")


async def main() -> None:
    settings = get_settings()

    try:
        storage = RedisStorage.from_url(settings.REDIS_URL)
        await storage.redis.ping()
        logger.info("Using Redis FSM storage")
    except Exception:
        logger.warning("Redis unavailable, falling back to in-memory FSM storage")
        storage = MemoryStorage()

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    dp.message.middleware(ThrottlingMiddleware())

    # Registration order matters: the main-menu buttons are matched first
    # so they can interrupt an in-progress application flow at any time.
    dp.include_router(main_menu.router)
    dp.include_router(my_applications.router)
    dp.include_router(contact.router)
    dp.include_router(start.router)
    dp.include_router(application_type.router)
    dp.include_router(meter_flow.router)
    dp.include_router(mpi_flow.router)
    dp.include_router(gas_leak_flow.router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Өтінім қалдыруды бастау"),
            BotCommand(command="cancel", description="Ағымдағы әрекетті тоқтату"),
        ]
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
