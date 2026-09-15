from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.common import send_cancelled
from bot.keyboards.inline import gas_confirm_kb
from bot.keyboards.reply import BTN_CANCEL, location_request_kb, main_menu_kb, remove_kb
from bot.services import api_client
from bot.states.application_states import GasStates

router = Router(name="gas_leak_flow")


@router.message(GasStates.waiting_meter_photo, F.photo)
async def gas_meter_photo_received(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(photos=[{"file_type": "METER_PHOTO", "telegram_file_id": file_id}])
    await state.set_state(GasStates.waiting_leak_photo)
    await message.answer("Газ шығып жатқан жердің фотосын жіберіңіз.")


@router.message(GasStates.waiting_meter_photo)
async def gas_meter_photo_missing(message: Message) -> None:
    await message.answer("Өтінемін, есептеу құралының фотосуретін жіберіңіз (сурет түрінде).")


@router.message(GasStates.waiting_leak_photo, F.photo)
async def gas_leak_photo_received(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    photos = list(data.get("photos", []))
    photos.append({"file_type": "GAS_LEAK_PHOTO", "telegram_file_id": file_id})
    await state.update_data(photos=photos)
    await state.set_state(GasStates.waiting_location)
    await message.answer("Геолокацияңызды жіберіңіз.", reply_markup=location_request_kb())


@router.message(GasStates.waiting_leak_photo)
async def gas_leak_photo_missing(message: Message) -> None:
    await message.answer("Өтінемін, газ шығып жатқан жердің фотосуретін жіберіңіз (сурет түрінде).")


@router.message(GasStates.waiting_location, F.text == BTN_CANCEL)
async def gas_location_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_cancelled(message)


@router.message(GasStates.waiting_location, F.location)
async def gas_location_received(message: Message, state: FSMContext) -> None:
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    await state.set_state(GasStates.confirm)
    data = await state.get_data()
    await message.answer(
        "⚠️ Өтінім түрі:\nЕсептеу құралынан газ шығуы\n\n"
        "Дербес шот: {account}\n"
        "Есептеу құралының фотосы: ✅\n"
        "Газ шығып жатқан жердің фотосы: ✅\n"
        "Геолокация: ✅\n\n"
        "Өтінімді жібересіз бе?".format(account=data["personal_account"]),
        reply_markup=remove_kb(),
    )
    await message.answer("Растаңыз:", reply_markup=gas_confirm_kb())


@router.message(GasStates.waiting_location)
async def gas_location_missing(message: Message) -> None:
    await message.answer(
        "Өтінемін, «📍 Геолокацияны жіберу» батырмасын басыңыз.", reply_markup=location_request_kb()
    )


@router.callback_query(GasStates.confirm, F.data == "gas:edit")
async def gas_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(photos=[])
    await state.set_state(GasStates.waiting_meter_photo)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Есептеу құралының фотосын қайта жіберіңіз.")
    await callback.answer()


@router.callback_query(GasStates.confirm, F.data == "gas:cancel")
async def gas_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_cancelled(callback.message)
    await callback.answer()


@router.callback_query(GasStates.confirm, F.data == "gas:submit")
async def gas_submit(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        result = await api_client.create_application(
            telegram_user_id=callback.from_user.id,
            personal_account=data["personal_account"],
            application_type="GAS_LEAK",
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
        "🚨 Авариялық өтінім қабылданды!\n\n"
        f"Өтінім нөмірі:\n{result['application_number']}\n\n"
        "Жақын арада маман сізбен байланысады.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
