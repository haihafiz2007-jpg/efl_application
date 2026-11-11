import sqlite3                                                          # To read tables directly and to catch IntegrityError
from decimal import Decimal                                             # Exact numbers

import pytest                                                           # For pytest.raises
import database                                                         # The file we are testing
import init_db as init_db_script                                        # The command-line database initializer

def count(db_file, table):                                              # Helper: how many rows are in a table?
    connection = database.get_connection(db_file)                       # Open the test database
    number = connection.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]  # COUNT(*) returns one number
    connection.close()                                                  # Release the file
    return number                                                       # Give the number back

def test_init_creates_eleven_tables(db_file):                           # The EFL schema plus the guide greeting table
    connection = database.get_connection(db_file)                       # Open the test database
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'").fetchall()  # sqlite_master lists every table
    connection.close()                                                  # Release the file
    assert len(rows) == 11                                              # Eleven tables

def test_seed_data_is_loaded(db_file):                                  # Starting data is present
    assert count(db_file, "currency") == 6                              # Six currencies
    assert count(db_file, "investment_plan") == 3                       # Three plans
    assert count(db_file, "tax_rule") == 3                              # Three tax rules

def test_init_db_script_seeds_all_exchange_rates(tmp_path):              # The script must load reference data too
    path = str(tmp_path / "script.db")                                  # Use a temporary database
    init_db_script.main(path)                                            # Run the same initializer as the command line
    connection = database.get_connection(path)                           # Open the initialized database
    rows = connection.execute(                                           # Read every currency rate
        "SELECT currency_code, rate_to_usd, source FROM exchange_rate ORDER BY currency_code"
    ).fetchall()
    connection.close()                                                  # Release the file
    assert [row["currency_code"] for row in rows] == ["BRL", "EUR", "GBP", "JPY", "TRY", "USD"]
    assert all(row["source"] == "sample" for row in rows)               # Seeded rates are marked as samples

def test_running_init_twice_adds_nothing(db_file):                      # init_db must be safe to repeat
    database.init_db(db_file)                                           # Run it a second time
    assert count(db_file, "currency") == 6                              # Still six currencies
    assert count(db_file, "exchange_rate") == 6                         # Still six rates
    assert count(db_file, "tax_rule") == 3                              # Still three tax rules

def test_list_currencies_has_six_in_code_order(db_file):                # Used by the drop-downs
    codes = [c["code"] for c in database.list_currencies(db_file)]      # Pull out just the codes
    assert codes == ["BRL", "EUR", "GBP", "JPY", "TRY", "USD"]          # Alphabetical

def test_save_transaction_stores_a_row(db_file):                        # Saving works
    transaction = {                                                     # A sample conversion
        "from_currency": "GBP",                                         # Currency sold
        "to_currency": "USD",                                           # Currency bought
        "amount": Decimal("300"),                                       # Amount
        "rate_used": Decimal("1.30"),                                   # Rate
        "fee_percent": Decimal("3.5"),                                  # Fee band
        "fee_usd": Decimal("13.65"),                                    # Fee in dollars
        "converted_amount": Decimal("390.00"),                          # Result
    }                                                                   # End of the sample
    new_id = database.save_transaction(1, transaction, db_file)         # Save it for user 1
    assert new_id == 1                                                  # The first row gets id 1
    assert count(db_file, "conversion_transaction") == 1                # One row stored

def test_foreign_key_blocks_unknown_user(db_file):                      # Foreign keys are enforced
    transaction = {"from_currency": "GBP", "to_currency": "USD", "amount": 300, "rate_used": 1.3, "fee_percent": 3.5, "fee_usd": 13.65, "converted_amount": 390}  # Same sample, shorter
    with pytest.raises(sqlite3.IntegrityError):                         # The database must refuse
        database.save_transaction(999, transaction, db_file)            # There is no user 999
