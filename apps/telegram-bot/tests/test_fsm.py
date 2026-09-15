import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import application_type, contact, gas_leak_flow, main_menu, meter_flow, mpi_flow, my_applications, start
from bot.states.application_states import AccountStates, ApplicationStates, GasStates, MeterStates, MpiStates
from tests.fake_telegram import CHAT, USER, callback_update, location_update, make_bot, photo_update, text_update

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def bot():
    b = make_bot()
    yield b
    await b.session.close()


@pytest.fixture(scope="session")
def _dispatcher_singleton():
    # aiogram routers can only ever be attached to one parent, so the
    # router tree (built from module-level router singletons) is wired
    # up exactly once per test session; each test gets a fresh storage.
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(main_menu.router)
    dispatcher.include_router(my_applications.router)
    dispatcher.include_router(contact.router)
    dispatcher.include_router(start.router)
    dispatcher.include_router(application_type.router)
    dispatcher.include_router(meter_flow.router)
    dispatcher.include_router(mpi_flow.router)
    dispatcher.include_router(gas_leak_flow.router)
    return dispatcher


@pytest.fixture
def dp(_dispatcher_singleton):
    _dispatcher_singleton.fsm.storage = MemoryStorage()
    return _dispatcher_singleton


async def _state(dp: Dispatcher, bot) -> str | None:
    key = StorageKey(bot_id=bot.id, chat_id=CHAT.id, user_id=USER.id)
    return await dp.storage.get_state(key)


async def _data(dp: Dispatcher, bot) -> dict:
    key = StorageKey(bot_id=bot.id, chat_id=CHAT.id, user_id=USER.id)
    return await dp.storage.get_data(key)


@pytest.fixture(autouse=True)
def mock_api_client(monkeypatch):
    async def fake_register_user(*args, **kwargs):
        return {"id": 1}

    created = {}

    async def fake_create_application(**kwargs):
        created.update(kwargs)
        return {"application_number": "REQ-20260915-00001", "id": 1}

    async def fake_get_public_settings():
        return {"emergency_phone": "104", "organization_name": "KazGaza", "contact_phone": "8800"}

    monkeypatch.setattr("bot.handlers.common.api_client.register_user", fake_register_user)
    monkeypatch.setattr("bot.handlers.meter_flow.api_client.create_application", fake_create_application)
    monkeypatch.setattr("bot.handlers.mpi_flow.api_client.create_application", fake_create_application)
    monkeypatch.setattr("bot.handlers.gas_leak_flow.api_client.create_application", fake_create_application)
    monkeypatch.setattr("bot.handlers.application_type.api_client.get_public_settings", fake_get_public_settings)
    monkeypatch.setattr("bot.handlers.contact.api_client.get_public_settings", fake_get_public_settings)
    return created


async def test_start_sets_waiting_account_state(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    assert await _state(dp, bot) == AccountStates.waiting_account.state


async def test_account_confirm_flow_moves_to_type_selection(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    assert await _state(dp, bot) == AccountStates.confirm_account.state
    assert (await _data(dp, bot))["personal_account"] == "123456789"

    await dp.feed_update(bot, callback_update("account:correct"))
    assert await _state(dp, bot) == ApplicationStates.select_type.state


async def test_account_edit_returns_to_waiting_account(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:edit"))
    assert await _state(dp, bot) == AccountStates.waiting_account.state


async def test_invalid_account_format_does_not_advance_state(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("not-a-number"))
    assert await _state(dp, bot) == AccountStates.waiting_account.state


async def test_meter_flow_full_happy_path(dp, bot, mock_api_client):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:METER_NOT_WORKING"))
    assert await _state(dp, bot) == MeterStates.waiting_photo.state

    await dp.feed_update(bot, photo_update("meter-photo-1"))
    assert await _state(dp, bot) == MeterStates.waiting_location.state

    await dp.feed_update(bot, location_update())
    assert await _state(dp, bot) == MeterStates.confirm.state

    await dp.feed_update(bot, callback_update("meter:submit"))
    assert await _state(dp, bot) is None  # cleared after successful submission
    assert mock_api_client["application_type"] == "METER_NOT_WORKING"
    assert mock_api_client["photos"][0]["telegram_file_id"] == "meter-photo-1"


async def test_meter_flow_rejects_text_instead_of_photo(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:METER_NOT_WORKING"))

    await dp.feed_update(bot, text_update("here is not a photo"))
    assert await _state(dp, bot) == MeterStates.waiting_photo.state


async def test_meter_flow_cancel_clears_state(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:METER_NOT_WORKING"))
    await dp.feed_update(bot, photo_update())
    await dp.feed_update(bot, location_update())
    await dp.feed_update(bot, callback_update("meter:cancel"))
    assert await _state(dp, bot) is None


async def test_gas_leak_requires_both_photos_before_location(dp, bot, mock_api_client):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:GAS_LEAK"))
    assert await _state(dp, bot) == GasStates.waiting_meter_photo.state

    await dp.feed_update(bot, photo_update("meter-photo"))
    assert await _state(dp, bot) == GasStates.waiting_leak_photo.state

    await dp.feed_update(bot, photo_update("leak-photo"))
    assert await _state(dp, bot) == GasStates.waiting_location.state

    await dp.feed_update(bot, location_update())
    assert await _state(dp, bot) == GasStates.confirm.state

    await dp.feed_update(bot, callback_update("gas:submit"))
    assert await _state(dp, bot) is None
    assert mock_api_client["application_type"] == "GAS_LEAK"
    file_ids = {p["telegram_file_id"] for p in mock_api_client["photos"]}
    assert file_ids == {"meter-photo", "leak-photo"}


async def test_mpi_flow_manual_date_entry(dp, bot, mock_api_client):
    from datetime import date, timedelta

    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:MPI_REMOVAL"))
    assert await _state(dp, bot) == MpiStates.waiting_date.state

    future = date.today() + timedelta(days=5)
    await dp.feed_update(bot, text_update(future.strftime("%d.%m.%Y")))
    assert await _state(dp, bot) == MpiStates.confirm.state

    await dp.feed_update(bot, callback_update("mpi:submit"))
    assert await _state(dp, bot) is None
    assert mock_api_client["application_type"] == "MPI_REMOVAL"
    assert mock_api_client["requested_date"] == future


async def test_main_menu_button_interrupts_in_progress_flow(dp, bot):
    await dp.feed_update(bot, text_update("/start"))
    await dp.feed_update(bot, text_update("123456789"))
    await dp.feed_update(bot, callback_update("account:correct"))
    await dp.feed_update(bot, callback_update("apptype:METER_NOT_WORKING"))
    assert await _state(dp, bot) == MeterStates.waiting_photo.state

    await dp.feed_update(bot, text_update("📝 Өтінім қалдыру"))
    assert await _state(dp, bot) == AccountStates.waiting_account.state
