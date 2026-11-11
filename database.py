import sqlite3
from decimal import Decimal
from pathlib import Path

import config
from errors import RateUnavailableError

BASE_DIR = Path(__file__).parent

def get_connection(db_file=None):
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(db_file or config.DB_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db(db_file=None):
    """Create the tables from schema.sql and add the starting data."""
    script = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    connection = get_connection(db_file)
    connection.executescript(script)
    seed_reference_data(connection)
    connection.commit()
    connection.close()

def seed_reference_data(connection):
    """Insert currencies, sample rates, plans, tax rules and the demo user."""
    for code in config.CURRENCIES:
        name, symbol = config.CURRENCY_NAMES[code]
        connection.execute(
            "INSERT OR IGNORE INTO currency (currency_code, name, symbol) VALUES (?, ?, ?)",
            (code, name, symbol),
        )
        has_rate = connection.execute(
            "SELECT 1 FROM exchange_rate WHERE currency_code = ?", (code,)
        ).fetchone()
        if has_rate is None:
            connection.execute(
                "INSERT INTO exchange_rate (currency_code, rate_to_usd, source) VALUES (?, ?, 'sample')",
                (code, float(config.SAMPLE_RATES_TO_USD[code])),
            )
    for plan in config.PLANS:
        connection.execute(
            "INSERT OR IGNORE INTO investment_plan VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            plan,
        )
    has_rules = connection.execute("SELECT 1 FROM tax_rule").fetchone()
    if has_rules is None:
        connection.executemany(
            "INSERT INTO tax_rule (plan_id, profit_above, tax_rate_pct) VALUES (?, ?, ?)",
            config.TAX_RULES,
        )
    connection.execute(
        "INSERT OR IGNORE INTO user (user_id, name, email, password_hash) VALUES (?, 'Demo user', 'demo@efl.test', 'not-set')",
        (config.DEMO_USER_ID,),
    )

def get_rate_to_usd(currency_code, db_file=None):
    """Return the newest rate for this currency as a Decimal."""
    connection = get_connection(db_file)
    try:
        row = connection.execute(
            "SELECT rate_to_usd FROM exchange_rate WHERE currency_code = ? ORDER BY fetched_at DESC, rate_id DESC LIMIT 1",
            (currency_code,),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        raise RateUnavailableError("No exchange rate is available for " + str(currency_code) + ".")
    return Decimal(str(row["rate_to_usd"]))

def list_currencies(db_file=None):
    """Return the active currencies as a list of dictionaries."""
    connection = get_connection(db_file)
    try:
        rows = connection.execute(
            "SELECT currency_code, name, symbol FROM currency WHERE is_active = 1 ORDER BY currency_code"
        ).fetchall()
    finally:
        connection.close()
    return [{"code": r["currency_code"], "name": r["name"], "symbol": r["symbol"]} for r in rows]

def save_transaction(user_id, transaction, db_file=None):
    """Insert a conversion transaction and return its id."""
    connection = get_connection(db_file)
    try:
        cursor = connection.execute(
            "INSERT INTO conversion_transaction (user_id, from_currency, to_currency, amount, rate_used, fee_percent, fee_usd, converted_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                transaction["from_currency"],
                transaction["to_currency"],
                float(transaction["amount"]),
                float(transaction["rate_used"]),
                float(transaction["fee_percent"]),
                float(transaction["fee_usd"]),
                float(transaction["converted_amount"]),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()