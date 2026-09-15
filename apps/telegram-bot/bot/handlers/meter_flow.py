from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.common import send_cancelled
from bot.keyboards.inline import meter_confirm_kb
from bot.keyboards.reply import BTN_CANCEL, location_request_kb, main_menu_kb, remove_kb
from bot.services import api_client
from bot.states.application_states import ApplicationStates, MeterStates

router = Router(name="meter_flow")


@router.message(MeterStates.waiting_photo, F.photo)
async def meter_photo_received(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(photos=[{"file_type": "METER_PHOTO", "telegram_file_id": file_id}])
    await state.set_state(MeterStates.waiting_location)
    await message.answer("Геолокацияңызды жіберіңіз.", reply_markup=location_request_kb())


@router.message(MeterStates.waiting_photo)
async def meter_photo_missing(message: Message) -> None:
    await message.answer("Өтінемін, есептеу құралының фотосуретін жіберіңіз (сурет түрінде).")


@router.message(MeterStates.waiting_location, F.text == BTN_CANCEL)
async def meter_location_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_cancelled(message)


@router.message(MeterStates.waiting_location, F.location)
async def meter_location_received(message: Message, state: FSMContext) -> None:
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    await state.set_state(MeterStates.confirm)
    data = await state.get_data()
    await message.answer(
        "Дербес шот: {account}\n"
        "Өтінім түрі: Счетчик жұмыс жасамайды\n"
        "Фото: ✅\n"
        "Геолокация: ✅\n\n"
        "Өтінімді жібересіз бе?".format(account=data["personal_account"]),
        reply_markup=remove_kb(),
    )
    await message.answer("Растаңыз:", reply_markup=meter_confirm_kb())


@router.message(MeterStates.waiting_location)
async def meter_location_missing(message: Message) -> None:
    await message.answer(
        "Өтінемін, «📍 Геолокацияны жіберу» батырмасын басыңыз.", reply_markup=location_request_kb()
    )


@router.callback_query(MeterStates.confirm, F.data == "meter:edit")
async def meter_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(photos=[])
    await state.set_state(MeterStates.waiting_photo)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Есептеу құралының фотосын қайта жіберіңіз.")
    await callback.answer()


@router.callback_query(MeterStates.confirm, F.data == "meter:cancel")
async def meter_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_cancelled(callback.message)
    await callback.answer()


@router.callback_query(MeterStates.confirm, F.data == "meter:submit")
async def meter_submit(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        result = await api_client.create_application(
            telegram_user_id=callback.from_user.id,
            personal_account=data["personal_account"],
            application_type="METER_NOT_WORKING",
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            photos=data.get("photos", []),
        )
    except api_client.ApiError as exc:
        await callback.message.answer(f"❌ Қате: {exc.message}", reply_markup=main_menu_kb())
        await state.clear()
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        "✅ Өтініміңіз қабылданды.\n\n"
        f"Өтінім нөмірі:\n{result['application_number']}\n\n"
        "Өтініміңіздің жағдайын осы нөмір арқылы бақылай аласыз.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
