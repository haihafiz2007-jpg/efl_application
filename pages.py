"""The HTML pages."""
from flask import Blueprint, current_app, redirect, render_template, url_for

import database
import config
import security

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    return redirect(url_for("pages.login_page"))

@bp.route("/hello")
def hello_page():
    message = database.get_greeting(current_app.config["DB_FILE"])
    return render_template("index.html", message=message)

@bp.route("/login")
def login_page():
    return render_template("index.html", page="login")

@bp.route("/converter")
@security.login_required
def converter_page():
    return render_template("converter.html", page="converter")

@bp.route("/quote-page")
@security.login_required
def quote_page():
    return render_template("index.html", page="quote", plans=config.PLANS)

@bp.route("/history-page")
@security.login_required
def history_page():
    db_file = current_app.config["DB_FILE"]
    user_id = security.current_user_id()
    transactions = database.list_user_conversion_transactions(user_id, db_file)
    quotes = database.list_saved_quotes(user_id, db_file)
    return render_template(
        "index.html", page="history", transactions=transactions, quotes=quotes
    )

@bp.route("/account-page")
@security.login_required
def account_page():
    user = database.get_user(security.current_user_id(), current_app.config["DB_FILE"])
    return render_template("index.html", page="account", user=user)
