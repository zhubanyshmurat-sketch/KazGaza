from aiogram.types import Message

from bot.keyboards.reply import main_menu_kb
from bot.services import api_client

APPLICATION_TYPE_LABELS_KK = {
    "METER_NOT_WORKING": "Счетчик жұмыс жасамайды",
    "MPI_REMOVAL": "МПИ-ге шешу",
    "GAS_LEAK": "Есептеу құралынан газ шығуы",
}

STATUS_LABELS_KK = {
    "NEW": "🆕 Жаңа",
    "IN_PROGRESS": "🟡 Өңделуде",
    "COMPLETED": "🟢 Аяқталды",
    "REJECTED": "🔴 Қабылданбады",
}


async def ensure_registered(message: Message) -> None:
    user = message.from_user
    await api_client.register_user(
        telegram_user_id=user.id,
        telegram_username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


async def send_cancelled(message: Message, text: str = "❌ Өтінім толтыру тоқтатылды.") -> None:
    await message.answer(text, reply_markup=main_menu_kb())
