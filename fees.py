from decimal import Decimal                                             # For exact money maths

import config                                                           # The fee bands live in config.py
from currency import round_money                                        # Reuse the 2-decimal rounding rule

def conversion_fee_percent(amount):                                     # Which fee band does this amount fall in?
    """Return the fee percentage for this amount of the initial currency."""  # Docstring
    for threshold, percent in config.FEE_BANDS:                         # Check the highest band first
        if amount > threshold:                                          # Strictly over the threshold, so exactly 500 does not count as over 500
            return percent                                              # Found the band, stop here
    return config.BASE_FEE_PERCENT                                      # Not over 500, so the base fee applies

def conversion_fee_usd(amount, from_rate_to_usd):                       # The fee in US dollars
    """Return the fee converted to US dollars, rounded to 2 decimal places."""  # Docstring
    percent = conversion_fee_percent(amount)                            # Step 1: find the band percentage
    fee_in_initial = amount * percent / Decimal("100")                  # Step 2: the fee in the currency the user is selling
    return round_money(fee_in_initial * from_rate_to_usd)               # Step 3: convert to dollars, then round once
