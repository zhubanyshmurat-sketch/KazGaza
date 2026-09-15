import calendar
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from kazgaza_shared import ApplicationType

TYPE_LABELS = {
    ApplicationType.METER_NOT_WORKING: "🔧 Счетчик жұмыс жасамайды",
    ApplicationType.MPI_REMOVAL: "📅 МПИ-ге шешу",
    ApplicationType.GAS_LEAK: "⚠️ Есептеу құралынан газ шығуы",
}


def account_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Дұрыс", callback_data="account:correct")],
            [InlineKeyboardButton(text="✏️ Өзгерту", callback_data="account:edit")],
        ]
    )


def application_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"apptype:{value.value}")]
            for value, label in TYPE_LABELS.items()
        ]
    )


def meter_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Жіберу", callback_data="meter:submit")],
            [InlineKeyboardButton(text="✏️ Өзгерту", callback_data="meter:edit")],
            [InlineKeyboardButton(text="❌ Бас тарту", callback_data="meter:cancel")],
        ]
    )


def mpi_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Жіберу", callback_data="mpi:submit")],
            [InlineKeyboardButton(text="✏️ Күнді өзгерту", callback_data="mpi:edit")],
            [InlineKeyboardButton(text="❌ Бас тарту", callback_data="mpi:cancel")],
        ]
    )


def gas_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚨 Жіберу", callback_data="gas:submit")],
            [InlineKeyboardButton(text="✏️ Өзгерту", callback_data="gas:edit")],
            [InlineKeyboardButton(text="❌ Бас тарту", callback_data="gas:cancel")],
        ]
    )


KK_MONTHS = [
    "Қаңтар", "Ақпан", "Наурыз", "Сәуір", "Мамыр", "Маусым",
    "Шілде", "Тамыз", "Қыркүйек", "Қазан", "Қараша", "Желтоқсан",
]


def calendar_kb(year: int, month: int) -> InlineKeyboardMarkup:
    today = date.today()
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"{KK_MONTHS[month - 1]} {year}", callback_data="cal:noop")]
    ]

    week_days = ["Дс", "Сс", "Ср", "Бс", "Жм", "Сб", "Жс"]
    rows.append([InlineKeyboardButton(text=d, callback_data="cal:noop") for d in week_days])

    month_days = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal:noop"))
                continue
            day_date = date(year, month, day)
            if day_date < today:
                row.append(InlineKeyboardButton(text="·", callback_data="cal:noop"))
            else:
                row.append(
                    InlineKeyboardButton(text=str(day), callback_data=f"cal:day:{day_date.isoformat()}")
                )
        rows.append(row)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    rows.append(
        [
            InlineKeyboardButton(text="‹", callback_data=f"cal:nav:{prev_year}-{prev_month:02d}"),
            InlineKeyboardButton(text="❌ Бас тарту", callback_data="mpi:cancel"),
            InlineKeyboardButton(text="›", callback_data=f"cal:nav:{next_year}-{next_month:02d}"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
