"""The HTML pages."""                         # Docstring: what this file does
from flask import Blueprint, render_template  # Flask tools: a route group and the page filler

bp = Blueprint("pages", __name__)             # Create the group; app.py registers it

@bp.route("/")                                # The home page
def index():                                  # Runs when the browser asks for /
    return render_template("index.html")      # Fill in templates/index.html and send it

@bp.route("/login")                           # Login page (built on Thursday)
def login_page():                             # Runs for /login
    return render_template("login.html")      # Send the page

@bp.route("/converter")                       # The converter page
def converter_page():                         # Runs for /converter
    return render_template("converter.html")  # Send the page

@bp.route("/quote-page")                      # Quote page (Tuesday)
def quote_page():                             # Runs for /quote-page
    return render_template("quote.html")      # Send the page

@bp.route("/history-page")                    # History page (Thursday)
def history_page():                           # Runs for /history-page
    return render_template("history.html")    # Send the page