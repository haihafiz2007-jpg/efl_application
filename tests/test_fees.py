from decimal import Decimal

import pytest
import fees

@pytest.mark.parametrize("amount, expected", [
    ("300", "3.5"),
    ("500", "3.5"),
    ("501", "2.7"),
    ("1500", "2.7"),
    ("1501", "2.0"),
    ("2500", "2.0"),
    ("2501", "1.5"),
    ("5000", "1.5"),
])
def test_fee_percent_at_band_edges(amount, expected):
    assert fees.conversion_fee_percent(Decimal(amount)) == Decimal(expected)

@pytest.mark.parametrize("amount, expected_fee", [
    ("300", "13.65"),
    ("500", "22.75"),
    ("501", "17.59"),
    ("1500", "52.65"),
    ("1501", "39.03"),
    ("2500", "65.00"),
    ("2501", "48.77"),
    ("5000", "97.50"),
])
def test_fee_in_usd_at_rate_1_30(amount, expected_fee):
    result = fees.conversion_fee_usd(Decimal(amount), Decimal("1.30"))
    assert result == Decimal(expected_fee)
