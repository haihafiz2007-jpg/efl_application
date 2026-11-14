from decimal import Decimal, ROUND_HALF_UP

import database

TWO_PLACES = Decimal("0.01")
SIX_PLACES = Decimal("0.000001")

def round_money(value):
    """Round to 2 decimal places, halves rounded up."""
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def get_rate(from_code, to_code, db_file=None):
    """Return the rate from one currency to another, rounded to 6 places."""
    from_usd = database.get_rate_to_usd(from_code, db_file)
    to_usd = database.get_rate_to_usd(to_code, db_file)
    return (from_usd / to_usd).quantize(SIX_PLACES, rounding=ROUND_HALF_UP)

def convert(amount, rate):
    """Return the converted amount rounded to 2 decimal places."""
    return round_money(amount * rate)

def refresh_rates(db_file=None):
    """Refresh rates from an external provider when configured."""
    return None
