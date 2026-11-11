from decimal import Decimal                                             # Decimal does exact money maths; float can drift (0.1 + 0.2 is not 0.3)

DB_FILE = "efl.db"                                                      # Name of the SQLite database file, created in the project folder
LOG_DIR = "logs"                                                        # Folder for log files (used on Thursday)
CACHE_DIR = "cache"                                                     # Folder for cached user data (used on Thursday)

MIN_TRANSACTION = Decimal("300")                                        # Annexe A: smallest amount allowed, in the initial currency
MAX_TRANSACTION = Decimal("5000")                                       # Annexe A: largest amount allowed, in the initial currency
CURRENCIES = ["GBP", "USD", "EUR", "BRL", "JPY", "TRY"]                 # Annexe A: the six currency codes the system supports

FEE_BANDS = [                                                           # Fee bands as (amount above, fee percent), highest band first
    (Decimal("2500"), Decimal("1.5")),                                  # Over 2,500 pays 1.5%
    (Decimal("1500"), Decimal("2.0")),                                  # Over 1,500 pays 2.0%
    (Decimal("500"), Decimal("2.7")),                                   # Over 500 pays 2.7%
]                                                                       # End of the list
BASE_FEE_PERCENT = Decimal("3.5")                                       # Up to and including 500 pays 3.5%

DEMO_USER_ID = 1                                                        # Until login exists (Tuesday), every transaction is saved for demo user 1

CURRENCY_NAMES = {                                                      # Display names, used to fill the currency table
    "GBP": ("Pound sterling", "£"),                                     # code: (name, symbol)
    "USD": ("US dollar", "$"),                                          # US dollar
    "EUR": ("Euro", "€"),                                               # Euro
    "BRL": ("Brazilian real", "R$"),                                    # Brazilian real
    "JPY": ("Japanese yen", "¥"),                                       # Japanese yen
    "TRY": ("Turkish lira", "₺"),                                       # Turkish lira
}                                                                       # End of the dictionary

SAMPLE_RATES_TO_USD = {                                                 # Sample rates: how many US dollars one unit is worth
    "USD": "1.00",                                                      # One dollar is one dollar
    "GBP": "1.30",                                                      # Our check values use 1 GBP = 1.30 USD
    "EUR": "1.10",                                                      # Sample rate only
    "BRL": "0.20",                                                      # Sample rate only
    "JPY": "0.0067",                                                    # Sample rate only
    "TRY": "0.030",                                                     # Sample rate only
}                                                                       # Live rates arrive later; Thursday adds the cached-rate fallback

PLANS = [                                                               # The three plans from Annexe A: (id, name, max a year, min monthly, min lump sum, min %, max %, monthly fee %)
    (1, "Basic Savings Plan", 20000, 50, None, 1.2, 2.4, 0.25),         # None means N/A (no lump-sum minimum)
    (2, "Savings Plan Plus", 30000, 50, 300, 3.0, 5.5, 0.3),            # Plan 2
    (3, "Managed Stock Investments", None, 150, 1000, 4.0, 23.0, 1.3),  # None for max a year means unlimited
]                                                                       # End of the plans list

TAX_RULES = [                                                           # Tax rules as (plan id, profit above, tax percent)
    (2, 12000, 10),                                                     # Plan 2: 10% on profits above 12,000
    (3, 12000, 10),                                                     # Plan 3: 10% on profits above 12,000
    (3, 40000, 20),                                                     # Plan 3: 20% on profits above 40,000
]                                                                       # Plan 1 has no tax rule because its tax is 0%
