import re

ACCOUNT_PATTERN = re.compile(r"^\d{4,20}$")


def verify_personal_account(account_number: str) -> tuple[bool, str | None]:
    """Validate a resident's personal/billing account number.

    Stage 1 (current): format-only validation — digits, 4-20 characters.
    Stage 2 (future): plug in a call to the organization's subscriber
    database/API here to confirm the account actually exists, without
    changing this function's signature or call sites.
    """
    account_number = (account_number or "").strip()
    if not ACCOUNT_PATTERN.match(account_number):
        return False, "Дербес шот тек сандардан тұруы керек (4-20 таңба)."
    return True, None
