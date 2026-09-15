from aiogram.fsm.state import State, StatesGroup


class AccountStates(StatesGroup):
    waiting_account = State()
    confirm_account = State()


class ApplicationStates(StatesGroup):
    select_type = State()


class MeterStates(StatesGroup):
    waiting_photo = State()
    waiting_location = State()
    confirm = State()


class MpiStates(StatesGroup):
    waiting_date = State()
    confirm = State()


class GasStates(StatesGroup):
    waiting_meter_photo = State()
    waiting_leak_photo = State()
    waiting_location = State()
    confirm = State()
