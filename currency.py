from decimal import Decimal, ROUND_HALF_UP

import config
import database


def round_money(value):
    """Round a Decimal to 2 decimal places using the standard half-up rule."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def refresh_rates(db_file=None):
    """Ensure sample exchange rates exist for each supported currency."""
    connection = database.get_connection(db_file)
    try:
        for code in config.CURRENCIES:
            row = connection.execute(
                "SELECT 1 FROM exchange_rate WHERE currency_code = ? LIMIT 1",
                (code,),
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO exchange_rate (currency_code, rate_to_usd, source) VALUES (?, ?, 'sample')",
                    (code, float(config.SAMPLE_RATES_TO_USD[code])),
                )
        connection.commit()
    finally:
        connection.close()
    return None


def get_rate(from_code, to_code, db_file=None):
    """Return the conversion rate between two currencies."""
    from_usd = database.get_rate_to_usd(from_code, db_file)
    to_usd = database.get_rate_to_usd(to_code, db_file)
    if from_usd == to_usd:
        return Decimal("1")
    return from_usd / to_usd


def convert(amount, rate):
    """Convert an amount using the supplied rate and round to 2 decimals."""
    return round_money(Decimal(str(amount)) * Decimal(str(rate)))
