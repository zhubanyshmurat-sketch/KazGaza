from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.handlers.common import APPLICATION_TYPE_LABELS_KK, STATUS_LABELS_KK
from bot.keyboards.reply import MENU_MY_APPLICATIONS, main_menu_kb
from bot.services import api_client

router = Router(name="my_applications")


def _format_application_line(app: dict) -> str:
    app_type = APPLICATION_TYPE_LABELS_KK.get(app["application_type"], app["application_type"])
    status = STATUS_LABELS_KK.get(app["status"], app["status"])
    created = app["created_at"][:10]
    day, month, year = created.split("-")[::-1] if "-" in created else (created, "", "")
    return f"<b>{app['application_number']}</b>\n{app_type}\n{day}.{month}.{year}\n{status}"


@router.message(F.text == MENU_MY_APPLICATIONS)
async def show_my_applications(message: Message, state: FSMContext) -> None:
    await state.clear()
    applications = await api_client.get_my_applications(message.from_user.id)
    if not applications:
        await message.answer("Сізде әлі өтінімдер жоқ.", reply_markup=main_menu_kb())
        return

    text = "📋 Соңғы өтінімдеріңіз:\n\n" + "\n\n".join(_format_application_line(a) for a in applications)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🔄 {a['application_number']}", callback_data=f"myapp:{a['application_number']}")]
            for a in applications
        ]
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")
    await message.answer("Жағдайын жаңарту үшін таңдаңыз:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("myapp:"))
async def refresh_application_status(callback: CallbackQuery) -> None:
    application_number = callback.data.removeprefix("myapp:")
    try:
        app = await api_client.get_application_status(application_number, callback.from_user.id)
    except api_client.ApiError as exc:
        await callback.answer(exc.message, show_alert=True)
        return
    status = STATUS_LABELS_KK.get(app["status"], app["status"])
    await callback.answer(f"{application_number}: {status}", show_alert=True)
