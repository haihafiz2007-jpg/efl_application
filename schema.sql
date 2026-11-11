PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS currency (
    currency_code TEXT PRIMARY KEY,
    name          TEXT    NOT NULL,
    symbol        TEXT    NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS exchange_rate (
    rate_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_code TEXT    NOT NULL REFERENCES currency (currency_code),
    rate_to_usd   REAL    NOT NULL CHECK (rate_to_usd > 0),
    fetched_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source        TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    phone         TEXT,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS investment_plan (
    plan_id         INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    max_per_year    REAL,
    min_monthly     REAL    NOT NULL,
    min_lump_sum    REAL,
    return_min_pct  REAL    NOT NULL,
    return_max_pct  REAL    NOT NULL,
    monthly_fee_pct REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS tax_rule (
    tax_rule_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id      INTEGER NOT NULL REFERENCES investment_plan (plan_id),
    profit_above REAL    NOT NULL,
    tax_rate_pct REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS conversion_transaction (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES user (user_id),
    from_currency   TEXT    NOT NULL REFERENCES currency (currency_code),
    to_currency     TEXT    NOT NULL REFERENCES currency (currency_code),
    amount          REAL    NOT NULL,
    rate_used       REAL    NOT NULL,
    fee_percent     REAL    NOT NULL,
    fee_usd         REAL    NOT NULL,
    converted_amount REAL   NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quote (
    quote_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES user (user_id),
    plan_id             INTEGER NOT NULL REFERENCES investment_plan (plan_id),
    recommended_plan_id INTEGER REFERENCES investment_plan (plan_id),
    lump_sum            REAL    NOT NULL,
    monthly_amount      REAL    NOT NULL,
    is_saved            INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quote_result (
    result_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id     INTEGER NOT NULL REFERENCES quote (quote_id),
    scenario     TEXT    NOT NULL,
    years        INTEGER NOT NULL,
    final_value  REAL    NOT NULL,
    total_profit REAL    NOT NULL,
    total_fees   REAL    NOT NULL,
    total_tax    REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS draft (
    draft_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES user (user_id),
    form_data TEXT    NOT NULL,
    saved_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS error_log (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TEXT   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source     TEXT    NOT NULL,
    message    TEXT    NOT NULL
);
