from decimal import Decimal

import pytest
import currency
from errors import RateUnavailableError

def test_round_money_rounds_half_up():
    assert currency.round_money(Decimal("2.675")) == Decimal("2.68")

def test_round_money_keeps_two_places():
    assert str(currency.round_money(Decimal("5"))) == "5.00"

def test_gbp_to_usd_rate(db_file):
    assert currency.get_rate("GBP", "USD", db_file) == Decimal("1.30")

def test_usd_to_gbp_rate_is_rounded_to_six_places(db_file):
    assert currency.get_rate("USD", "GBP", db_file) == Decimal("0.769231")

def test_convert_applies_rate_and_rounds():
    assert currency.convert(Decimal("300"), Decimal("1.30")) == Decimal("390.00")

def test_missing_rate_raises_error(db_file):
    with pytest.raises(RateUnavailableError):
        currency.get_rate("XXX", "USD", db_file)