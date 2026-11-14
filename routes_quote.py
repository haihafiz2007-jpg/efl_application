"""Savings quote and saved-quote endpoints."""
from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

import database
import quotes
import security
from errors import InputError

bp = Blueprint("quote", __name__)


def _remember_failed_quote(user_id, data, db_file):
    try:
        database.save_quote_draft(user_id, data, db_file)
    except Exception:
        current_app.logger.exception("Could not cache a failed quote submission.")


@bp.route("/api/quotes", methods=["POST"])
@security.login_required
def create_quote():
    data = request.get_json(silent=True) or {}
    db_file = current_app.config["DB_FILE"]
    user_id = security.current_user_id()
    try:
        result = quotes.calculate_quote(
            data.get("plan_id"),
            data.get("lump_sum"),
            data.get("monthly_amount"),
            db_file,
        )
    except InputError as error:
        _remember_failed_quote(user_id, data, db_file)
        return jsonify({"error": str(error)}), 400

    is_saved = data.get("save") is True
    quote_id = database.save_quote(
        user_id,
        {
            "plan_id": result["plan_id"],
            "recommended_plan_id": result["recommended_plan_id"],
            "lump_sum": Decimal(str(data["lump_sum"])),
            "monthly_amount": Decimal(str(data["monthly_amount"])),
            "is_saved": is_saved,
        },
        result["projections"],
        db_file,
    )
    plans, _ = database.get_plans_and_tax_rules(db_file)
    plan_names = {plan["plan_id"]: plan["name"] for plan in plans}
    response = {
        "quote_id": quote_id,
        "plan_id": result["plan_id"],
        "plan_name": plan_names[result["plan_id"]],
        "recommended_plan_id": result["recommended_plan_id"],
        "recommended_plan_name": plan_names[result["recommended_plan_id"]],
        "is_saved": is_saved,
        "projections": {
            scenario: {
                str(year): {key: str(value) for key, value in values.items()}
                for year, values in periods.items()
            }
            for scenario, periods in result["projections"].items()
        },
    }
    return jsonify(response), 201


@bp.route("/api/quotes/<int:quote_id>/save", methods=["POST"])
@security.login_required
def save_quote(quote_id):
    if not database.save_quote_if_saved(
        quote_id, security.current_user_id(), current_app.config["DB_FILE"]
    ):
        return jsonify({"error": "Saved quote not found."}), 404
    return jsonify({"quote_id": quote_id, "is_saved": True})
