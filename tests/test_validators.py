"""Tests for input validation."""
from decimal import Decimal

import pytest
import validators
from errors import InputError

@pytest.mark.parametrize("text, expected", [
    ("300", Decimal("300")),
    ("5000", Decimal("5000")),
    (" 750.50 ", Decimal("750.50")),
    (1200, Decimal("1200")),
])
def test_valid_amounts(text, expected):
    assert validators.validate_amount(text) == expected

@pytest.mark.parametrize("text", ["299.99", "5000.01", "0", "-500", "abc", "", "NaN", "Infinity", "100.123", None])
def test_invalid_amounts_raise_input_error(text):
    with pytest.raises(InputError):
        validators.validate_amount(text)

def test_message_names_the_limits():
    with pytest.raises(InputError) as problem:
        validators.validate_amount("100")
    assert "300" in str(problem.value) and "5,000" in str(problem.value)

def test_currency_is_cleaned_and_checked():
    assert validators.validate_currency(" gbp ") == "GBP"
    with pytest.raises(InputError):
        validators.validate_currency("ABC")
