import sqlite3
import json
import secrets
from decimal import Decimal
from pathlib import Path

import config
from errors import RateUnavailableError
from werkzeug.security import generate_password_hash

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
    connection.execute(
        "INSERT INTO greeting (message) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM greeting)",
        ("Hello from the database!",),
    )
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
    seeded_user = connection.execute(
        "SELECT password_hash FROM user WHERE user_id = ?", (config.DEMO_USER_ID,)
    ).fetchone()
    if seeded_user is None:
        connection.execute(
            "INSERT INTO user (user_id, name, email, password_hash) "
            "VALUES (?, 'Demo user', 'demo@efl.test', ?)",
            (config.DEMO_USER_ID, generate_password_hash(secrets.token_urlsafe(32))),
        )
    elif seeded_user["password_hash"] == "not-set":
        connection.execute(
            "UPDATE user SET password_hash = ? WHERE user_id = ?",
            (generate_password_hash(secrets.token_urlsafe(32)), config.DEMO_USER_ID),
        )

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
            "FROM conversion_transaction WHERE user_id = ? ORDER BY created_at DESC, transaction_id DESC",
            (config.DEMO_USER_ID,),
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]

def list_user_conversion_transactions(user_id, db_file=None):
    """Return recent conversions belonging to one user."""
    connection = get_connection(db_file)
    try:
        rows = connection.execute(
            "SELECT created_at, from_currency, to_currency, amount, fee_usd, converted_amount "
            "FROM conversion_transaction WHERE user_id = ? "
            "ORDER BY created_at DESC, transaction_id DESC",
            (user_id,),
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]

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

def get_plans_and_tax_rules(db_file=None):
    """Return investment plans and ordered tax bands."""
    connection = get_connection(db_file)
    try:
        plans = connection.execute(
            "SELECT plan_id, name, max_per_year, min_monthly, min_lump_sum, "
            "return_min_pct, return_max_pct, monthly_fee_pct "
            "FROM investment_plan ORDER BY plan_id"
        ).fetchall()
        rules = connection.execute(
            "SELECT plan_id, profit_above, tax_rate_pct FROM tax_rule "
            "ORDER BY plan_id, profit_above"
        ).fetchall()
    finally:
        connection.close()
    tax_rules = {}
    for row in rules:
        tax_rules.setdefault(row["plan_id"], []).append(
            (row["profit_above"], row["tax_rate_pct"])
        )
    return [dict(row) for row in plans], tax_rules

def save_quote(user_id, quote, results, db_file=None):
    """Save a quote and its projections in one transaction."""
    connection = get_connection(db_file)
    try:
        cursor = connection.execute(
            "INSERT INTO quote (user_id, plan_id, recommended_plan_id, lump_sum, monthly_amount, is_saved) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                user_id,
                quote["plan_id"],
                quote["recommended_plan_id"],
                float(quote["lump_sum"]),
                float(quote["monthly_amount"]),
                int(quote.get("is_saved", False)),
            ),
        )
        quote_id = cursor.lastrowid
        connection.executemany(
            "INSERT INTO quote_result (quote_id, scenario, years, final_value, total_profit, total_fees, total_tax) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    quote_id,
                    scenario,
                    years,
                    float(result["final_value"]),
                    float(result["total_profit"]),
                    float(result["total_fees"]),
                    float(result["total_tax"]),
                )
                for scenario, period_results in results.items()
                for years, result in period_results.items()
            ],
        )
        connection.commit()
        return quote_id
    finally:
        connection.close()

def save_quote_draft(user_id, form_data, db_file=None):
    """Cache submitted form data for a user after a failed request."""
    connection = get_connection(db_file)
    try:
        connection.execute(
            "INSERT INTO draft (user_id, form_data) VALUES (?, ?)",
            (user_id, json.dumps(form_data, separators=(",", ":"), default=str)),
        )
        connection.commit()
    finally:
        connection.close()

def save_quote_if_saved(quote_id, user_id, db_file=None):
    """Mark one of the user's quotes as saved."""
    connection = get_connection(db_file)
    try:
        cursor = connection.execute(
            "UPDATE quote SET is_saved = 1 WHERE quote_id = ? AND user_id = ?",
            (quote_id, user_id),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()

def list_saved_quotes(user_id, db_file=None):
    """Return the user's saved quotes with their projection results."""
    connection = get_connection(db_file)
    try:
        rows = connection.execute(
            "SELECT q.quote_id, q.created_at, q.plan_id, p.name AS plan_name, "
            "q.recommended_plan_id, rp.name AS recommended_plan_name, q.lump_sum, q.monthly_amount, "
            "r.scenario, r.years, r.final_value, r.total_profit, r.total_fees, r.total_tax "
            "FROM quote q JOIN investment_plan p ON p.plan_id = q.plan_id "
            "LEFT JOIN investment_plan rp ON rp.plan_id = q.recommended_plan_id "
            "JOIN quote_result r ON r.quote_id = q.quote_id "
            "WHERE q.user_id = ? AND q.is_saved = 1 "
            "ORDER BY q.created_at DESC, q.quote_id DESC, r.years, r.scenario",
            (user_id,),
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]

def get_user_by_email(email, db_file=None):
    """Look up a user by normalized email address."""
    connection = get_connection(db_file)
    try:
        row = connection.execute(
            "SELECT user_id, name, email, phone, password_hash FROM user WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None

def get_user(user_id, db_file=None):
    """Return contact details for one user."""
    connection = get_connection(db_file)
    try:
        row = connection.execute(
            "SELECT user_id, name, email, phone FROM user WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None

def create_user(name, email, phone, password_hash, db_file=None):
    """Create an account and return its user id."""
    connection = get_connection(db_file)
    try:
        cursor = connection.execute(
            "INSERT INTO user (name, email, phone, password_hash) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), phone.strip() or None, password_hash),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def update_user_contacts(user_id, name, phone, db_file=None):
    """Update the signed-in user's name and phone number."""
    connection = get_connection(db_file)
    try:
        cursor = connection.execute(
            "UPDATE user SET name = ?, phone = ? WHERE user_id = ?",
            (name.strip(), phone.strip() or None, user_id),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()

def log_error(source, message, db_file=None):
    """Record an application error in the database."""
    connection = get_connection(db_file)
    try:
        connection.execute(
            "INSERT INTO error_log (source, message) VALUES (?, ?)",
            (str(source)[:255], str(message)[:2000]),
        )
        connection.commit()
    finally:
        connection.close()
