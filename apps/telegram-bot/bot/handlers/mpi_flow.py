from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.common import send_cancelled
from bot.keyboards.inline import calendar_kb, mpi_confirm_kb
from bot.keyboards.reply import main_menu_kb
from bot.services import api_client
from bot.services.validators import parse_date_kz
from bot.states.application_states import MpiStates

router = Router(name="mpi_flow")


async def _show_mpi_confirm(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    requested_date: object = data["requested_date"]
    await state.set_state(MpiStates.confirm)
    await message.answer(
        "Дербес шот: {account}\n"
        "Өтінім түрі: МПИ-ге шешу\n"
        "Күні: {date}\n\n"
        "Деректер дұрыс па?".format(
            account=data["personal_account"], date=requested_date.strftime("%d.%m.%Y")
        ),
        reply_markup=mpi_confirm_kb(),
    )


@router.message(MpiStates.waiting_date, F.text)
async def mpi_date_entered(message: Message, state: FSMContext) -> None:
    parsed, error = parse_date_kz(message.text)
    if not parsed:
        await message.answer(error)
        return
    await state.update_data(requested_date=parsed)
    await _show_mpi_confirm(message, state)


@router.callback_query(MpiStates.waiting_date, F.data.startswith("cal:nav:"))
async def mpi_calendar_nav(callback: CallbackQuery) -> None:
    year_str, month_str = callback.data.removeprefix("cal:nav:").split("-")
    await callback.message.edit_reply_markup(reply_markup=calendar_kb(int(year_str), int(month_str)))
    await callback.answer()


@router.callback_query(MpiStates.waiting_date, F.data == "cal:noop")
async def mpi_calendar_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(MpiStates.waiting_date, F.data.startswith("cal:day:"))
async def mpi_calendar_day(callback: CallbackQuery, state: FSMContext) -> None:
    from datetime import date

    iso_date = callback.data.removeprefix("cal:day:")
    parsed = date.fromisoformat(iso_date)
    await state.update_data(requested_date=parsed)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_mpi_confirm(callback.message, state)
    await callback.answer()


@router.callback_query(MpiStates.waiting_date, F.data == "mpi:cancel")
async def mpi_cancel_from_calendar(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_cancelled(callback.message)
    await callback.answer()


@router.callback_query(MpiStates.confirm, F.data == "mpi:edit")
async def mpi_edit(callback: CallbackQuery, state: FSMContext) -> None:
    from datetime import date

    await state.set_state(MpiStates.waiting_date)
    await callback.message.edit_reply_markup(reply_markup=None)
    today = date.today()
    await callback.message.answer(
        "МПИ-ге шешу күнін қайта таңдаңыз немесе ДД.ММ.ГГГГ форматында жазыңыз:",
        reply_markup=calendar_kb(today.year, today.month),
    )
    await callback.answer()


@router.callback_query(MpiStates.confirm, F.data == "mpi:cancel")
async def mpi_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_cancelled(callback.message)
    await callback.answer()


@router.callback_query(MpiStates.confirm, F.data == "mpi:submit")
async def mpi_submit(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        result = await api_client.create_application(
            telegram_user_id=callback.from_user.id,
            personal_account=data["personal_account"],
            application_type="MPI_REMOVAL",
            requested_date=data["requested_date"],
        )
    except api_client.ApiError as exc:
        await callback.message.answer(f"❌ Қате: {exc.message}", reply_markup=main_menu_kb())
        await state.clear()
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        "✅ Өтініміңіз қабылданды.\n\nӨтінім нөмірі:\n{number}".format(number=result["application_number"]),
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
