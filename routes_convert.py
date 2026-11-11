from flask import Blueprint, current_app, jsonify, request              # Flask tools; a Blueprint is a group of routes kept in their own file

import currency                                                         # Rates and conversion
import database                                                         # Saving and loading data
import fees                                                             # Fee rules
import security                                                         # Who is the user
import validators                                                       # Input checks
from errors import InputError, RateUnavailableError                     # The two errors this route handles

bp = Blueprint("convert", __name__)                                     # Create the group; app.py registers it

@bp.route("/api/currencies", methods=["GET"])                           # List the currencies for the drop-downs
def currencies():                                                       # Runs for GET /api/currencies
    return jsonify(database.list_currencies(current_app.config["DB_FILE"]))  # Send the list as JSON

@bp.route("/api/convert", methods=["POST"])                             # Convert an amount and save the transaction
def convert():                                                          # Runs for POST /api/convert
    data = request.get_json(silent=True) or {}                          # Read the JSON body; if it is missing or broken use an empty dictionary
    db_file = current_app.config["DB_FILE"]                             # Which database file to use
    try:                                                                # Everything that can fail with a known error goes in here
        amount = validators.validate_amount(data.get("amount"))         # Check the amount
        from_code = validators.validate_currency(data.get("from"))      # Check the first currency
        to_code = validators.validate_currency(data.get("to"))          # Check the second currency
        if from_code == to_code:                                        # Converting a currency into itself makes no sense
            raise InputError("Choose two different currencies.")        # Tell the user
        warning = currency.refresh_rates(db_file)                       # Load fresh rates; gives a warning text if that failed, otherwise None
        rate = currency.get_rate(from_code, to_code, db_file)           # Rate for the conversion
        from_usd = currency.get_rate(from_code, "USD", db_file)         # Rate to dollars, used for the fee
        fee_percent = fees.conversion_fee_percent(amount)               # Band percentage
        fee_usd = fees.conversion_fee_usd(amount, from_usd)             # Fee in dollars
        converted = currency.convert(amount, rate)                      # The amount the user receives
    except InputError as error:                                         # The user typed something invalid
        return jsonify({"error": str(error)}), 400                      # 400 means Bad Request; send the message
    except RateUnavailableError as error:                               # No rate in the database
        return jsonify({"error": str(error)}), 503                      # 503 means Service Unavailable
    transaction_id = database.save_transaction(                         # Save the finished conversion
        security.current_user_id(),                                     # Whose transaction it is
        {                                                               # The values to store
            "from_currency": from_code,                                 # Currency sold
            "to_currency": to_code,                                     # Currency bought
            "amount": amount,                                           # Amount in the initial currency
            "rate_used": rate,                                          # Rate used
            "fee_percent": fee_percent,                                 # Band percentage
            "fee_usd": fee_usd,                                         # Fee in dollars
            "converted_amount": converted,                              # What the user receives
        },                                                              # End of the values
        db_file,                                                        # Which database
    )                                                                   # End of the call
    return jsonify({                                                    # Send the result back to the browser
        "transaction_id": transaction_id,                               # The id of the saved row
        "amount": str(amount),                                          # Text, because JSON has no Decimal type
        "from": from_code,                                              # Currency sold
        "to": to_code,                                                  # Currency bought
        "rate": str(rate),                                              # Rate used
        "fee_percent": str(fee_percent),                                # Band percentage
        "fee_usd": str(fee_usd),                                        # Fee in dollars
        "converted": str(converted),                                    # What the user receives
        "warning": warning,                                             # A warning text, or null
    }), 200                                                             # 200 means OK
