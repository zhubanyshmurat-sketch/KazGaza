import re
from datetime import date, datetime

ACCOUNT_PATTERN = re.compile(r"^\d{4,20}$")
DATE_PATTERN = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")


def validate_account_format(text: str) -> tuple[bool, str | None]:
    """Fast client-side check mirroring the backend's format rule, so the
    user gets instant feedback. The backend remains the source of truth
    (verify_personal_account) and re-validates on submission."""
    value = (text or "").strip()
    if not ACCOUNT_PATTERN.match(value):
        return False, "Дербес шот тек сандардан тұруы керек (4-20 таңба). Қайта енгізіңіз:"
    return True, None


def parse_date_kz(text: str) -> tuple[date | None, str | None]:
    match = DATE_PATTERN.match((text or "").strip())
    if not match:
        return None, "Күнді ДД.ММ.ГГГГ форматында енгізіңіз. Мысалы: 25.09.2026"
    day, month, year = (int(g) for g in match.groups())
    try:
        parsed = date(year, month, day)
    except ValueError:
        return None, "Күн жарамсыз. Қайта енгізіңіз (ДД.ММ.ГГГГ):"
    if parsed < date.today():
        return None, "Күн өткен уақытта болуы мүмкін емес. Қайта енгізіңіз (ДД.ММ.ГГГГ):"
    return parsed, None
