from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.common import ensure_registered
from bot.keyboards.inline import account_confirm_kb, application_type_kb
from bot.services.validators import validate_account_format
from bot.states.application_states import AccountStates, ApplicationStates

router = Router(name="start")

WELCOME_TEXT = (
    "Қош келдіңіз!\n"
    "Өтінім қалдыру үшін дербес шотыңызды енгізіңіз.\n\n"
    "Дербес шотты енгізіңіз:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await ensure_registered(message)
    await message.answer(WELCOME_TEXT)
    await state.set_state(AccountStates.waiting_account)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    from bot.handlers.common import send_cancelled

    await state.clear()
    await send_cancelled(message, "❌ Әрекет тоқтатылды.")


@router.message(AccountStates.waiting_account, F.text)
async def account_entered(message: Message, state: FSMContext) -> None:
    ok, error = validate_account_format(message.text)
    if not ok:
        await message.answer(error)
        return

    account = message.text.strip()
    await state.update_data(personal_account=account)
    await state.set_state(AccountStates.confirm_account)
    await message.answer(
        f"Сіз енгізген дербес шот:\n\n<b>{account}</b>\n\nДеректер дұрыс па?",
        reply_markup=account_confirm_kb(),
        parse_mode="HTML",
    )


@router.callback_query(AccountStates.confirm_account, F.data == "account:edit")
async def account_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AccountStates.waiting_account)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Дербес шотты қайта енгізіңіз:")
    await callback.answer()


@router.callback_query(AccountStates.confirm_account, F.data == "account:correct")
async def account_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(ApplicationStates.select_type)
    await callback.message.answer("Өтінім түрін таңдаңыз:", reply_markup=application_type_kb())
    await callback.answer()
