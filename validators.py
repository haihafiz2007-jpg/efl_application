from decimal import Decimal, InvalidOperation                           # InvalidOperation is raised when text is not a number

import config                                                           # The limits and currency codes live in config.py
from errors import InputError                                           # The error type for bad user input

def validate_amount(text):                                              # Check the amount the user typed
    """Return the amount as a Decimal, or raise InputError with a clear message."""  # Docstring
    try:                                                                # Try to turn the text into a number
        amount = Decimal(str(text).strip())                             # str() copes with numbers and None; strip() removes spaces
    except InvalidOperation:                                            # The text was not a number, for example abc or empty
        raise InputError("Enter the amount as a number, for example 500.")  # A message the user can act on
    if not amount.is_finite():                                          # Decimal accepts words like NaN and Infinity, so block them
        raise InputError("Enter the amount as a number, for example 500.")  # Same message
    if amount.as_tuple().exponent < -2:                                 # More than two digits after the point, such as 100.123
        raise InputError("Use at most two decimal places.")             # Tell the user what to fix
    if amount < config.MIN_TRANSACTION or amount > config.MAX_TRANSACTION:  # Outside the Annexe A limits
        raise InputError(f"The amount must be between {config.MIN_TRANSACTION:,} and {config.MAX_TRANSACTION:,}.")  # f-string puts the limits in the message, with commas
    return amount                                                       # Everything passed, so return the clean Decimal

def validate_currency(code):                                            # Check a currency code
    """Return the code in capitals, or raise InputError."""             # Docstring
    clean = str(code).strip().upper()                                   # Remove spaces and make capitals, so " gbp " becomes GBP
    if clean not in config.CURRENCIES:                                  # Not one of the six
        raise InputError("Choose one of: " + ", ".join(config.CURRENCIES) + ".")  # List the allowed codes
    return clean                                                        # Return the clean code