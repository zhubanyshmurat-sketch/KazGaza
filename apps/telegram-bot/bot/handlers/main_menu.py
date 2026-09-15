from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.common import ensure_registered
from bot.handlers.start import WELCOME_TEXT
from bot.keyboards.reply import MENU_NEW_APPLICATION
from bot.states.application_states import AccountStates

router = Router(name="main_menu")


@router.message(F.text == MENU_NEW_APPLICATION)
async def new_application(message: Message, state: FSMContext) -> None:
    await state.clear()
    await ensure_registered(message)
    await message.answer(WELCOME_TEXT)
    await state.set_state(AccountStates.waiting_account)
