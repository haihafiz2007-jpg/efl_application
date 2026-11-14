from decimal import Decimal

import config
from currency import round_money

def conversion_fee_percent(amount):
    """Return the fee percentage for this amount of the initial currency."""
    for threshold, percent in config.FEE_BANDS:
        if amount > threshold:
            return percent
    return config.BASE_FEE_PERCENT

def conversion_fee_usd(amount, from_rate_to_usd):
    """Return the fee converted to US dollars, rounded to 2 decimal places."""
    percent = conversion_fee_percent(amount)
    fee_in_initial = amount * percent / Decimal("100")
    return round_money(fee_in_initial * from_rate_to_usd)
