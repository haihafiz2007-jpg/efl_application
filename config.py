from decimal import Decimal

DB_FILE = "efl.db"
LOG_DIR = "logs"
CACHE_DIR = "cache"

MIN_TRANSACTION = Decimal("300")
MAX_TRANSACTION = Decimal("5000")
CURRENCIES = ["GBP", "USD", "EUR", "BRL", "JPY", "TRY"]

FEE_BANDS = [
    (Decimal("2500"), Decimal("1.5")),
    (Decimal("1500"), Decimal("2.0")),
    (Decimal("500"), Decimal("2.7")),
]
BASE_FEE_PERCENT = Decimal("3.5")

DEMO_USER_ID = 1

CURRENCY_NAMES = {
    "GBP": ("Pound sterling", "£"),
    "USD": ("US dollar", "$"),
    "EUR": ("Euro", "€"),
    "BRL": ("Brazilian real", "R$"),
    "JPY": ("Japanese yen", "¥"),
    "TRY": ("Turkish lira", "₺"),
}

SAMPLE_RATES_TO_USD = {
    "USD": "1.00",
    "GBP": "1.30",
    "EUR": "1.10",
    "BRL": "0.20",
    "JPY": "0.0067",
    "TRY": "0.030",
}

PLANS = [
    (1, "Basic Savings Plan", 20000, 50, None, 1.2, 2.4, 0.25),
    (2, "Savings Plan Plus", 30000, 50, 300, 3.0, 5.5, 0.3),
    (3, "Managed Stock Investments", None, 150, 1000, 4.0, 23.0, 1.3),
]

TAX_RULES = [
    (2, 12000, 10),
    (3, 12000, 10),
    (3, 40000, 20),
]
