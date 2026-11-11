from decimal import Decimal, ROUND_HALF_UP                              # ROUND_HALF_UP is the school rule: 2.675 rounds to 2.68

import database                                                         # We read rates through the database file

TWO_PLACES = Decimal("0.01")                                            # The shape of a money amount: two decimal places
SIX_PLACES = Decimal("0.000001")                                        # The shape of a rate: six decimal places (matches the data dictionary)

def round_money(value):                                                 # Round any amount to two decimal places
    """Round to 2 decimal places, halves rounded up."""                 # Docstring
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)           # quantize forces the shape of TWO_PLACES

def get_rate(from_code, to_code, db_file=None):                         # Rate for 1 unit of from_code, in to_code
    """Return the rate from one currency to another, rounded to 6 places."""  # Docstring
    from_usd = database.get_rate_to_usd(from_code, db_file)             # US dollars per 1 unit of the first currency
    to_usd = database.get_rate_to_usd(to_code, db_file)                 # US dollars per 1 unit of the second currency
    return (from_usd / to_usd).quantize(SIX_PLACES, rounding=ROUND_HALF_UP)  # Go through US dollars: the dollars cancel out, leaving first-to-second

def convert(amount, rate):                                              # Apply a rate to an amount
    """Return the converted amount rounded to 2 decimal places."""      # Docstring
    return round_money(amount * rate)                                   # Multiply, then round once at the end

def refresh_rates(db_file=None):                                        # Load fresh rates before converting (Thursday adds the real version)
    """Thursday: load live rates. For now do nothing and report no warning."""  # Docstring
    return None                                                         # None means there is no warning to show
