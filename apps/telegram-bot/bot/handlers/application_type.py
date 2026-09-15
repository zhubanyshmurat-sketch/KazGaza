from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.inline import calendar_kb
from bot.services import api_client
from bot.states.application_states import ApplicationStates, GasStates, MeterStates, MpiStates

router = Router(name="application_type")


@router.callback_query(ApplicationStates.select_type, F.data == "apptype:METER_NOT_WORKING")
async def select_meter(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(application_type="METER_NOT_WORKING", photos=[])
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(MeterStates.waiting_photo)
    await callback.message.answer("Есептеу құралының фотосын жіберіңіз.")
    await callback.answer()


@router.callback_query(ApplicationStates.select_type, F.data == "apptype:MPI_REMOVAL")
async def select_mpi(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(application_type="MPI_REMOVAL")
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(MpiStates.waiting_date)
    today = date.today()
    await callback.message.answer(
        "МПИ-ге шешу күнін таңдаңыз немесе ДД.ММ.ГГГГ форматында жазыңыз (мысалы 25.09.2026):",
        reply_markup=calendar_kb(today.year, today.month),
    )
    await callback.answer()


@router.callback_query(ApplicationStates.select_type, F.data == "apptype:GAS_LEAK")
async def select_gas(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(application_type="GAS_LEAK", photos=[])
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "⚠️ Газ иісі қатты сезілсе немесе қауіп төніп тұрса, "
        "авариялық газ қызметіне дереу хабарласыңыз."
    )
    try:
        public_settings = await api_client.get_public_settings()
        emergency_phone = public_settings.get("emergency_phone")
    except Exception:
        emergency_phone = None
    if emergency_phone:
        await callback.message.answer(f"☎️ Авариялық қызмет: {emergency_phone}")

    await state.set_state(GasStates.waiting_meter_photo)
    await callback.message.answer("Есептеу құралының фотосын жіберіңіз.")
    await callback.answer()
