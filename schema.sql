PRAGMA foreign_keys = ON;                                              -- Make SQLite enforce foreign keys (it ignores them by default)

CREATE TABLE IF NOT EXISTS greeting (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS currency (                                  -- Create the table only if it does not exist yet
    currency_code TEXT PRIMARY KEY,                                    -- Three-letter code such as GBP; the primary key
    name TEXT NOT NULL,                                                -- Full name; NOT NULL means it must be filled in
    symbol TEXT NOT NULL,                                              -- Symbol such as £
    is_active INTEGER NOT NULL DEFAULT 1                               -- 1 = offered to users, 0 = hidden
);                                                                     -- End of the currency table

CREATE TABLE IF NOT EXISTS exchange_rate (                             -- One row per rate we have loaded
    rate_id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- Auto number; each new row gets the next id
    currency_code TEXT NOT NULL REFERENCES currency (currency_code),   -- Foreign key: must be a real currency
    rate_to_usd REAL NOT NULL CHECK (rate_to_usd > 0),                 -- US dollars per one unit; CHECK blocks zero or negative
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,                -- When the rate was loaded; filled in automatically
    source TEXT NOT NULL                                               -- Where the rate came from, for example sample or live
);                                                                     -- End of the exchange_rate table

CREATE TABLE IF NOT EXISTS user (                                      -- One row per customer
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- Auto number
    name TEXT NOT NULL,                                                -- Customer name
    email TEXT NOT NULL UNIQUE,                                        -- UNIQUE: two users cannot share an email
    phone TEXT,                                                        -- Optional, so no NOT NULL
    password_hash TEXT NOT NULL,                                       -- We store a hash, never the password itself
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP                 -- Filled in automatically
);                                                                     -- End of the user table

CREATE TABLE IF NOT EXISTS investment_plan (                           -- The three plans from Annexe A
    plan_id INTEGER PRIMARY KEY,                                       -- We choose the ids (1, 2, 3) ourselves
    name TEXT NOT NULL,                                                -- Plan name
    max_per_year REAL,                                                 -- NULL means unlimited
    min_monthly REAL NOT NULL,                                         -- Minimum monthly amount
    min_lump_sum REAL,                                                 -- NULL means N/A
    return_min_pct REAL NOT NULL,                                      -- Lowest predicted yearly return, in percent
    return_max_pct REAL NOT NULL,                                      -- Highest predicted yearly return, in percent
    monthly_fee_pct REAL NOT NULL                                      -- RBSX group fee per month, in percent
);                                                                     -- End of the investment_plan table

CREATE TABLE IF NOT EXISTS tax_rule (                                  -- Tax bands for each plan
    tax_rule_id INTEGER PRIMARY KEY AUTOINCREMENT,                     -- Auto number
    plan_id INTEGER NOT NULL REFERENCES investment_plan (plan_id),     -- Which plan this rule belongs to
    profit_above REAL NOT NULL,                                        -- The rule applies to profit above this amount
    tax_rate_pct REAL NOT NULL                                         -- Tax percentage on that profit
);                                                                     -- End of the tax_rule table

CREATE TABLE IF NOT EXISTS conversion_transaction (                    -- Every currency conversion we save
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,                  -- Auto number
    user_id INTEGER NOT NULL REFERENCES user (user_id),                -- Who made the conversion
    from_currency TEXT NOT NULL REFERENCES currency (currency_code),   -- Currency being sold
    to_currency TEXT NOT NULL REFERENCES currency (currency_code),     -- Currency being bought
    amount REAL NOT NULL,                                              -- Amount in the initial currency
    rate_used REAL NOT NULL,                                           -- Rate at the time of conversion
    fee_percent REAL NOT NULL,                                         -- Fee band percentage applied
    fee_usd REAL NOT NULL,                                             -- Fee converted to US dollars
    converted_amount REAL NOT NULL,                                    -- What the user receives
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP                 -- Filled in automatically
);                                                                     -- End of the conversion_transaction table

CREATE TABLE IF NOT EXISTS quote (                                     -- A savings quote (built on Tuesday)
    quote_id INTEGER PRIMARY KEY AUTOINCREMENT,                        -- Auto number
    user_id INTEGER NOT NULL REFERENCES user (user_id),                -- Who asked for the quote
    plan_id INTEGER NOT NULL REFERENCES investment_plan (plan_id),     -- The plan the user chose
    recommended_plan_id INTEGER REFERENCES investment_plan (plan_id),  -- Second link to the plan table: the best plan
    lump_sum REAL NOT NULL,                                            -- Initial lump sum
    monthly_amount REAL NOT NULL,                                      -- Monthly amount
    is_saved INTEGER NOT NULL DEFAULT 0,                               -- 1 once the user chooses Save
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP                 -- Filled in automatically
);                                                                     -- End of the quote table

CREATE TABLE IF NOT EXISTS quote_result (                              -- The results shown on a quote (built on Tuesday)
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Auto number
    quote_id INTEGER NOT NULL REFERENCES quote (quote_id),             -- Which quote this belongs to
    scenario TEXT NOT NULL,                                            -- min or max return
    years INTEGER NOT NULL,                                            -- 1, 5 or 10
    final_value REAL NOT NULL,                                         -- Value at the end of the period
    total_profit REAL NOT NULL,                                        -- Profit in the period
    total_fees REAL NOT NULL,                                          -- Fees paid in the period
    total_tax REAL NOT NULL                                            -- Tax paid in the period
);                                                                     -- End of the quote_result table

CREATE TABLE IF NOT EXISTS draft (                                     -- Unsaved form data kept when something fails
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,                        -- Auto number
    user_id INTEGER NOT NULL REFERENCES user (user_id),                -- Whose draft it is
    form_data TEXT NOT NULL,                                           -- The form values, stored as JSON text
    saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP                   -- Filled in automatically
);                                                                     -- End of the draft table

CREATE TABLE IF NOT EXISTS error_log (                                 -- Internal errors (Thursday)
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,                          -- Auto number
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,               -- Filled in automatically
    source TEXT NOT NULL,                                              -- Which part of the program failed
    message TEXT NOT NULL                                              -- What went wrong
);                                                                     -- End of the error_log table; this table stands alone, no foreign keys