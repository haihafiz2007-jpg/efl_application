from decimal import Decimal                                             # Exact numbers

import pytest                                                           # For pytest.raises
import currency                                                         # The file we are testing
from errors import RateUnavailableError                                 # The error we expect for a missing rate

def test_round_money_rounds_half_up():                                  # Halves must round up
    assert currency.round_money(Decimal("2.675")) == Decimal("2.68")    # A float would give 2.67; Decimal with ROUND_HALF_UP gives 2.68

def test_round_money_keeps_two_places():                                # The result always has two decimal places
    assert str(currency.round_money(Decimal("5"))) == "5.00"            # Compare as text, because 5 and 5.00 are equal as numbers

def test_gbp_to_usd_rate(db_file):                                      # db_file is our fixture from conftest.py
    assert currency.get_rate("GBP", "USD", db_file) == Decimal("1.30")  # The sample rate for pounds

def test_usd_to_gbp_rate_is_rounded_to_six_places(db_file):             # 1 divided by 1.3 never ends
    assert currency.get_rate("USD", "GBP", db_file) == Decimal("0.769231")  # 0.76923076... rounded to six places

def test_convert_applies_rate_and_rounds():                             # Pure maths, no database
    assert currency.convert(Decimal("300"), Decimal("1.30")) == Decimal("390.00")  # 300 x 1.30

def test_missing_rate_raises_error(db_file):                            # A currency with no stored rate
    with pytest.raises(RateUnavailableError):                           # The test passes only if this error is raised inside the block
        currency.get_rate("XXX", "USD", db_file)                        # XXX is not a currency we know