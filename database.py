import sqlite3                                                          # Python's built-in SQLite library; nothing to install
from decimal import Decimal                                             # For exact rates
from pathlib import Path                                                # Lets us find schema.sql whatever folder we run from

import config                                                           # Our settings file
from errors import RateUnavailableError                                 # The error to raise when no rate exists

BASE_DIR = Path(__file__).parent                                        # The folder this file lives in

def get_connection(db_file=None):                                       # Open the database; db_file lets tests use a different file
    """Open a connection to the SQLite database."""                     # Docstring
    connection = sqlite3.connect(db_file or config.DB_FILE)             # Use the given file, or the default from config
    connection.row_factory = sqlite3.Row                                # Lets us read a column by name, row["amount"]
    connection.execute("PRAGMA foreign_keys = ON")                      # Turn on foreign keys for this connection
    return connection                                                   # Give the open connection to the caller

def init_db(db_file=None):                                              # Create every table and fill the reference data
    """Create the tables from schema.sql and add the starting data."""  # Docstring
    script = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")      # Read the whole SQL file as text
    connection = get_connection(db_file)                                # Open the database
    connection.executescript(script)                                    # Run every statement in the file
    seed_reference_data(connection)                                     # Add currencies, rates, plans, tax rules and the demo user
    connection.commit()                                                 # Save the changes permanently
    connection.close()                                                  # Release the file

def seed_reference_data(connection):                                    # Add starting rows; safe to run twice
    """Insert currencies, sample rates, plans, tax rules and the demo user."""  # Docstring
    connection.execute(
        "INSERT INTO greeting (message) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM greeting)",
        ("Hello from the database!",),
    )
    for code in config.CURRENCIES:                                      # Go through the six codes
        name, symbol = config.CURRENCY_NAMES[code]                      # Look up the name and symbol
        connection.execute(                                             # Start an INSERT statement
            "INSERT OR IGNORE INTO currency (currency_code, name, symbol) VALUES (?, ?, ?)",  # OR IGNORE skips it if the row exists; ? are placeholders
            (code, name, symbol),                                       # The values that replace the three ? marks
        )                                                               # End of the INSERT
        has_rate = connection.execute(                                  # Ask: do we already have a rate for this currency?
            "SELECT 1 FROM exchange_rate WHERE currency_code = ?", (code,)  # (code,) is a one-item tuple
        ).fetchone()                                                    # fetchone gives one row, or None if there is none
        if has_rate is None:                                            # Only add a rate when there is none, so running twice adds nothing
            connection.execute(                                         # Start an INSERT statement
                "INSERT INTO exchange_rate (currency_code, rate_to_usd, source) VALUES (?, ?, 'sample')",  # The source is the fixed word sample
                (code, float(config.SAMPLE_RATES_TO_USD[code])),        # Turn the text rate into a number for SQLite
            )                                                           # End of the INSERT
    for plan in config.PLANS:                                           # Go through the three plans
        connection.execute(                                             # Start an INSERT statement
            "INSERT OR IGNORE INTO investment_plan VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  # Eight values, in the same order as the table columns
            plan,                                                       # The whole tuple fills the eight ? marks
        )                                                               # End of the INSERT
    has_rules = connection.execute("SELECT 1 FROM tax_rule").fetchone()  # Are there tax rules already?
    if has_rules is None:                                               # Only add them once
        connection.executemany(                                         # Run the same INSERT for many rows
            "INSERT INTO tax_rule (plan_id, profit_above, tax_rate_pct) VALUES (?, ?, ?)",  # One tax rule
            config.TAX_RULES,                                           # The list of rules
        )                                                               # End of the INSERT
    connection.execute(                                                 # Add the demo user that owns every transaction until login exists
        "INSERT OR IGNORE INTO user (user_id, name, email, password_hash) VALUES (?, 'Demo user', 'demo@efl.test', 'not-set')",  # Fixed id, so it is added once
        (config.DEMO_USER_ID,),                                         # The id from config
    )                                                                   # End of the INSERT

def get_greeting(db_file=None):
    """Return the greeting message stored in the database."""
    connection = get_connection(db_file)
    try:
        row = connection.execute(
            "SELECT message FROM greeting ORDER BY id LIMIT 1"
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        raise ValueError("No greeting is available in the database.")
    return row["message"]

def list_conversion_transactions(db_file=None):
    """Return recent conversions for the history page."""
    connection = get_connection(db_file)
    try:
        rows = connection.execute(
            "SELECT created_at, from_currency, to_currency, amount, fee_usd, converted_amount "
            "FROM conversion_transaction ORDER BY created_at DESC, transaction_id DESC"
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]

def get_rate_to_usd(currency_code, db_file=None):                       # Latest rate for one currency, as US dollars per unit
    """Return the newest rate for this currency as a Decimal."""        # Docstring
    connection = get_connection(db_file)                                # Open the database
    try:                                                                # try/finally makes sure we always close the connection
        row = connection.execute(                                       # Start a SELECT statement
            "SELECT rate_to_usd FROM exchange_rate WHERE currency_code = ? ORDER BY fetched_at DESC, rate_id DESC LIMIT 1",  # Newest first, take one row
            (currency_code,),                                           # The currency to look up
        ).fetchone()                                                    # One row, or None
    finally:                                                            # Runs whether or not an error happened
        connection.close()                                              # Release the file
    if row is None:                                                     # No rate stored for this currency
        raise RateUnavailableError("No exchange rate is available for " + str(currency_code) + ".")  # Stop with a clear error; the route turns it into a message
    return Decimal(str(row["rate_to_usd"]))                             # str() first, so Decimal gets 1.3 and not 1.3000000000000000444

def list_currencies(db_file=None):                                      # The currencies to show in the drop-down lists
    """Return the active currencies as a list of dictionaries."""       # Docstring
    connection = get_connection(db_file)                                # Open the database
    try:                                                                # Always close the connection
        rows = connection.execute(                                      # Start a SELECT statement
            "SELECT currency_code, name, symbol FROM currency WHERE is_active = 1 ORDER BY currency_code"  # Only active currencies, in code order
        ).fetchall()                                                    # fetchall gives every row
    finally:                                                            # Runs whether or not an error happened
        connection.close()                                              # Release the file
    return [{"code": r["currency_code"], "name": r["name"], "symbol": r["symbol"]} for r in rows]  # Turn each row into a plain dictionary Flask can send as JSON

def save_transaction(user_id, transaction, db_file=None):               # Store one finished conversion and return its id
    """Insert a conversion transaction and return its id."""            # Docstring
    connection = get_connection(db_file)                                # Open the database
    try:                                                                # Always close the connection
        cursor = connection.execute(                                    # Start an INSERT statement
            "INSERT INTO conversion_transaction (user_id, from_currency, to_currency, amount, rate_used, fee_percent, fee_usd, converted_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  # Eight columns, eight ? marks
            (                                                           # The eight values, in the same order
                user_id,                                                # Who converted
                transaction["from_currency"],                           # Currency sold
                transaction["to_currency"],                             # Currency bought
                float(transaction["amount"]),                           # SQLite stores REAL, so Decimal becomes float
                float(transaction["rate_used"]),                        # The rate we used
                float(transaction["fee_percent"]),                      # Band percentage
                float(transaction["fee_usd"]),                          # Fee in US dollars
                float(transaction["converted_amount"]),                 # What the user receives
            ),                                                          # End of the values
        )                                                               # End of the INSERT
        connection.commit()                                             # Save permanently
        return cursor.lastrowid                                         # The auto number SQLite gave the new row
    finally:                                                            # Runs even after the return above
        connection.close()                                              # Release the file