import pytest

from app.services.account_service import verify_personal_account


@pytest.mark.parametrize(
    "account,expected_valid",
    [
        ("123456789", True),
        ("1234", True),
        ("12345678901234567890", True),
        ("abc123", False),
        ("123", False),
        ("", False),
        ("123456789012345678901", False),  # 21 digits, too long
        (" 123456 ", True),  # trimmed
    ],
)
def test_verify_personal_account_format(account, expected_valid):
    ok, error = verify_personal_account(account)
    assert ok is expected_valid
    if not expected_valid:
        assert error
