from datetime import date, timedelta

import pytest

from bot.services.validators import parse_date_kz, validate_account_format


@pytest.mark.parametrize(
    "account,expected",
    [
        ("123456789", True),
        ("1234", True),
        ("abc", False),
        ("", False),
        ("12 34", False),
    ],
)
def test_validate_account_format(account, expected):
    ok, error = validate_account_format(account)
    assert ok is expected
    if not expected:
        assert error


def test_parse_date_kz_valid_future_date():
    future = date.today() + timedelta(days=10)
    text = future.strftime("%d.%m.%Y")
    parsed, error = parse_date_kz(text)
    assert parsed == future
    assert error is None


def test_parse_date_kz_rejects_bad_format():
    parsed, error = parse_date_kz("2026-09-25")
    assert parsed is None
    assert error


def test_parse_date_kz_rejects_invalid_calendar_date():
    parsed, error = parse_date_kz("31.02.2026")
    assert parsed is None
    assert error


def test_parse_date_kz_rejects_past_date():
    past = date.today() - timedelta(days=1)
    parsed, error = parse_date_kz(past.strftime("%d.%m.%Y"))
    assert parsed is None
    assert "өткен" in error
