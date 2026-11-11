from decimal import Decimal, InvalidOperation

import config
from errors import InputError

def validate_amount(text):
    """Return the amount as a Decimal, or raise InputError with a clear message."""
    try:
        amount = Decimal(str(text).strip())
    except InvalidOperation:
        raise InputError("Enter the amount as a number, for example 500.")
    if not amount.is_finite():
        raise InputError("Enter the amount as a number, for example 500.")
    if amount.as_tuple().exponent < -2:
        raise InputError("Use at most two decimal places.")
    if amount < config.MIN_TRANSACTION or amount > config.MAX_TRANSACTION:
        raise InputError(f"The amount must be between {config.MIN_TRANSACTION:,} and {config.MAX_TRANSACTION:,}.")
    return amount

def validate_currency(code):
    """Return the code in capitals, or raise InputError."""
    clean = str(code).strip().upper()
    if clean not in config.CURRENCIES:
        raise InputError("Choose one of: " + ", ".join(config.CURRENCIES) + ".")
    return clean