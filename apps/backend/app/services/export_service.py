import csv
import io

from openpyxl import Workbook

from app.models.application import Application

HEADERS = [
    "№ Өтінім",
    "Күні",
    "Дербес шот",
    "Түрі",
    "Статус",
    "Приоритет",
    "Пайдаланушы",
    "Орындаушы",
]


def _row_for(app: Application) -> list[str]:
    return [
        app.application_number,
        app.created_at.strftime("%d.%m.%Y %H:%M"),
        app.personal_account,
        app.application_type.value,
        app.status.value,
        app.priority.value,
        app.user.telegram_username or f"id{app.user.telegram_user_id}",
        app.assigned_admin.name if app.assigned_admin else "-",
    ]


def export_csv(applications: list[Application]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADERS)
    for app in applications:
        writer.writerow(_row_for(app))
    return buffer.getvalue().encode("utf-8-sig")


def export_xlsx(applications: list[Application]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Өтінімдер"
    ws.append(HEADERS)
    for app in applications:
        ws.append(_row_for(app))
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
