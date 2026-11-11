"""The HTML pages."""                         # Docstring: what this file does
from flask import Blueprint, current_app, redirect, render_template, url_for  # Flask tools: a route group and the page filler

import database
import config

bp = Blueprint("pages", __name__)             # Create the group; app.py registers it

@bp.route("/")
def index():
    return redirect(url_for("pages.login_page"))

@bp.route("/hello")
def hello_page():
    message = database.get_greeting(current_app.config["DB_FILE"])
    return render_template("index.html", message=message)

@bp.route("/login")                           # Login page (built on Thursday)
def login_page():                             # Runs for /login
    return render_template("index.html", page="login")

@bp.route("/converter")                       # The converter page
def converter_page():                         # Runs for /converter
    return render_template("converter.html", page="converter")

@bp.route("/quote-page")                      # Quote page (Tuesday)
def quote_page():                             # Runs for /quote-page
    return render_template("index.html", page="quote", plans=config.PLANS)

@bp.route("/history-page")                    # History page (Thursday)
def history_page():                           # Runs for /history-page
    transactions = database.list_conversion_transactions(current_app.config["DB_FILE"])
    return render_template("index.html", page="history", transactions=transactions)