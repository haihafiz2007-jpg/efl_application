from decimal import Decimal                                             # Exact numbers, as in the real code

import pytest                                                           # Gives us parametrize
import fees                                                             # The file we are testing

@pytest.mark.parametrize("amount, expected", [                          # Run the test below once per row of this table
    ("300", "3.5"),                                                     # Minimum amount: 3.5%
    ("500", "3.5"),                                                     # Exactly 500 is still 3.5%
    ("501", "2.7"),                                                     # Just over 500: 2.7%
    ("1500", "2.7"),                                                    # Exactly 1,500 is still 2.7%
    ("1501", "2.0"),                                                    # Just over 1,500: 2.0%
    ("2500", "2.0"),                                                    # Exactly 2,500 is still 2.0%
    ("2501", "1.5"),                                                    # Just over 2,500: 1.5%
    ("5000", "1.5"),                                                    # Maximum amount: 1.5%
])                                                                      # End of the table
def test_fee_percent_at_band_edges(amount, expected):                   # pytest passes each row in as arguments
    assert fees.conversion_fee_percent(Decimal(amount)) == Decimal(expected)  # assert fails the test if the two sides differ

@pytest.mark.parametrize("amount, expected_fee", [                      # Second table: fee in US dollars at 1 GBP = 1.30 USD
    ("300", "13.65"),                                                   # 3.5% of 300 = 10.50 GBP = 13.65 USD
    ("500", "22.75"),                                                   # 3.5% of 500 = 17.50 GBP
    ("501", "17.59"),                                                   # 2.7% of 501 = 13.527 GBP = 17.5851 USD, rounds to 17.59
    ("1500", "52.65"),                                                  # 2.7% of 1,500
    ("1501", "39.03"),                                                  # 2.0% of 1,501 = 30.02 GBP = 39.026 USD, rounds to 39.03
    ("2500", "65.00"),                                                  # 2.0% of 2,500
    ("2501", "48.77"),                                                  # 1.5% of 2,501 = 37.515 GBP = 48.7695 USD, rounds to 48.77
    ("5000", "97.50"),                                                  # 1.5% of 5,000
])                                                                      # End of the table
def test_fee_in_usd_at_rate_1_30(amount, expected_fee):                 # One run per row
    result = fees.conversion_fee_usd(Decimal(amount), Decimal("1.30"))  # Calculate the fee with a fixed rate
    assert result == Decimal(expected_fee)                              # Compare with the hand-calculated value
