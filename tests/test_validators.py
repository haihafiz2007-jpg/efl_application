"""Tests for input validation."""                                       # Docstring: what is tested
from decimal import Decimal                                             # Exact numbers

import pytest                                                           # For parametrize and raises
import validators                                                       # The file we are testing
from errors import InputError                                           # The error we expect for bad input

@pytest.mark.parametrize("text, expected", [                            # Valid amounts and what they should become
    ("300", Decimal("300")),                                            # The minimum is allowed
    ("5000", Decimal("5000")),                                          # The maximum is allowed
    (" 750.50 ", Decimal("750.50")),                                    # Spaces are removed
    (1200, Decimal("1200")),                                            # A number, not text, also works
])                                                                      # End of the table
def test_valid_amounts(text, expected):                                 # One run per row
    assert validators.validate_amount(text) == expected                 # The clean Decimal comes back

@pytest.mark.parametrize("text", ["299.99", "5000.01", "0", "-500", "abc", "", "NaN", "Infinity", "100.123", None])  # Every kind of bad input we thought of
def test_invalid_amounts_raise_input_error(text):                       # One run per bad value
    with pytest.raises(InputError):                                     # Each must be rejected
        validators.validate_amount(text)                                # Try the bad value

def test_message_names_the_limits():                                    # The message must help the user
    with pytest.raises(InputError) as problem:                          # Keep the error so we can read its message
        validators.validate_amount("100")                               # Below the minimum
    assert "300" in str(problem.value) and "5,000" in str(problem.value)  # The message contains both limits

def test_currency_is_cleaned_and_checked():                             # Currency codes
    assert validators.validate_currency(" gbp ") == "GBP"               # Spaces and lower case are fixed
    with pytest.raises(InputError):                                     # Unknown code
        validators.validate_currency("ABC")                             # Not one of the six
