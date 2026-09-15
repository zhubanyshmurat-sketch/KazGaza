from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

MENU_NEW_APPLICATION = "📝 Өтінім қалдыру"
MENU_MY_APPLICATIONS = "📋 Менің өтінімдерім"
MENU_CONTACT = "☎️ Байланыс"
BTN_SEND_LOCATION = "📍 Геолокацияны жіберу"
BTN_CANCEL = "❌ Бас тарту"


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_NEW_APPLICATION)],
            [KeyboardButton(text=MENU_MY_APPLICATIONS), KeyboardButton(text=MENU_CONTACT)],
        ],
        resize_keyboard=True,
    )


def location_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SEND_LOCATION, request_location=True)],
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
