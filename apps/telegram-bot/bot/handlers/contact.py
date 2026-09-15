from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import MENU_CONTACT, main_menu_kb
from bot.services import api_client

router = Router(name="contact")


@router.message(F.text == MENU_CONTACT)
async def show_contact(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        settings = await api_client.get_public_settings()
    except api_client.ApiError:
        settings = {}

    org = settings.get("organization_name", "KazGaza")
    contact_phone = settings.get("contact_phone") or "-"
    emergency_phone = settings.get("emergency_phone") or "-"

    text = (
        f"☎️ <b>{org}</b>\n\n"
        f"Байланыс телефоны: {contact_phone}\n"
        f"🚨 Авариялық қызмет: {emergency_phone}"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")
